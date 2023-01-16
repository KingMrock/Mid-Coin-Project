import json
import threading
import time
from typing import Dict, Tuple, List

from Curve import EllipticCurve
from User import *
from Hash import *
from Signature import verify, sign
import pickle


"""
Transactions are stored in a list of tuples (sender, receiver, amount)
"""
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        if not Transaction.is_valid(self):
            raise ValueError("Invalid transaction.")

    def __str__(self):
        return str(self.sender) + " -> " + str(self.receiver) + " : " + str(self.amount) + " MidlCoin"

    def __eq__(self, other):
        return self.sender == other.sender and self.receiver == other.receiver and self.amount == other.amount

    @classmethod
    def is_valid(cls, transaction):
        return transaction.sender.balance >= transaction.amount

    def __getstate__(self):
        return {'sender': self.sender, 'receiver': self.receiver, 'amount': self.amount }

    def __setstate__(self, state):
        self.__init__(state['sender'], state['receiver'], state['amount'])


class Block (object):
    def __init__(self, previous_hash: str, transactions: List[Tuple[Transaction, Tuple[int, int]]]):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.data = str(previous_hash) + str(transactions)
        self.hash = str(Hash(self.data))
        self.miner = None

    def calculate_hash(self):
        return str(Hash(self.data))

    def __str__(self):
        transactions = ""
        for transaction in self.transactions:
            transactions += (str(transaction[0]) + "\n")
        return "Block Hash:" + str(self.hash) + \
               "\nPrevious Hash: " + str(self.previous_hash) + \
               "\nTransaction in this block:\n" + transactions + \
               "Mined by: " + str(self.miner)

    def __eq__(self, other):
        return self.hash == other.hash

    def __getstate__(self):
        return {'previous_hash': self.previous_hash, 'transactions': self.transactions, 'data': self.data, 'hash': self.hash, 'miner': self.miner }

    def __setstate__(self, state):
        self.__init__(state['previous_hash'], state['transactions'])
        self.data = state['data']
        self.hash = state['hash']
        self.miner = state['miner']

class BlockChain (object):
    def __init__(self, curve: EllipticCurve):
        self.curve = curve
        self.blocks = []
        self.users = []
        self.pending_transactions = []
        self.stake = Staking()
        #threading.Thread(target=self.start_timer).start()

    def add_block(self, block: Block):
        """Add a block to the chain."""
        # Check if this is the first block being added to the chain
        if len(self.blocks) == 0:
            previous_hash = "BLOCKCHAIN_START"
        else:
            previous_hash = self.blocks[-1].hash

        print("Here")
        # Check if the block's transactions are valid and signed by the correct user
        if not self.verify_signed_transactions(block.transactions):
            return False

        print("here")
        # Check if the current block points to the correct previous block
        if block.previous_hash != previous_hash:
            return False

        print("Block added to the chain!")
        # If all checks pass, add the block to the chain
        self.blocks.append(block)
        return True

    def add_user(self, user: User):
        self.users.append(user)

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
        new_block = Block(previous_hash, self.pending_transactions)
        new_block.miner = miner
        miner.balance += 10
        print(str(new_block))
        self.add_block(new_block)
        for transaction in self.pending_transactions:
            transaction[0].sender.balance -= transaction[0].amount
            transaction[0].receiver.balance += transaction[0].amount
        self.pending_transactions = []
        return self.add_block(new_block)

    def add_transaction(self, transaction_signed):
        self.pending_transactions.append(transaction_signed)
        if len(self.pending_transactions) > 10:
            self.mine()

    def start_timer(self):
        while True:
            time.sleep(10)
            if len(self.pending_transactions) > 0:
                # mine the transactions
                self.mine()

    def make_transaction(self, sender, privkey, receiver, amount):
        by = self.get_user(sender)
        to = self.get_user(receiver)
        if by is None or to is None:
            return False
        transaction = Transaction(by, to, amount)
        signature = sign(self.curve, privkey, str(transaction))
        self.add_transaction((transaction, signature))

    def __str__(self):
        return str(self.blocks)

    def print_chain(self):
        for block in self.blocks:
            print(str(block)+"\n")

    def verify_signed_transactions(self, signed_transactions):
        for signed_transaction in signed_transactions:
            if not Transaction.is_valid(signed_transaction[0]):
                return False
            if not verify(self.curve, signed_transaction[0].sender.pubkey, str(signed_transaction[0]), signed_transaction[1]):
                return False
        return True

    def save_to_file(blockchain, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(blockchain, f)

    @classmethod
    def load_from_file(cls, file_path):
        """
        Load the blockchain from a file using pyckle
        """
        with open(file_path, 'rb') as f:
            return pickle.load(f)

class Staking:
    def __init__(self):
        self.users = {}
        self.total_staked_coins = 0

    def stake_coins(self, user: User, amount: int, unstaking_period: int = 100):
        """Stake a given amount of coins."""
        if amount > user.balance:
            raise ValueError("Insufficient balance.")
        if user not in self.users.keys():
            self.users[user] = 0
        self.users[user] += amount
        self.total_staked_coins += amount
        user.balance -= amount
        self.update_staking_power(user)
        user.unstaking_period = unstaking_period

    def update_staking_power(self, user: User):
        """Update the user's staking power based on the amount of staked coins."""
        user.staking_power = self.users[user] / self.total_staked_coins

    def unstake_coins(self, user: User, amount: int):
        """Unstake a given amount of coins."""
        if amount > self.users[user]:
            raise ValueError("Insufficient staked coins.")
        self.users[user] -= amount
        self.total_staked_coins -= amount
        user.balance += amount
        self.update_staking_power(user)

    def __setstate__(self, state):
        self.users = state['users']
        self.total_staked_coins = state['total_staked_coins']
        for user in self.users:
            self.update_staking_power(user)

    def __getstate__(self):
        return {'users': self.users, 'total_staked_coins': self.total_staked_coins}



