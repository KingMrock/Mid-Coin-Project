from Point import CurvePoint

class User:
    def __init__(self, name: str, privkey: int, pubkey: CurvePoint):
        self.name = name
        self.privkey = privkey
        self.pubkey = pubkey
        self.staking_power = 0 # How much of the total staking power this user has
        self.balance = 5 # Initial balance

    def get_balance(self, blockchain):
        return self.balance

    def __str__(self):
        return "User :" + self.name + ": " + str(self.pubkey)

    def __getstate__(self):
        return { 'name': self.name, 'privkey': self.privkey, 'pubkey': self.pubkey, 'staking_power': self.staking_power, 'balance': self.balance }

    def __setstate__(self, state):
        self.name = state['name']
        self.privkey = state['privkey']
        self.pubkey = state['pubkey']
        self.staking_power = state['staking_power']
        self.balance = state['balance']