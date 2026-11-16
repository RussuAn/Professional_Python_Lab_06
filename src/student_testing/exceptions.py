"""Domain-specific error hierarchy."""
class ApplicationError(Exception):
    """Base application error."""

class ConfigurationError(ApplicationError):
    """Invalid application configuration."""

class DataError(ApplicationError):
    """Base data processing error."""

class DataImportError(DataError):
    """Input data could not be imported."""

class RecordValidationError(DataError):
    """Invalid record with source metadata."""
    def __init__(self, message: str, *, line_number: int | None = None, field: str | None = None) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field

class DataExportError(DataError):
    """Atomic data export failed."""
