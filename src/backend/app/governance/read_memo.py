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
    # Exact built-in scalars have no instance dict or slots to traverse.
    # Avoid repeated reflection for every title/path token in a warm memo;
    # subclasses still take the general path so their storage is counted.
    if type(value) in (str, int, float, bool, bytes, type(None)):
        return total
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


def bounded_entries(memo):
    """Retain useful pure entries when the whole parsed tree exceeds budget.

    Charge shared objects per entry conservatively. Include dictionary storage
    after insertion, so the retained subset cannot exceed the existing limit.
    Large relationship indexes are preferred, but never exempt from the cap.
    """
    retained = {}
    payload = 0
    indexes = {'summary_change_index', 'archive_directory_index'}
    def priority(key):
        return 0 if isinstance(key, tuple) and key and key[0] in indexes else 1
    for key in sorted(memo, key=priority):
        value = memo[key]
        weight = size(key) + size(value)
        retained[key] = value
        if getsizeof(retained) + payload + weight > MAX_BYTES:
            retained.pop(key)
        else:
            payload += weight
    # A rejected insertion can still grow the dict's allocated table.
    while retained and getsizeof(retained) + payload > MAX_BYTES:
        key, value = retained.popitem()
        payload -= size(key) + size(value)
    return retained


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
            if used > MAX_BYTES:
                memo = bounded_entries(memo)
                used = size(memo) if memo else MAX_BYTES + 1
            while _versions and (len(_versions) >= MAX_VERSIONS or
                                  sum(row[1] for row in _versions.values()) + used > MAX_BYTES):
                _versions.popitem(last=False)
            if used <= MAX_BYTES:
                _versions[root] = (memo, used)
