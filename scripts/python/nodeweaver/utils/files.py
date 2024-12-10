"""File operation utilities for NodeWeaver.

This module provides utilities for reading and writing files, with a focus
on JSON handling and validation. It includes functions for safe file operations
with proper error handling and user feedback.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import json
import hou

def read_json(path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Read and validate a JSON file.

    Args:
        path: Path to JSON file as string or Path object

    Returns:
        Dictionary of JSON contents if valid, None if invalid

    Notes:
        - Validates file existence and .json extension
        - Checks for non-empty content
        - Prints warning messages for invalid files

    Example:
        >>> data = read_json("config/settings.json")
        >>> if data:
        ...     print("Settings loaded")

    Since: 1.0.0
    """
    if isinstance(path, str):
        path = Path(path)

    if not path.exists() or path.suffix != ".json":
        print(f"JSON file either does not exist at {path} or doesn't end with .json. File not read.")
        return None

    if path.stat().st_size == 0:
        print(f"JSON file at {path} is empty. File not read.")
        return None

    try:
        with open(path) as json_file:
            return json.load(json_file)
    except json.JSONDecodeError:
        print(f"Invalid JSON content in {path}")
        return None


def write_json(path: Union[str, Path],
                data: Dict[str, Any],
                indent: int = 2,
                create_dirs: bool = True,
                overwrite: bool = False) -> bool:
    """Write a dictionary to a JSON file.

    Args:
        path: Path to JSON file as string or Path object
        data: Dictionary to write to file
        indent: Number of spaces for JSON indentation
        create_dirs: Whether to create parent directories if they don't exist
        overwrite: Whether to overwrite existing file without prompting

    Returns:
        True if write successful, False otherwise

    Examples:
        >>> data = {"setting": "value"}
        >>> write_json("config/new.json", data, create_dirs=True)
        True

    Notes:
        - Creates parent directories if create_dirs=True
        - Prompts for confirmation before overwriting unless overwrite=True
        - Uses consistent indentation for readability

    Since: 1.0.0
    """
    if isinstance(path, str):
        path = Path(path)

    if path.exists() and not overwrite:
        response = hou.ui.displayMessage(
            f"The file at\n{path}\nalready exists, would you like to overwrite it?",
            buttons=("Yes", "No")
        )
        if response == 1:
            return False

    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=indent)
        return True

    except OSError as e:
        hou.ui.displayMessage(f"Error writing JSON file: {str(e)}")
        return False