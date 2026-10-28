"""Bounded pure parser memo for private immutable materializations only."""
from collections import OrderedDict
from contextlib import contextmanager
from sys import getsizeof
from threading import RLock
from copy import deepcopy

MAX_BYTES = 8 * 1024 * 1024
MAX_VERSIONS = 2
_lock = RLock()
_versions = OrderedDict()


def clone(value, memo=None):
    """Defensive copies with a narrow fast path for plain parsed containers.

    Preserve cycles/aliases and delegate custom types to deepcopy's protocol.
    No caller receives a mutable object owned by the shared parser memo.
    """
    kind = type(value)
    if kind in (str, int, float, bool, bytes, type(None)):
        return value
    memo = {} if memo is None else memo
    key = id(value)
    if key in memo:
        return memo[key]
    if kind is dict:
        result = {}
        memo[key] = result
        for k, v in value.items():
            result[clone(k, memo)] = clone(v, memo)
        return result
    if kind is list:
        result = []
        memo[key] = result
        result.extend(clone(item, memo) for item in value)
        return result
    return deepcopy(value, memo)


def size(value, seen=None):
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    total = getsizeof(value)
    if isinstance(value, dict):
        return total + sum(size(k, seen) + size(v, seen) for k, v in value.items())
    if isinstance(value, (tuple, list, set, frozenset)):
        return total + sum(size(v, seen) for v in value)
    if hasattr(value, '__dict__'):
        total += size(vars(value), seen)
    for cls in type(value).__mro__:
        slots = getattr(cls, '__slots__', ())
        for slot in ((slots,) if isinstance(slots, str) else slots):
            if slot not in ('__dict__', '__weakref__') and hasattr(value, slot):
                total += size(getattr(value, slot), seen)
    return total


def clear():
    with _lock:
        _versions.clear()


@contextmanager
def lease(root):
    # Root names belong to cached_materialize, not caller-controlled live paths.
    # A different revision gets a different private root. Never retain a card,
    # authorization answer, acceptance verdict or execution state in this memo.
    with _lock:
        memo, _ = _versions.pop(root, ({}, 0))
        try:
            yield memo
        finally:
            used = size(memo)
            while _versions and (len(_versions) >= MAX_VERSIONS or
                                  sum(row[1] for row in _versions.values()) + used > MAX_BYTES):
                _versions.popitem(last=False)
            if used <= MAX_BYTES:
                _versions[root] = (memo, used)
