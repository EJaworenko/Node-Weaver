"""User interface utilities for NodeWeaver.

This module provides utilities for managing Houdini's user interface elements
and interactions. It focuses on providing consistent user feedback and
handling common UI operations.

Functions:
    warn_if_manual_mode: Display warning if in manual update mode
"""

import textwrap
import hou

def warn_if_manual_mode(mode: str = "simple", custom: str = "") -> bool:
    """Check if Houdini is in manual mode and warn the user if it is.

    Args:
        mode: Warning mode:
            "simple": Basic warning
            "errorfull": Full error message
            "errorpartial": Custom error with manual mode note
        custom: Custom message to prepend to warning

    Returns:
        True if warning was displayed (manual mode active)

    Notes:
        - Checks current update mode setting
        - Formats message appropriately
        - Handles different warning types
        - Returns whether warning was shown

    Example:
        >>> if warn_if_manual_mode("errorfull"):
        ...     return  # Operation cancelled due to manual mode

    Since: 1.0.0
    """
    dialogs = {
        "simple": "Houdini's update mode is set to manual. Some operations may not work as expected. Please switch to auto-update mode by clicking the 'Auto Update' button in the bottom right corner of the Houdini window.",
        "errorfull": "This operation failed. It may be because the current update mode is set to manual. Please switch to auto-update mode by clicking the 'Auto Update' button in the bottom right corner of the Houdini window.",
        "errorpartial": "It may be because the current update mode is set to manual. Please switch to auto-update mode by clicking the 'Auto Update' button in the bottom right corner of the Houdini window.",
    }
    dialog = dialogs.get(mode, dialogs['simple'])
    if hou.updateModeSetting() == hou.updateMode.Manual:
        hou.ui.displayMessage(textwrap.fill(custom + dialog), ("OK",))
        return True
    return False


def reload_node_shapes() -> None:
    """Reload all node shapes in the current Network Editor pane.

    Forces a refresh of all node shapes, in the Network Editor. This is
    useful after modifying node shapes as Node Weaver does.
    """
    hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).reloadNodeShapes()