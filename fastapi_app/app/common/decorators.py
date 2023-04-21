import time
from functools import wraps

from .loggers import logger


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        logger.info(f"{func.__name__} took {elapsed_time:.2f} seconds")
        return result

    return wrapper


def timer_decorator_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        logger.info(f"{func.__name__} took {elapsed_time:.2f} seconds")
        return result

    return wrapper
