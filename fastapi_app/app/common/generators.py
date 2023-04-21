def infinite_generator(start: int = 0) -> int:
    i = start
    while True:
        yield i
        i += 1


def chunk_generator(lst, n=2000):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
