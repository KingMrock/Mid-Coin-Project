import Point

class User:
    def __init__(self, name: str, privkey: int, pubkey: Point):
        self.name = name
        self.privkey = privkey
        self.pubkey = pubkey
        self.staking_power = 0 # How much of the total staking power this user has
        self.balance = 5 # Initial balance

    def get_balance(self, blockchain):
        return self.balance

