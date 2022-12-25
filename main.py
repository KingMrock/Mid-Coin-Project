from Diffie import *
from Prime import *
from Curve import EllipticCurve
from Point import CurvePoint
from Field import Z_nZ
from Signature import *
from random import randint

# Defining main function
def main():
    """
    # Find a generator point on the curve, output order of the curve
    Field = Z_nZ(generate_prime(32))
    print("On utilise le corps Z/", Field.p, "Z")
    curve = EllipticCurve(a=Field(0), b=Field(7))
    print(bsgs(curve, Field))
    """

    # Define the curve parameters
    F = Z_nZ(generate_prime(18))
    a = F(0)
    b = F(7)

    # Create the curve object
    curve = EllipticCurve(a, b)
    bsgs(curve, F)

    print(curve.get_generator() * (curve.get_order()))

    # Generate a random private key
    privkey = randint(1, curve.get_order() - 1)

    # Calculate the public key
    pubkey = privkey * curve.get_generator()
    print("Private key:", privkey)
    print("Public key:", pubkey)

    # Choose a message to sign
    message = "Hello, world!"

    # Sign the message
    signature = sign(curve, privkey, message)
    print("Signature", signature)

    # Verify the signature
    is_valid = verify(curve, pubkey, message, signature)

    print("Signature is valid:", is_valid)





# Using the special variable
# __name__
if __name__ == "__main__":
    main()