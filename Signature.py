from Field import Z_nZ
from Hash import *
from random import randint
from Curve import *
from Point import Ideal


def sign(curve, privkey, message, k=None):
    """
    Sign a message using the private key and the curve.
    Returns the signature as a tuple (r,s).computationnaly
    """
    # Hash the message
    h = Hash(message).hash
    field = Z_nZ(curve.get_order())
    # Choose a random nonce k
    if k is None:
        k = randint(1, curve.get_order() - 1)

    # Calculate r and s
    point = curve.get_generator() * k
    if isinstance(point, Ideal):
        return sign(curve, privkey, message)
    r = int(point.get_x()) % curve.get_order()
    if r == 0:
        return sign(curve, privkey, message)
    print(field(k), field(k).inverse(), field(k).inverse()*field(k) == field(1))
    s = (h + ((privkey * r) % curve.get_order())) * (field(k).inverse().get_n()) % curve.get_order()
    if s == 0:
        return sign(curve, privkey, message)

    #print("r", r, "s", s)
    return r, s


def verify(curve, pubkey, message, signature):
    """
    Verify a signature for a message using the public key and the curve.
    Returns True if the signature is valid, False otherwise.
    """
    field = Z_nZ(curve.get_order())
    # Unpack the signature
    r, s = signature
    s = field(s)

    # Hash the message
    h = Hash(message).hash

    # Calculate w
    w = s.inverse()

    # Calculate u1 and u2
    u1 = (h * w.get_n() % curve.get_order())
    u2 = (r * w.get_n() % curve.get_order())

    # Calculate v
    #print(curve.get_generator() * u1, pubkey * u2)
    v = (curve.get_generator() * u1) + (pubkey * u2)
    #print("v", v, "r", r)

    return int(v.get_x()) % curve.get_order() == r
