"""Errors raised by the orders app."""


class OrderError(ValueError):
    """Raised when an order request is invalid. The message is shown to the user."""
