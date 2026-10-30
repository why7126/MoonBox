"""Trusted Git adapter for moonbox-worktree; callers authorize business scope."""
from .git import Repository, WorktreeConflict

__all__ = ['Repository', 'WorktreeConflict']
