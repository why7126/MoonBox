"""Byte-bounded protocol queue. One oversized, frame-bounded item may stand alone."""
import json
import queue
import threading
import time
from collections import deque

FRAME_BYTES = 8 * 1024 * 1024
QUEUE_BYTES = 4 * 1024 * 1024


def validate_depth(data, maximum=64):
    depth=0; quoted=False; escaped=False
    for byte in data:
        if quoted:
            if escaped: escaped=False
            elif byte==92: escaped=True
            elif byte==34: quoted=False
        elif byte==34: quoted=True
        elif byte in (91,123):
            depth+=1
            if depth>maximum: return False
        elif byte in (93,125): depth-=1
    return True


class ByteQueue:
    def __init__(self, maximum=QUEUE_BYTES, maximum_items=128):
        self.maximum=maximum; self.maximum_items=maximum_items; self.bytes=0; self.items=deque(); self.condition=threading.Condition()

    def put(self,value,timeout=None):
        size=len(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
        end=None if timeout is None else time.monotonic()+timeout
        with self.condition:
            while len(self.items)>=self.maximum_items or (self.items and self.bytes+size>self.maximum):
                remaining=None if end is None else end-time.monotonic()
                if remaining is not None and remaining<=0: raise queue.Full
                self.condition.wait(remaining)
            self.items.append((value,size));self.bytes+=size;self.condition.notify_all()

    def get(self,timeout=None):
        end=None if timeout is None else time.monotonic()+timeout
        with self.condition:
            while not self.items:
                remaining=None if end is None else end-time.monotonic()
                if remaining is not None and remaining<=0: raise queue.Empty
                self.condition.wait(remaining)
            value,size=self.items.popleft();self.bytes-=size;self.condition.notify_all();return value
