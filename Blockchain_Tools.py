from Point import CurvePoint
from datetime import datetime, timedelta
from Signature import *
import re

class User:
    def __init__(self, name: str, pubkey: CurvePoint):
        self.name = name
        self.pubkey = pubkey
        self.staking_power = 0 # How much of the total staking power this user has
        self.balance = 0 # Initial balance

    def get_balance(self, blockchain):
        return self.balance

    def __str__(self):
        return self.name + ": " + str(self.pubkey)

    def __getstate__(self):
        return {'name': self.name, 'pubkey': self.pubkey, 'staking_power': self.staking_power, 'balance': self.balance }

    def __setstate__(self, state):
        self.name = state['name']
        self.pubkey = state['pubkey']
        self.staking_power = state['staking_power']
        self.balance = state['balance']



"""
Transactions are stored in a list of tuples (sender, receiver, amount)
"""
class Transaction:
    def __init__(self, sender, receiver, amount, status="Pending"):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.status = status

    def __str__(self):
        return str(self.sender) + " -> " + str(self.receiver) + " : " + str(self.amount) + " Mid£Coin"

    def __eq__(self, other):
        return self.sender == other.sender and self.receiver == other.receiver and self.amount == other.amount

    @classmethod
    def is_valid(cls, transaction):
        return transaction.sender.balance >= transaction.amount

    def __getstate__(self):
        return {'sender': self.sender, 'receiver': self.receiver, 'amount': self.amount, 'status': self.status}

    def __setstate__(self, state):
        self.__init__(state['sender'], state['receiver'], state['amount'], state['status'])


class Staking:
    def __init__(self):
        self.users = {} # Dictionary of users and their staked coins and their unstaking period
        self.total_staked_coins = 0
        self.unstaking_period = timedelta(minutes=100)

    def stake_coins(self, user: User, amount: float):
        """Stake a given amount of coins."""
        if amount > user.balance:
            raise ValueError("Insufficient balance.")
        if user not in self.users.keys():
            self.users[user] = [0, timedelta(0)]
        self.users[user][0] += amount
        self.total_staked_coins += amount
        user.balance -= amount
        self.update_staking_power(user)
        self.users[user][1] = datetime.now()

    def update_staking_power(self, user: User):
        """Update the user's staking power based on the amount of staked coins."""
        if self.total_staked_coins == 0:
            user.staking_power = 0
        else:
            user.staking_power = self.users[user][0] / self.total_staked_coins

    def unstake_coins(self, user: User, amount: float):
        """Unstake a given amount of coins."""
        if amount > self.users[user][0]:
            return False
        if datetime.now() - self.users[user][1] < self.unstaking_period:
            return False
        self.users[user[0]] -= amount
        self.users[user[1]] = datetime.now()
        self.total_staked_coins -= amount
        user.balance += amount
        self.update_staking_power(user)
        return True

    def add_user(self, user: User):
        self.users[user] = [0, datetime.now()-self.unstaking_period]

    def __setstate__(self, state):
        self.users = state['users']
        self.total_staked_coins = state['total_staked_coins']
        self.unstaking_period = state['unstaking_period']
        for user in self.users:
            self.update_staking_power(user)

    def __getstate__(self):
        return {'users': self.users, 'total_staked_coins': self.total_staked_coins, 'unstaking_period': self.unstaking_period}


def verify_function(curve, transaction, signature):
    match = re.search(r"X: (\d+);Y: (\d+) ", transaction)
    if match:
        x = match.group(1)
        y = match.group(2)
    else:
        return "Invalid public key"
    try:
        x = int(x)
        y = int(y)
        field = curve.get_a().p
        pub_key = CurvePoint(Zn(x, field), Zn(y, field), curve)
    except:
        return "Invalid public key"

    match = re.search(r"(\d+), (\d+)", signature)
    if match:
        signature = (int(match.group(1)), int(match.group(2)))
    else:
        return "Invalid signature"

    print(pub_key, signature)
    if verify(curve, pub_key, transaction, signature) or verify(curve, pub_key, transaction[1:], signature):
        return "Valid Transaction"
    else:
        return "Invalid Transaction"

def read_block(data):
    lines = data.splitlines()
    transactions = []
    messages = []
    block_hash = ""
    previous_hash = ""
    miner = ""
    amount = 0
    i = 0
    while i < len(lines):
        if lines[i].startswith("Block Hash: "):
            block_hash = lines[i][12:]
            i+=1
        elif lines[i].startswith("Previous Hash: "):
            previous_hash = lines[i][15:]
            i+=1
        elif lines[i].startswith("Transaction in this block:"):
            while i < len(lines) and not lines[i].startswith("Message in this block"):
                transaction = lines[i]
                end_index = transaction.find("Mid£Coin") + len("Mid£Coin")
                transaction_text = transaction[0:end_index]
                signature_start_index = transaction.find("Signature:") + len("Signature:")
                signature = transaction[signature_start_index:]
                transactions.append((transaction_text, signature))
                i += 1
        elif lines[i].startswith("Messages in this block:"):
            while i < len(lines) and not lines[i].startswith("Mined by: "):
                message = lines[i]
                end_index = message.find("Signature:") - 1
                message_text = message[0:end_index]
                signature_start_index = message.find("Signature:") + len("Signature:")
                signature = message[signature_start_index:]
                messages.append((message_text, signature))
                i += 1
        elif lines[i].startswith("Mined by: "):
            miner = lines[i][10:]
            amount = float(lines[i][lines[i].find("Reward:") + len("Reward: "):])
            i += 1

        calculated_hash = str(Hash(data[data.find("Block Hash: "), data.find("Mined by: ")]))
        return block_hash, previous_hash, transactions, messages, miner, calculated_hash, amount
