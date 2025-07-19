import logging
from typing import Dict

from paystack.errors.errors import TransactionError

logger = logging.getLogger(__name__)

def assert_success(
    resp: Dict,
    expected_message: str,
    error_message: str,
    error_code: int = 403,
    extra_context: Dict = None
) -> None:
    """
    Raise a TransactionError if the response message does not match the expected one.

    Args:
        resp (Dict): The response dictionary from the API.
        expected_message (str): The expected success message from Paystack.
        error_message (str): The message to raise in TransactionError.
        error_code (int): The HTTP status code to attach.
        extra_context (Dict): Additional context to include in the error.

    Raises:
        TransactionError: if the `message` in `resp` doesn't match `expected_message`.
    """
    actual_message = resp.get("message", "")
    if actual_message != expected_message:
        context = {"message": actual_message}
        if extra_context:
            context.update(extra_context)
        logger.warning(f"{error_message}: {actual_message}")
        raise TransactionError(
            message=error_message,
            code=error_code,
            context=context
        )
