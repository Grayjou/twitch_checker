"""
Utility helpers for twitch_checker.
"""

from typing import Iterable, List, Generator


def chunked(items: Iterable[str], size: int = 100) -> Generator[List[str], None, None]:
    """
    Yield lists of size <= `size` from an iterable.
    Useful for Twitch API batching.
    """
    lst = list(items)
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
