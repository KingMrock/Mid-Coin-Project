import json

from Curve_Tools import *
from Prime import *
from Curve import EllipticCurve
from Point import CurvePoint
from Field import Zn
from Signature import *
from random import randint
from Blockchain_Tools import *
from Block import *

# Defining main function
def main():
    """Simulate a small blockchain test with a few users and a few transactions"""
    p = 20333
    a = Zn(0, p)
    b = Zn(7, p)
    # Create the curve object
    curve = EllipticCurve(a, b)
    curve.set_generator(CurvePoint(Zn(15377, p), Zn(20134, p), curve))
    curve.set_order(3389)

    # Generate a random private key
    privkey_alice = randint(1, curve.get_order() - 1)
    Alice = User("Alice", curve.get_generator() * privkey_alice)
    privkey_bob = randint(1, curve.get_order() - 1)
    Bob = User("Bob", curve.get_generator() * privkey_bob)

    blockchain = BlockChain(curve)
    blockchain.add_user(Alice)
    blockchain.add_user(Bob)
    blockchain.stake.stake_coins(Alice, 2)

    blockchain.make_transaction(Alice.pubkey, privkey_alice, Bob.pubkey, 1)
    blockchain.make_transaction(Bob.pubkey, privkey_bob, Alice.pubkey, 4)

    blockchain.mine()

    blockchain.print_chain()

    blockchain.save_to_file("blockchain.txt")
    print("Saved blockchain to blockchain.txt")
    blockchain.stop_timer()
    print("Here")

    blockload = BlockChain.load_from_file("blockchain.txt")
    blockload.print_chain()
    blockload.stop_timer()

    return 0
# Using the special variable
# __name__
if __name__ == "__main__":
    main()