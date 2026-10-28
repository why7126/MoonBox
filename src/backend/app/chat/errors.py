"""Shared errors without importing database models or execution services."""

class ChatError(Exception):
    def __init__(self, code: int, message: str, status: int = 409, *, kind: str | None = None, details: dict | None = None):
        self.code, self.message, self.status = code, message, status
        self.kind = kind
        self.details = details or {}

