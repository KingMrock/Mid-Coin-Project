from Prime import *


class Hash:
    def __init__(self, message: str):
        # These are the two prime numbers we use to apply the modulo
        self.m1, self.m2 = 131071, 131063
        self.p1, self.p2 = 31, 37
        self.hash = 0
        self.compute_hash(message)

    def compute_hash(self, message: str):
        pow1, pow2 = 1, 1
        hash1, hash2 = 0, 0
        for ch in message:
            seed = 1 + ord(ch) - ord('a')
            hash1 = (hash1 + seed * pow1) % self.m1
            hash2 = (hash2 + seed * pow2) % self.m2
            pow1 = (pow1 * self.p1) % self.m1
            pow2 = (pow2 * self.p2) % self.m2
        self.hash = int(str(hash1) + str(hash2))

    def __eq__(self, other):
        return self.hash == other.hash

    def __str__(self):
        return bin(self.hash)

    def diff(self, other):
        return bin(self.hash & other.hash)


if __name__ == '__main__':
    s1, s2 = "animal", "amimal"
    hash1, hash2 = Hash(s1), Hash(s2)
    print("Hash of " + s1 + " is " + str(hash1))
    print("Hash of " + s2 + " is " + str(hash2))
    print("The difference between the hashes is " + hash1.diff(hash2))
