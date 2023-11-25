import itertools
from typing import Iterable, Iterator, List, TypeVar


T = TypeVar('T')


def batched(iterable: Iterable[T], batch_size: int) -> Iterator[List[T]]:
    """
    A generator that yields batches of a specified size from an iterable.

    Parameters:
        iterable (Iterable[T]): An iterable of any type T.
        batch_size (int): The number of items to include in each batch.

    Yields:
        Iterator[List[T]]: An iterator over batches (lists) from the iterable.

    """
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, batch_size))
        if not batch:
            break
        yield batch
