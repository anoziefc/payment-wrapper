import logging


logger = logging.getLogger(__name__)


class TransactionError(Exception):
    def __init__(self, message: str = "Card validation failed", code: int = None, context: dict = None):
        self.code = code
        self.context = context or {}

        masked_context = {k: self._mask_value(v) for k, v in self.context.items()}

        full_message = message
        if code:
            full_message += f" (Error code: {code})"

        logger.error(f"CardError raised: {full_message} | Context: {masked_context}")
        super().__init__(full_message)

    def _mask_value(self, value):
        if isinstance(value, str):
            if len(value) > 6:
                return value[:2] + "****" + value[-2:]
        return value[:2] + "****"
