"""Custom exceptions for the NodeWeaver package.

This module defines the exception hierarchy used throughout NodeWeaver.
All custom exceptions inherit from the base ScriptGeneratorError.

Exception Hierarchy:
    ScriptGeneratorError
    ├── ValidationError
    └── ConfigurationError
"""


class ScriptGeneratorError(Exception):
    """Base exception for all NodeWeaver script generation errors.

    This is the parent class for all custom exceptions in the script generation
    system. All specific error types should inherit from this class.

    Example:
        >>> try:
        ...     # Script generation code
        ... except ScriptGeneratorError as e:
        ...     print(f"Script generation failed: {e}")
    """
    pass

class ValidationError(ScriptGeneratorError):
    """Raised when script validation fails.

    This exception indicates that script validation failed due to invalid input,
    missing required fields, or other validation errors.

    Example:
        >>> if not script_content:
        ...     raise ValidationError("Script content cannot be empty")
    """
    pass

class ConfigurationError(ScriptGeneratorError):
    """Raised when configuration loading or parsing fails.

    This exception indicates that there was an error loading or parsing
    configuration files or settings.

    Example:
        >>> try:
        ...     with open(config_path) as f:
        ...         config = json.load(f)
        ... except json.JSONDecodeError as e:
        ...     raise ConfigurationError(f"Invalid JSON in config: {e}")
    """
    pass