"""Public interface for inspecting scripts and callbacks in Houdini nodes.

This module provides functionality for searching, analyzing and extracting
scripts from nodes, including callbacks, expressions, menu scripts, and
conditionals.

Example:
    >>> inspector = ScriptInspector()
    >>> inspector.print_scripts_in_selected_nodes()

Classes:
    ScriptInspector: Main script inspection functionality
"""

from typing import Optional, List, Dict
import hou
from ._impl import _script_inspector
from nodeweaver.utils.decorators import reload_before_run

class ScriptInspector:
    """Inspects and analyzes scripts and callbacks in Houdini nodes.

    Provides methods to search, analyze and extract scripts from node parameters,
    including callbacks, expressions, menu scripts, and conditionals.

    Attributes:
        search_mode: Current search mode (None until first search)
        search_str: Current search string (None until first search)

    Example:
        >>> inspector = ScriptInspector()
        >>> scripts = inspector.search_scripts(node)
        >>> for script in scripts:
        ...     print(f"{script['type']}: {script['script']}")
    """

    def __init__(self) -> None:
        """Initialize the ScriptInspector.

        Creates a new ScriptInspector instance with default settings for analyzing
        Houdini scripts.
        """
        self.search_mode: Optional[int] = None
        self.search_str: Optional[str] = None

    def search_scripts(self, node: hou.Node) -> List[Dict[str, str]]:
        """Search for scripts in a node's parameters.

        Args:
            node: Node to search

        Returns:
            List of found scripts with their metadata:
            - parameter: Parameter name
            - type: Script type (callback, expression, etc.)
            - script: Formatted script content

        Raises:
            ValueError: If node is None

        Example:
            >>> scripts = inspector.search_scripts(node)
            >>> for script in scripts:
            ...     print(f"{script['parameter']}: {script['script']}")
        """
        if not node:
            raise ValueError("Node cannot be None")

        # Get search parameters if not already set
        if self.search_mode is None:
            self.search_mode, self.search_str = _script_inspector.prompt_search_params()
            if self.search_mode is None:
                return []

        return _script_inspector.find_scripts(node, self.search_mode, self.search_str)

    @reload_before_run
    def print_scripts_in_selected_nodes(self) -> None:
        """Search and print scripts from all selected nodes.

        Finds all script-type parameters in the selected nodes and prints their contents,
        organized by node and parameter name.

        Raises:
            RuntimeError: If no nodes are selected
            ValueError: If selected nodes contain no script parameters

        Example:
            >>> inspector = ScriptInspector()
            >>> inspector.search_selected()  # Prints all scripts in selected nodes
        """
        sel = hou.selectedNodes()
        if not sel:
            hou.ui.displayMessage("Please select a node first.",
                                severity=hou.severityType.Error)
            return

        for node in sel:
            scripts = self.search_scripts(node)

            if scripts:
                print(f"\nScripts found in {node.path()}:")
                print("-" * 40)
                for script in scripts:
                    print(f"Parameter: {script['parameter']}")
                    print(script['script'])
                    print("-" * 40)

    @staticmethod
    def format_script(label: str, script: str, indent: int = 4) -> str:
        """Format a script with proper indentation and wrapping.

        Takes raw script content and formats it with consistent indentation, line wrapping
        and optional label prefix.

        Args:
            label (str): Script type label to prefix (e.g. 'Python', 'VEX')
            script (str): The raw script content to format
            indent (int, optional): Number of spaces for indentation. Defaults to 4.

        Returns:
            str: The formatted script string with proper indentation and wrapping

        Raises:
            ValueError: If script is None or empty
            TypeError: If indent is not an integer

        Example:
            >>> inspector = ScriptInspector()
            >>> formatted = inspector.format_script("Python", "def foo():\\n    pass", 4)
        """
        return _script_inspector.format_script(label, script, indent)