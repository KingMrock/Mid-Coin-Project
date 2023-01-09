from Curve import *
from Field import *
from Point import *
from Prime import *
import random
import math




def compute_lcm(x, y):

   # choose the greater number
   if x > y:
       greater = x
   else:
       greater = y

   while(True):
       if((greater % x == 0) and (greater % y == 0)):
           lcm = greater
           break
       greater += 1

   return lcm

"""
def bsgs(P: CurvePoint, f: Z_nZ):
    m = int(f.p**(1/4))
    Ps = [j*P for j in range(1, m)]

    l = 1
    Q = (f.p+1)*P
    k = 1
    u = 0
    found = False
    while not found:
        R = Q + (k*2*m)*P
        for j in range(m-1):
            if Ps[j] == R:
                u = f.p+1+2*m*k + j
                found = True
            if -(Ps[j]) == R:
                u = f.p + 1 + 2 * m * k - j
                found = True
        k += 1
    factors = factorize(u, dupl=False)
    print(factors)
    i = 0
    while i < len(factors):
        factor = int(factors[i])
        if u % factor == 0 and isinstance((u//factor) * P, Ideal):
            u = u//factor
        else:
            i += 1
    print("P order:", u, "\n")
    l = compute_lcm(l, u)
    for n in range(int(f.p + 1 - 2 * (f.p**(1/2))), int(f.p + 1 + 2 * (f.p**(1/2)))):
        if l % n:
            return n
"""

def bsgs(e: EllipticCurve, f: Z_nZ) -> int:
    """
    Implementation of the Baby Step Giant Step funtion from Wikipedia
    Return the order of the curve

    Caution: The Memory Cost of this function is O(sqrt(p)), where p is the order of the field Z/nZ
    So it is unsuitable for large prime number
    """
    m = int(f.p**(1/4))
    found_order = False
    while not found_order:
        P = get_element(e, f)
        Ps = [j*P for j in range(0, m)]

        l = 1
        Q = (f.p+1)*P
        k = 1
        u = 0
        found = False
        while not found:
            R = Q + k*((2*m)*P)
            for j in range(m):
                if Ps[j] == R:
                    u = f.p+1+2*m*k - j
                    found = True
                if -(Ps[j]) == R:
                    u = f.p + 1 + 2 * m * k + j
                    found = True
            k += 1
        factors = factorize(u, dupl=False)
        i = 0
        while i < len(factors):
            factor = factors[i]
            if u % factor == 0 and isinstance((u//int(factor)) * P, Ideal):
                u = u//int(factor)
            else:
                i += 1
        e.set_order(u)
        e.set_generator(P)
        l = compute_lcm(l, u)
        ns = []
        for n in range(int(f.p + 1 - 2 * (f.p**(1/2))), int(f.p + 1 + 2 * (f.p**(1/2)))+1):
            if n % l == 0:
                ns.append(n)
        if len(ns) == 1:
            return ns[0]


def factorize(n, dupl=True):
    factors = []
    p = 2
    while True:
        while n % p == 0 and n > 0:
            if dupl is False:
                if p not in factors:
                    factors.append(p)
            else:
                factors.append(p)
            n = n / p
        p += 1
        if p > n / p:
            break
    if n > 1:
        factors.append(n)
    return factors


def calculateLegendre(a, p):
    if a >= p or a < 0:
        return calculateLegendre(a % p, p)
    elif a == 0 or a == 1:
        return a
    elif a == 2:
        if p % 8 == 1 or p % 8 == 7:
            return 1
        else:
            return -1
    elif a == p - 1:
        if p % 4 == 1:
            return 1
        else:
            return -1
    elif not is_prime(a):
        factors = factorize(a)
        product = 1
        for pi in factors:
            product *= calculateLegendre(pi, p)
        return product
    else:
        if ((p - 1) / 2) % 2 == 0 or ((a - 1) / 2) % 2 == 0:
            return calculateLegendre(p, a)
        else:
            return (-1) * calculateLegendre(p, a)



def mult2(a, b, q, n):
    t1 = (a[0] * b[1]) % n
    t2 = (a[1] * b[0]) % n
    t1 = (t1 + t2) % n
    t2 = (a[1] * b[1]) % n
    t3 = ((n - 1) * q[0]) % n
    t4 = ((n - 1) * q[1]) % n
    t5 = (a[0] * b[0]) % n
    t3 = (t5 * t3) % n
    t4 = (t5 * t4) % n
    c = [(t1 + t3) % n, (t2 + t4) % n]
    return (c)


def exp1(e, g, n):
    t = 1
    sq = g
    e1 = e
    while (e1 != 0):
        if (e1 % 2) == 1:
            t = (sq * t) % n
            e1 = (e1 - 1) // 2
        else:
            e1 = e1 // 2
        sq = (sq * sq) % n
    return (t)



def exp2(e, g, q, n):
    t = [0, 1]
    sq = g
    e1 = e
    while (e1 != 0):
        if (e1 % 2) == 1:
            t = mult2(sq, t, q, n)
            e1 = (e1 - 1) // 2
        else:
            e1 = e1 // 2
        sq = mult2(sq, sq, q, n)
    return (t)


def CL(c, b, p):
    t1 = (b * b) % p
    t2 = (4 * c) % p
    t2 = (p - t2) % p
    g = (t1 + t2) % p
    e = (p - 1) // 2
    h = exp1(e, g, p)
    s = 1
    if ((h == 0) or (h == 1)):
        s = 0
    e = e + 1
    t1 = ((p - 1) * b) % p
    t2 = c % p
    q = [t1, t2]
    a = [1, 0]
    t3 = exp2(e, a, q, p)
    t = s * t3[1]
    return (t)

def sqrt1(c, p):
    m1 = 50
    t = 0
    c1 = c % p
    for i in range(m1):
        y = CL(c1, ((i + 1) % p), p)
        t1 = (y * y) % p
        if (t1 == c1):
            t = y
            break
    return (t)

"""
def Cipolla(n: int, f: Z_nZ):
    fn = f(n)
    for i in range(f.p):
        leg = calculateLegendre(f(i)*f(i) - n,f.p)
        if leg != 1:
            x=pow(i*i-n, (f.p+1)/2, f.p)
"""



def get_element(e: EllipticCurve, f: Z_nZ)->CurvePoint:
    found = False
    while not found:
        x_int = random.randint(0, f.p)
        x = f(x_int)
        fx = x*x*x + e.get_a()*x + e.get_b()
        leg = calculateLegendre(fx.get_n(), f.p)
        if leg == 1:
            result = sqrt1(fx.get_n(), f.p)
            cz = CurvePoint(x, f(result), e)
            return cz
