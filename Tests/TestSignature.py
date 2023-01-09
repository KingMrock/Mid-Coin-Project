#Test For signature module
#
# Path: Tests/TestSignature.py
from Curve_Tools import bsgs
from Prime import *
from Curve import EllipticCurve
from Point import CurvePoint
from Signature import *
from random import randint
from Field import Z_nZ


#Run test for fixed k
def test_fixed_k(size = 1001):
    # Define the curve parameters
    #F = Z_nZ(130127)
    F = Z_nZ(20333)
    a = F(0)
    b = F(7)
    print("On utilise le corps Z/", F.p, "Z")

    # Create the curve object
    curve = EllipticCurve(a, b)
    curve.set_generator(CurvePoint(F(15377), F(20134), curve))
    curve.set_order(3389)
    #curve.set_generator(CurvePoint(F(7), F(42), curve))
    #curve.set_order(102)

    print(curve.get_generator() * curve.get_order())
    print("Generator", curve.get_generator())
    print("Print Curve order: ", curve.get_order())

    # Generate a random private key
    privkey = randint(1, curve.get_order() - 1)

    # Calculate the public key
    pubkey = privkey * curve.get_generator()
    print("Private key:", privkey)
    print("Public key:", pubkey)

    message = "Hello, world!"
    okay = 0
    for i in range(1, size):
        signature = sign(curve, privkey, message, k=i)
        if verify(curve, pubkey, message, signature):
            print(i, ": Signature is valid:", True)
            okay += 1
        else:
            print(i, ": Signature is valid:", False)

    print("Signature is valid:", okay, "times out of", size-1)


def test_inverse():
    #Function testing if the inverse function from Z_nZ work properly
    F = Z_nZ(101)
    for i in range(1, 101):
        print(i, F(i).inverse())
        if F(i).inverse() * F(i) != F(1):
            print("Error with", i)
            return False

def test_point_multiplication():
    #Function testing if the point multiplication function from Point module work properly
    F = Z_nZ(101)
    a = F(0)
    b = F(7)
    print("On utilise le corps Z/", F.p, "Z")
    curve = EllipticCurve(a, b)
    curve.set_generator(CurvePoint(F(7), F(42), curve))
    curve.set_order(101)
    print(curve.get_generator() * curve.get_order())
    print("Generator", curve.get_generator())
    print("Print Curve order: ", curve.get_order())
    for i in range(1, 100):
        point = curve.get_generator()
        u = random.randint(1, 101)
        for j in range(1, u+1):
            print("addidtion: ", point+curve.get_generator(), "multiplication", curve.get_generator() * (j+1), "j=", j)
            point = point + curve.get_generator()
        if point != (u+1) * curve.get_generator():
            print("Error with", u)
            print(point, (u+1) * curve.get_generator())
            return False


def test_curve():
    #Function testing if the curve function from Curve module work properly
    found = False
    while not found:
        F = Z_nZ(generate_prime(16))
        a = F(0)
        b = F(7)
        print("On utilise le corps Z/", F.p, "Z")
        curve = EllipticCurve(a, b)
        bsgs(curve, F)
        print("Generator", curve.get_generator())
        print("Print Curve order: ", curve.get_order())
        if is_prime(curve.get_order()):
            found = True



if __name__ == "__main__":
    #test_inverse()
    test_fixed_k()
    #test_point_multiplication()
    #test_curve()