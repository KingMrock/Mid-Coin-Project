from Field import Z_nZ
from Hash import *
from random import randint
from Curve import *

def sign(curve, privkey, message):
    """
    Sign a message using the private key and the curve.
    Returns the signature as a tuple (r,s).
    """
    # Hash the message
    h = Hash(message).hash

    field = Z_nZ(curve.get_order())
    # Choose a random nonce k
    h = field(h)
    k = field(randint(1, curve.get_order() - 1))

    # Calculate r and s
    r = field(int((curve.get_generator() * int(k)).get_x()))
    s = (h + privkey * r) * k.inverse()

    print("r", r, "s", s, "k", k, "h", h)
    return r, s


def verify(curve, pubkey, message, signature):
    """
    Verify a signature for a message using the public key and the curve.
    Returns True if the signature is valid, False otherwise.
    """
    field = Z_nZ(curve.get_order())
    # Unpack the signature
    r, s = signature

    # Hash the message
    h = field(Hash(message).hash)

    # Calculate w
    w = s.inverse()

    # Calculate u1 and u2
    u1 = int((h * w))
    u2 = int((r * w))
    print("u1*curvegen", u1 * curve.get_generator(), "u2*pubkey", u2 * pubkey)

    # Calculate v
    v = -((curve.get_generator() * u1) + (pubkey * u2))
    print("v", v)
    return field(int(v.get_x())) == r
