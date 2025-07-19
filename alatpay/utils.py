import logging
from typing import Dict

from alatpay.exceptions import AlatException

logger = logging.getLogger(__name__)

def assert_success(
    resp: Dict,
    expected_message: str,
    error_message: str,
    error_code: int,
    extra_context: Dict = None
) -> None:
    actual_message = resp.get("message", "")
    if actual_message != expected_message:
        context = {"message": actual_message}
        if extra_context:
            context.update(extra_context)
        logger.warning(f"{error_message}: {actual_message}")
        raise AlatException(
            message=error_message,
            code=error_code,
            context=context
        )
