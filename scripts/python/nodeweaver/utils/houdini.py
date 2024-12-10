"""Utility functions for Houdini environment and configuration.

This module provides utilities for managing Houdini's environment variables
and configuration settings. It focuses on persistent changes that survive
between sessions.
"""
from typing import Union
import hou

def set_env_var(var_name: str, var_value: Union[str, int, float]) -> None:
    """Set a Houdini environment variable and save to ensure persistence.

    Args:
        var_name: Environment variable name
        var_value: Value to set, converted to string

    Notes:
        - Uses both hscript and Python methods to ensure compatibility
        - Saves the hip file to persist the environment change
        - Previous value is overwritten without warning

    Examples:
        >>> set_env_var("MY_TOOL_PATH", "/custom/path")
        >>> set_env_var("CACHE_SIZE", 1024)

    Warning:
        This function saves the hip file. Ensure all changes are committed
        before calling.

    Since: 1.0.0
    """
    str_value = str(var_value)
    hou.hscript(f"setenv {var_name}={str_value}")
    hou.putenv(var_name, str_value)
    hou.hipFile.save(None, False)