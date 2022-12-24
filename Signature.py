import random
from Hash import *

# Generate a private key (a random integer between 1 and the order of the generator point)
private_key = random.randint(1, generator_point_order())

# Generate a public key from the private key (the result of multiplying the generator point by the private key)
public_key = point_multiplication(generator_point(), private_key)

def sign(message: bytes) -> tuple:
    # Hash the message using a cryptographic hash function (such as SHA-256)
    hash_ = str(Hash(message))

    # Generate a random nonce (a number used once)
    nonce = random.randint(1, generator_point_order())

    # Compute the nonce multiplied by the generator point and add it to the public key. This is the "r" value.
    r = point_addition(point_multiplication(generator_point(), nonce), public_key)

    # Compute the inverse of the nonce modulo the order of the generator point
    nonce_inv = inverse_modulo(nonce, generator_point_order())

    # Multiply the hash of the message by the inverse of the nonce
    s_num = (int.from_bytes(hash_, 'big') * nonce_inv) % generator_point_order()

    # Add the private key multiplied by the "r" value to the result of step 7. This is the "s" value.
    s = (s_num + private_key * r[0]) % generator_point_order()

    # The signature is the pair (r, s)
    return (r, s)


def verify(message: bytes, signature: tuple, public_key: tuple) -> bool:
    # Hash the message using the same cryptographic hash function used to sign the message
    hash_ = str(Hash(message))

    # Unpack the signature
    r, s = signature

    # Compute the inverse of "s" modulo the order of the generator point
    s_inv = inverse_modulo(s, generator_point_order())

    # Multiply the hash of the message by the inverse of "s"
    z = (int.from_bytes(hash_, 'big') * s_inv) % generator_point_order()

    # Multiply "r" by the inverse of "s"
    u1 = (z * r[0]) % generator_point_order()

    # Add the result of step 4 to the generator point multiplied by the result of step 3
    u2 = (s_inv * r[0]) % generator_point_order()
    point = point_addition(point_multiplication(generator_point(), u1), point_multiplication(public_key, u2))

    # The result of step 5 should be equal to the public key. If it is, the signature is valid.
    return point == public_key