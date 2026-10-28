"""Separate periodic maintenance from the fast work-admission poll."""
import time


class Periodic:
    def __init__(self, seconds, clock=time.monotonic):
        self.seconds, self.clock, self.next_at = seconds, clock, 0.0

    def run(self, callback, *args):
        if self.clock() < self.next_at:
            return
        result = callback(*args)
        # Schedule after completion: a slow scan must not cause catch-up bursts.
        # Failure does not pretend a publication or maintenance run succeeded.
        self.next_at = self.clock() + self.seconds
        return result
