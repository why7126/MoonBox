"""Per-call execution policy, isolated by worker thread and restored after every run."""
from contextvars import ContextVar
DELIVERY = ContextVar('moonbox_delivery_scope', default=None)
IMAGE = ContextVar('moonbox_immutable_image', default=None)
