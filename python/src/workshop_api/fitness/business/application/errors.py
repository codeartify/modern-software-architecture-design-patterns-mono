class NotFoundError(Exception):
    """Raised when requested workshop data does not exist."""


class BusinessRuleViolation(Exception):
    """Raised when a workshop business rule is violated."""


class DuplicatePaymentError(Exception):
    """Raised when the same payment is applied more than once."""
