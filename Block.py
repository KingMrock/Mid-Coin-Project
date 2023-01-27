import json
import threading
import time
from typing import Dict, Tuple, List

from Curve import EllipticCurve
from Blockchain_Tools import *
from Hash import *
from Signature import verify, sign
import pickle

class Block (object):
    def __init__(self, previous_hash: str, transactions: List[Tuple[Transaction, Tuple[int, int]]], messages: List[Tuple[str, Tuple[int, int]]] = None):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.messages = messages
        self.data = str(previous_hash) + str(transactions)
        self.hash = str(Hash(self.data))
        self.miner = None
        self.reward = 0

    def calculate_hash(self):
        return str(Hash(self.data))

    def __str__(self):
        transactions = ""
        if not self.messages:
            messages = "\n"
        else:
            messages = "\nMessages in this block:\n"
        for transaction in self.transactions:
            transactions += (str(transaction[0]) + " Signature: " + str(transaction[1]) + "\n")
        for message in self.messages:
            messages += message[0] + " Signature: " + str(message[1]) + "\n"
        return "Block Hash:" + str(self.hash) + \
               "\nPrevious Hash: " + str(self.previous_hash) + \
               "\nTransaction in this block:\n" + transactions + messages + \
               "Mined by: " + str(self.miner) + " Reward: " + str(self.reward)



    def __eq__(self, other):
        return self.hash == other.hash

    def __getstate__(self):
        return {'previous_hash': self.previous_hash, 'transactions': self.transactions, 'data': self.data,
                'hash': self.hash, 'miner': self.miner, 'reward': self.reward, 'messages': self.messages}

    def __setstate__(self, state):
        self.__init__(state['previous_hash'], state['transactions'])
        self.data = state['data']
        self.hash = state['hash']
        self.miner = state['miner']
        self.reward = state['reward']
        self.messages = state['messages']


def calculate_cost(message):
    """
    Calculates the cost of a message
    """
    return (len(message) // 60) * 0.1 + 0.1


class BlockChain (object):
    def __init__(self, curve: EllipticCurve):
        self.curve = curve
        self.blocks = []
        self.users = []
        self.pending_transactions = []
        self.pending_messages = []
        self.stake = Staking()
        god = User("God", curve.get_generator() * 1)
        god.balance = 500
        bonus = User("bonus", curve.get_generator() * 2)
        bonus.balance = 0
        self.users.append(god)
        self.users.append(bonus)
        """
        Can't use thread on server deployment
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=self.start_timer)
            self.thread.start()
        """

    def add_user(self, user: User):
        self.users.append(user)
        self.stake.add_user(user)
        if self.get_user_by_name("God").balance >= 5:
            self.make_transaction(self.get_user_by_name("God").pubkey, 1, user.pubkey, 5)
            self.mine()
        elif self.get_user_by_name("God").balance < 0:
            self.save_to_file('blockchain.txt')
        elif self.get_user_by_name("God").balance < 5:
            self.make_transaction(self.get_user_by_name("God").pubkey, 1, user.pubkey, self.get_user_by_name("God").balance)
            self.mine()

    def get_user(self, public_key):
        for user in self.users:
            if user.pubkey == public_key:
                return user
        return None

    def get_user_by_name(self, name):
        for user in self.users:
            if user.name == name:
                return user
        return None

    @classmethod
    def check_validity(cls, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block.previous_hash != previous_block.hash or chain.verify_transactions(block.transactions):
                return False
            previous_block = block
            block_index += 1
        return True


    def mine(self):
        total_staking_power = sum(user.staking_power for user in self.users)
        lucky_number = random.uniform(0, total_staking_power)
        cumulative_staking_power = 0
        miner = None
        for user in self.users:
            cumulative_staking_power += user.staking_power
            if cumulative_staking_power >= lucky_number:
                miner = user
                break
        if len(self.blocks) == 0:
            previous_hash = "BLOCKCHAIN_START"
        else:
            previous_hash = self.blocks[-1].hash

        for transaction in self.pending_transactions:
            if not self.verify_signed_transaction(transaction):
                self.pending_transactions.remove(transaction)
                transaction[0].status = "Denied"
            else:
                # Round the amount to 5 decimals
                transaction[0].amount = round(transaction[0].amount, 5)
                transaction[0].sender.balance -= transaction[0].amount
                transaction[0].receiver.balance += transaction[0].amount
                transaction[0].status = "Complete"


        new_block = Block(previous_hash, self.pending_transactions, self.pending_messages)
        new_block.miner = miner

        if miner is not self.get_user_by_name("God"):
            new_block.reward = 2 + self.get_user_by_name("bonus").balance
            miner.balance += (2 + self.get_user_by_name("bonus").balance)
            self.get_user_by_name("bonus").balance = 0
        else:
            new_block.reward = 0
        self.blocks.append(new_block)
        self.pending_transactions = []
        self.pending_messages = []
        #Save the blockchain
        self.save_to_file('blockchain.txt')
        return new_block

    def add_transaction(self, transaction_signed):
        self.pending_transactions.append(transaction_signed)
        if len(self.pending_transactions) > 10:
            self.mine()

    def start_timer(self):
        """
        This function is used to mine a block every 3 seconds
        """
        while self.stop_event.is_set():
            time.sleep(3)
            if len(self.pending_transactions) > 0:
                # mine the transactions
                self.mine()

    def make_transaction(self, sender, privkey, receiver, amount):
        """
        Creates a transaction and signs it with the private key of the sender.
        Sender and receiver are the PUBLIC KEYS of the users
        """
        by = self.get_user(sender)
        to = self.get_user(receiver)
        if by is None or to is None:
            raise Exception("User not found")
        transaction = Transaction(by, to, amount)
        if not Transaction.is_valid(transaction):
            raise Exception("Transaction is not valid")
        signature = sign(self.curve, privkey, str(transaction))
        self.add_transaction((transaction, signature))
        return transaction

    def __str__(self):
        return str(self.blocks)

    def print_chain(self):
        """
        Prints the blockchain in a readable format block by block
        """
        print("Blockchain: ", self.chain_to_string())


    def chain_to_string(self):
        """
        Returns the blockchain as a string
        """
        chain = ""
        for block in self.blocks:
            chain += str(block) + "\n\n"
        return chain

    def verify_signed_transactions(self, signed_transactions):
        """
        Verifies a list of signed transactions
        """
        for signed_transaction in signed_transactions:
            if self.verify_signed_transaction(signed_transaction) is False:
                return False
        return True

    def verify_signed_transaction(self, signed_transaction):
        """
        Verifies a signed transaction by checking if the signature is valid and if the sender has enough balance
        """
        if not Transaction.is_valid(signed_transaction[0]):
            return False
        if not verify(self.curve, signed_transaction[0].sender.pubkey, str(signed_transaction[0]), signed_transaction[1]):
            return False
        return True

    def save_to_file(self, file_path):
        """
        Save the blockchain to a file in pickle format (binary) more efficient
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_file(cls, file_path):
        """
        Load the blockchain from a file using pyckle
        """
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def get_last_x_transaction(self, user, number):
        """
        Get the last x transactions of a user
        """
        transactions = []
        for block in reversed(self.blocks):
            for transaction in reversed(block.transactions):
                if transaction[0].sender == user or transaction[0].receiver == user:
                    transactions.append(transaction)
                    if len(transactions) == number:
                        return transactions
        return transactions

    def get_last_x_transaction_sender(self, user, number):
        """
        Get the last x transactions of a user
        """
        transactions = []
        for block in reversed(self.blocks):
            for transaction in reversed(block.transactions):
                if transaction[0].sender == user:
                    transactions.append(transaction)
                    if len(transactions) == number:
                        return transactions
        return transactions

    def get_last_x_transaction_receiver(self, user, number):
        """
        Get the last x transactions received by a user
        """
        transactions = []
        for block in reversed(self.blocks):
            for transaction in reversed(block.transactions):
                if transaction[0].receiver == user:
                    transactions.append(transaction)
                    if len(transactions) == number:
                        return transactions
        return transactions

    @classmethod
    def load_from_text(cls, file_path):
        """
        Load the blockchain from a file reading and adding users and blocks
        """
        blockchain = BlockChain()
        with open(file_path, 'r') as file:
            current_block = None
            for line in file:
                if line.startswith("Block Hash:"):
                    current_block = Block()
                    current_block.hash = line.strip().split(":")[1]
                    blockchain.blocks.append(current_block)
                elif line.startswith("Previous Hash:"):
                    current_block.previous_hash = line.strip().split(":")[1]
                elif line.startswith("Transaction in this block:"):
                    pass
                elif line.startswith("Mined by:"):
                    miner = line.strip().split(":")[1]
                else:
                    transaction = line.strip().split(":")
                    sender = blockchain.get_user_by_name(transaction[0])
                    receiver = blockchain.get_user_by_name(transaction[1])
                    amount = float(transaction[2])
                    blockchain.add_transaction(Transaction(sender, receiver, amount))
        return blockchain

    def stop_timer(self):
        """
        Stops the timer thread
        """
        self.stop_event.clear()
        self.thread.join()

    def add_message(self, sender, privkey, message, fast=False):
        """
        Adds a message to the blockchain
        """
        by = self.get_user(sender)
        if by is None:
            raise Exception("User not found")
        cost = calculate_cost(message)
        if fast:
            cost *= 1.05
        message = str(by) + " :" + message
        print(message)
        try:
            self.make_transaction(sender, privkey, self.get_user_by_name("bonus").pubkey, cost)
        except:
            raise Exception("Not enough balance")
        signature_message = sign(self.curve, privkey, message)
        print(verify(self.curve, by.pubkey, message, signature_message))
        self.pending_messages.append((message, signature_message))
        return message, signature_message

    def print_users(self):
        """
        Prints the users in the blockchain
        """
        for user in self.users:
            print(str(user) + " " + str(user.balance))


    def __getstate__(self):
        """
        Used to pickle the blockchain
        """
        state = self.__dict__.copy()
        """
        del state['thread']
        del state['stop_event']
        """
        return state

    def __setstate__(self, state):
        """
        Used to unpickle the blockchain
        """
        self.__dict__.update(state)
        """
        self.thread = threading.Thread(target=self.start_timer)
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.thread.start()
        """

