"""Business-rule errors raised by use cases. The API layer maps these to HTTP."""
from __future__ import annotations


class MonthAlreadyLoadedError(Exception):
    """The target month already has transactions; loading is blocked (no dup)."""


class EmptyDraftError(Exception):
    """There are no lines to load (no templates, or the user discarded them all)."""


class InvalidDraftLineError(Exception):
    """A draft line failed validation (unknown template, bad amount/date)."""
