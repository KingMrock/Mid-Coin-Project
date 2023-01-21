class Point(object):
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __add__(self, other):
        return Point(self.get_x() + other.get_x(), self.get_y() + other.get_y())

    def __str__(self):
        return "X: " + str(self.get_x()) + ";Y: " + str(self.get_y())

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def set_x(self, x):
        self.__x = x

    def set_y(self, y):
        self.__y = y


class CurvePoint(Point):
    def __init__(self, x, y, curve):
        if curve.is_on_curve(x, y):
            Point.__init__(self, x, y)
            self.__curve = curve
        else:
            raise Exception('The point x:{}; y:{} is not on the given curve: '.format(x, y) + str(curve))

    def get_curve(self):
        return self.__curve

    def set_curve(self, curve):
        self.__curve = curve

    def __neg__(self):
        return CurvePoint(self.get_x(), -self.get_y(), self.__curve)

    def __eq__(self, other):
        if type(other) is Ideal:
            return False
        return other.get_x() == self.get_x() and other.get_y() == self.get_y()

    def __add__(self, other):
        if isinstance(other, Ideal):
            return self

        x_1, y_1, x_2, y_2 = self.get_x(), self.get_y(), other.get_x(), other.get_y()

        if (x_1, y_1) == (x_2, y_2):
            if y_1 == 0:
                return Ideal(self.get_curve())  # Tangent
            m = (3 * x_1 * x_1 + self.get_curve().get_a()) / (2 * y_1)
        else:
            if x_1 == x_2:
                return Ideal(self.get_curve())
            m = (y_2 - y_1) / (x_2 - x_1)
        x_3 = m * m - x_2 - x_1
        y_3 = m * (x_3 - x_1) + y_1
        return CurvePoint(x_3, -y_3, self.get_curve())

    def __sub__(self, other):
        return self + -other

    def __mul__(self, n):
        if not (isinstance(n, int)):
            raise Exception("Can't scale a point by something which isn't an int!")
        else:
            if n < 0:
                return -self * -n
            if n == 0:
                return Ideal(self.get_curve())
            else:
                Q = self
                R = self if n & 1 == 1 else Ideal(self.get_curve())

                i = 2
                while i <= n:
                    Q = Q + Q

                    if n & i == i:
                        R = Q + R

                    i = i << 1

                return R

    def __rmul__(self, n):
        return self * n

    def __getstate__(self):
        return {'x': self.get_x(), 'y': self.get_y(), 'curve': self.get_curve()}

    def __setstate__(self, state):
        self.set_x(state['x'])
        self.set_y(state['y'])
        self.set_curve(state['curve'])


class Ideal(CurvePoint):
    """
    The Ideal Point of the curve, or Point at Infinity (the intersection of all vertical lines)
    It's the neutral element of the elliptic curve group
    It has no x, y coordinates
    """
    def __init__(self, curve):
        self.__curve = curve

    def get_curve(self):
        return self.__curve

    def __eq__(self, other):
        return isinstance(other, Ideal)

    def __str__(self):
        return 'Ideal point of the curve: ' + str(self.get_curve())

    def __neg__(self):
        return self

    def __add__(self, other):
        return other

    def __mul__(self, n):
        if not isinstance(n, int):
            raise Exception("Can't scale Point by non Integer value")
        else:
            return self
