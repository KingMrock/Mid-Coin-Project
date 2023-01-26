from Point import CurvePoint
from datetime import datetime, timedelta

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
