from Types import *
from Prime import is_prime


def euclide_extended_algo(a, b):
    """
    Euclidean extended algorithm, return u, v Bezout's coefficients and r : gcd(a,b)
    such that r = a*u + b*v
    """
    if abs(b) > abs(a):
        (x, y, d) = euclide_extended_algo(b, a)
        return y, x, d

    if abs(b) == 0:
        return 1, 0, a

    x1, u, y1, v = 0, 1, 1, 0
    while abs(b) > 0:
        q, r = divmod(a, b)
        x = u - q * x1
        y = v - q * y1
        a, b, u, x1, v, y1 = b, r, x1, x, y1, y

    return u, v, a




class _FieldElement(object):
    """
    Base class implementing operation for any commutative field
    """

    def __radd__(self, other): return self + other

    def __rsub__(self, other): return -self + other

    def __rmul__(self, other): return self * other

    # All elements in a field have an inverse by definition
    def __truediv__(self, other): return self * other.inverse()

    def __rtruediv__(self, other): return self.inverse() * other

    def __div__(self, other): return self.__truediv__(other)

    def __rdiv__(self, other): return self.__rtruediv__(other)


@memoize
def Z_nZ(p):
    class Zn(_FieldElement):
        def __init__(self, n):
            try:
                self.__n = n % p
            except:
                raise TypeError("Can't convert {} to int".format(type(n).__name__))

        def get_n(self):
            return self.__n

        @typecheck
        def __add__(self, other):
            return Zn(self.get_n() + other.get_n())

        @typecheck
        def __sub__(self, other):
            return Zn(self.get_n() - other.get_n())

        @typecheck
        def __mul__(self, other):
            return Zn(self.get_n() * other.get_n())

        def __neg__(self):
            return Zn(-self.get_n())

        def __eq__(self, other):
            return isinstance(other, Zn) and self.get_n() == other.get_n()

        def __ne__(self, other):
            return not isinstance(other, Zn) or self.get_n() != other.get_n()

        def __str__(self):
            return str(self.get_n())

        def __repr__(self):
            return "{} (mod {})".format(self.get_n(), self.p)

        def __int__(self):
            return self.get_n()

        def __abs__(self):
            return abs(self.get_n())

        def __gcd__(self, other):
            return self + other

        def divmod(self, divisor):
            q, r = divmod(self.get_n(), divisor.get_n())
            return Zn(q), Zn(r)


        def inverse(self):
            x, y, d = euclide_extended_algo(self.get_n(), self.p)
            return Zn(x)

        def __hash__(self):
            return hash(Zn.__name__)

    Zn.p = p
    Zn.prime = is_prime(p)
    Zn.__name__ = "Z/{}Z".format(p)
    return Zn
