class TaskManagementError(Exception):
    """task management errors."""

class DuplicateIDError(TaskManagementError):
    """DuplicateIDError"""

class RecordNotFoundError(TaskManagementError):
    """Recordnotfound"""

class ValidationError(TaskManagementError):
    """ValidationError"""

class DataFileError(TaskManagementError):
    """Data cannot safelybe read or write"""          
