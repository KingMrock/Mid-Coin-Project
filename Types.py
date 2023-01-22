def typecheck(func):
    """
    Decorator for binary operators of Zp class
    Check if the type of both elements are compatible
    """

    def func_check(self, other):
        if type(self) != type(other):
            try:
                other = self.__class__(other)  # Try to cast other element to class of the first one
            except:
                raise TypeError("Unable to cast {} from type {} to type {} in {}".format(
                    other, type(other).__name__, type(self).__name__, func.__name__))
        return func(self, other)

    return func_check


def memoize(func):
    cache = {}

    def memoized_func(*args, **kwargs):
        argTuple = args + tuple(kwargs)
        if argTuple not in cache:
            cache[argTuple] = func(*args, **kwargs)
        else:
            print("using memoized value:", cache[argTuple])
        return cache[argTuple]

    memoized_func.cache = cache
    return memoized_func
