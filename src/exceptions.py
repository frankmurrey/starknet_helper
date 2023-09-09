from pydantic import ValidationError


class ModuleConfigValidationError(ValueError):
    def __init__(
            self,
            message: str,
    ):
        self.message = message
        super().__init__(message)
