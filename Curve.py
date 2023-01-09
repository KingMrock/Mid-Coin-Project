import numpy as np
import math
import matplotlib.pyplot as plt
from Field import Z_nZ



class EllipticCurve(object):
    def __init__(self, a, b):
        """
        Constructor of class curve
        """
        self.__n = None  # Order of the curve
        self.__g = None  # Generator Point of the Curve
        self.__a = a
        self.__b = b

    def is_on_curve(self, x, y):
        """
        Check if given coordinates are on the curve
        """
        return y * y == x * x * x + self.get_a() * x + self.get_b()

    def __eq__(self, other):
        """
        Check if two curves are equal based on their coordinates
        """
        return self.__a == other.geta() and self.__b == other.getb()

    def get_a(self):
        return self.__a

    def get_b(self):
        return self.__b

    def set_order(self, n):
        self.__n = n

    def set_generator(self, g):
        self.__g = g

    def get_order(self):
        return self.__n

    def get_generator(self):
        return self.__g

    def __str__(self):
        return 'y^2 = x^3 + {}x + {}'.format(self.__a, self.__b)

    def plot(self):
        """
        Display the curve using matplotlib
        """
        mag = round(math.log(math.abs(self.__a + self.__b),
                             10)) + 1  # This allows to generate an adequate amount of point based on a and b
        x, y = np.ogrid[-mag * 10: mag * 10: mag * 100j, -mag * 5:mag * 5:mag * 100j]
        plt.contour(x.ravel(), y.ravel(), pow(y, 2) - pow(x, 3) - x * self.__a - self.__b, [0])
        plt.grid()
        plt.show()

    @classmethod
    def plot_range(cls, a_list, b_list):
        """
        Plot different curves based on a list of a parameters and b parameters
        The plot appears in red if the condition a**3+b**2!=0 isn't satisfied
        """
        figure, axis = plt.subplots(len(a_list), len(b_list), layout="constrained")
        for i in range(len(a_list)):
            for k in range(len(b_list)):
                a = a_list[i]
                b = b_list[k]
                mag = round(math.log(abs(a + b) + 1, 4)) + 1  # This allows to generate an adequate x,y axis
                x, y = np.mgrid[-3 * mag:3 * mag: 150j, -3 * mag:3 * mag:150j]
                c = 'red' if (27 * b ** 2 + 4 * a ** 3 == 0) else 'black'
                axis[i, k].contour(x, y, pow(y, 2) - pow(x, 3) - x * a - b, levels=[0], colors=c)
                axis[i, k].axhline(0, lw=0.5)
                axis[i, k].axvline(0, lw=0.5)
                axis[i, k].set_ylabel("a=" + str(a), rotation='horizontal', fontsize='large')
                axis[i, k].set_xlabel("b=" + str(b), rotation='horizontal', fontsize='large')
                axis[i, k].label_outer()

        figure.text(0.5, 0.5, 'Property of M\'Rock Corp. LLC',
                    fontsize=40, color='gray', alpha=0.3,
                    ha='center', va='center', rotation=30)
        figure.show()
