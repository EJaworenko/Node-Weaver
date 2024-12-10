"""Utility functions for Houdini action button callbacks.

This module provides functions commonly used in action button callbacks,
particularly focusing on file and path operations. It handles:

- Path opening and validation
- Directory creation
- File browser integration
- Path expansion and normalization
"""

from typing import Any, Dict, Union
from pathlib import Path
import hou

def open_path(kwargs: Dict[str, Any], parm_name: Union[str, hou.Parm],
              path_instead: bool = False) -> None:
    """Open a path in the system file browser.

    Args:
        kwargs: Node callback dictionary
        parm_name: Parameter name or parameter containing path
        path_instead: Whether to use parm_name as direct path

    Notes:
        - Handles both parameters and direct paths
        - Creates directories if needed
        - Validates paths before opening
        - Handles both files and directories
        - Expands Houdini variables

    Example:
        >>> # From parameter
        >>> open_path(kwargs, "file_path")

        >>> # Direct path
        >>> open_path(kwargs, "/path/to/file", path_instead=True)

    Since: 1.0.0
    """
    if path_instead:
        dir_path = parm_name
    else:
        if isinstance(parm_name, str):
            dir_path = kwargs['node'].evalParm(parm_name)
        elif isinstance(parm_name, hou.Parm):
            template = parm_name.parmTemplate()
            if template.type() == hou.parmTemplateType.String:
                dir_path = parm_name.eval()
            else:
                hou.ui.displayMessage(
                    "The supplied parm is not a string type.")
                return
        else:
            hou.ui.displayMessage(text=f"Invalid parm name supplied: {parm_name}. Action cancelled.",
                                    severity=hou.severityType.ImportantMessage)
            return
    dir_path = hou.text.expandString(dir_path)

    if dir_path != "":
        # If the directory exists, check if it is a file or folder and open it in the file browser.
        dir_path = Path(dir_path)
        if dir_path.exists():
            if dir_path.is_dir() is False:
                dir_path = dir_path.parent
            if str(dir_path)[-1] != '/':
                dir_path = str(dir_path) + '/'
            hou.ui.showInFileBrowser(dir_path)
            return
        else:
            # If the directory doesn't exist, check if it's a file in a second way.
            if dir_path.name != dir_path.stem:
                dir_path = dir_path.parent
                if dir_path.exists():
                    if str(dir_path)[-1] != '/':
                        dir_path = str(dir_path) + '/'
                    hou.ui.showInFileBrowser(dir_path)
                    return
            # Check if the directory even appears to be a path.
            if str(dir_path).find("/") < 0 and str(dir_path).find("\\") < 0:
                hou.ui.displayMessage(text=f"Invalid path supplied: {dir_path}. Action cancelled.",
                                        severity=hou.severityType.ImportantMessage)
                return
            # If the directory doesn't exist, ask if the user wants to create it.
            if hou.ui.displayMessage(
                    f"The following directory does not exist, would you like to create it?\n{dir_path}",
                    ("Yes", "No")) == 0:
                dir_path.mkdir(parents=True, exist_ok=True)
                hou.ui.showInFileBrowser(str(dir_path))
                return
    else:
        hou.ui.displayMessage(text="Directory not defined, could not open.",
                                severity=hou.severityType.ImportantMessage)