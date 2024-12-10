"""Utility decorators for NodeWeaver.

This module provides decorators used throughout the NodeWeaver package to enhance
functionality and development workflow. It includes decorators for module reloading,
Houdini update mode management, and other utility purposes.

Features:
    - Automatic module reloading for development
    - Temporary update mode modification
    - Performance optimization helpers
"""
from functools import wraps
from importlib import reload
import sys
from typing import Callable, Any
import hou

def reload_before_run(func: Callable) -> Callable:
    """Decorator that reloads the module containing the decorated function before execution.

    This decorator automatically reloads the module containing the decorated function
    before running it. This is useful during development when functions are called
    through Houdini callbacks or the Python shell.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function that reloads its own module before executing

    Examples:
        >>> @reload_before_run
        ... def my_function():
        ...     pass

        >>> # In a callback:
        >>> # from my_module import my_function; my_function()

    Notes:
        - Only reloads the specific module containing the decorated function
        - Does nothing if the module isn't found in sys.modules
        - Preserves the original function's metadata using functools.wraps

    Since: 1.0.0
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        module_name = func.__module__
        if module_name in sys.modules:
            reload(sys.modules[module_name])
        return func(*args, **kwargs)
    return wrapper


def pause_update_mode(func: Callable) -> Callable:
    """Temporarily set Houdini's update mode to Manual during function execution.

    This decorator pauses Houdini's cooking and viewport updates during the decorated
    function's execution by setting the update mode to Manual. The original update mode
    is restored after execution, even if the function raises an exception.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that executes with paused updates

    Examples:
        >>> @pause_update_mode
        ... def heavy_node_operation():
        ...     # Operations run with updates paused
        ...     pass

        >>> @pause_update_mode
        ... def batch_process_nodes(nodes):
        ...     for node in nodes:
        ...         # Each iteration runs without triggering updates
        ...         node.setColor((1, 0, 0))

    Notes:
        - Use this decorator for operations that would normally trigger many node
          cooks or viewport updates
        - The original update mode is always restored, even if the function raises
          an exception
        - This can significantly improve performance for batch operations
        - Updates are deferred until after the function completes

    Warning:
        Be cautious when using this with functions that rely on node cooking or
        viewport feedback during their execution, as these will be delayed until
        the function completes.

    Since: 1.0.0
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_mode = hou.updateModeSetting()
        try:
            hou.setUpdateMode(hou.updateMode.Manual)
            return func(*args, **kwargs)
        finally:
            hou.setUpdateMode(original_mode)
    return wrapper