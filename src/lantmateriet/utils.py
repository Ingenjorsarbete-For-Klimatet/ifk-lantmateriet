"""Utils module."""
import time
import logging
from functools import wraps


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def timeit(has_key: bool = True):
    """Time decorator.

    Args:
        has_key: if firt argument is a key (from a dict), use in logging

    Returns:
        decorated function
    """

    def timeit_decorator(fun: callable):
        @wraps(fun)
        def wrap(*args, **kw):
            t0 = time.perf_counter()
            result = fun(*args, **kw)
            t1 = time.perf_counter()

            if has_key is True:
                logging.info(f"{args[0]} took: {t1 - t0} s.")
            else:
                logging.info(f"Took: {t1 - t0} s.")
            return result

        return wrap

    return timeit_decorator


def smap(fun, *args):
    """Useful in assigning different functions in Pool.map.

    Args:
        fun: function
        *args: function arguments
    """
    return fun(*args)
