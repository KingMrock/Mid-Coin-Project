import random


def is_prime(n: int) -> bool:
    """Primality test using 6k+-1 optimization."""
    if n <= 3:
        return n > 1
    if not n % 2 or not n % 3:
        return False
    i = 5
    stop = int(n**0.5)
    while i <= stop:
        if not n % i or not n % (i + 2):
            return False
        i += 6
    return True


def generate_prime(bit_len, marsenne=False):
    if marsenne:
        return 2**32-1
    while True:
        a = random.randint(2**(bit_len-2), 2**(bit_len-1))
        a << 1
        a |= 1
        if is_prime(a):
            return a
