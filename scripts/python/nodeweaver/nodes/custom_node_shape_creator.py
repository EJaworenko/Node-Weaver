"""Custom node shape creator for Houdini.

This module provides functionality for creating and managing custom node shapes,
including example network generation and shape data export. It handles:

- Creation of example node shape networks
- Export of shape data to JSON format
- Size and path management
- Group assignments and organization

The module uses a class-based approach to maintain state and manage the creation
process, with separate methods for different aspects of shape creation.

Classes:
    CustomNodeShapeCreator: Main shape creation functionality
"""

from typing import Dict, Any
from pathlib import Path
import hou
from nodeweaver.utils.files import write_json
from nodeweaver.utils.nodes import NetworkBuilder
from nodeweaver.core.exceptions import ValidationError

class CustomNodeShapeCreator:
    """Manages creation and export of custom node shapes.

    This class handles the creation of example networks and export of node
    shape data to JSON format.

    Attributes:
        node: The HDA node being managed
        builder: NetworkBuilder instance for creating examples

    Example:
        >>> creator = CustomNodeShapeCreator(node)
        >>> creator.create_example()
        >>> creator.export_shape_data()
    """

    def __init__(self, node: hou.Node):
        """Initialize with the HDA node.

        Args:
            node (hou.Node): The HDA node containing custom shape parameters.
                Must be a valid Digital Asset node.

        Raises:
            ValueError: If node is None or invalid
            TypeError: If node is not of type hou.Node
        """
        self.node = node
        self.builder = NetworkBuilder(node.parent())

    def create_example(self) -> None:
        """Create an example node shape network.

        Creates a complete network demonstrating shape creation techniques
        based on the selected example type.

        Notes:
            - Resets node parameters before creation
            - Handles different example types
            - Creates appropriate network structure
            - Sets up proper connections

        Example:
            >>> creator.create_example()  # Creates based on node's example parameter

        Raises:
            ValueError: If example index is invalid
        """
        example = self.node.evalParm("examples")

        if hou.ui.displayMessage(
            "Settings on this node will be overwritten when you create this example.\n"
            "Would you like to continue?",
            buttons=("Yes", "No")
        ) == 1:
            return

        # Reset node parameters
        for parm in self.node.parms():
            try:
                parm.revertToDefaults()
            except hou.PermissionError:
                continue

        # Map example index to template name
        templates = {
            0: "simple_clip_method",
            1: "complex_constructed_method",
            2: "honeycomb_trace_method"
        }

        template_name = templates.get(example)
        if not template_name:
            raise ValueError(f"Invalid example index: {example}")

        # Build network from template
        self.builder.build_from_template(template_name)
        self.update_path()
        self.update_size()

    def export_shape_data(self) -> None:
        """Export node shape data to JSON file.

        Extracts shape data from the current node setup and exports it
        in a format suitable for node shape definition.

        Notes:
            - Validates shape name and path
            - Generates shape data structure
            - Handles outline, flags, inputs/outputs
            - Creates proper JSON formatting

        Example:
            >>> creator.export_shape_data()

        Raises:
            ValidationError: If shape name not specified
        """
        def gen_list(attrib_name: str) -> list:
            """Generate list of point values from geometry attribute."""
            return [
                [float(x.strip()) for x in i.split(",")]
                for i in geo.stringListAttribValue(attrib_name)
            ]

        # Update path and validate
        self.update_path()
        path = Path(self.node.evalParm("path"))
        name = self.node.evalParm("shape_name")

        if not name:
            raise ValidationError("No shape name specified")

        # Generate shape data
        geo = self.node.node("JSON_OUT").geometry()
        data = {
            "name": name,
            "flags": {
                str(i): {"outline": gen_list(f"flag{i}_outline")}
                for i in range(4)
            },
            "outline": gen_list("outline"),
            "inputs": gen_list("inputs"),
            "outputs": gen_list("outputs"),
            "icon": gen_list("icon")
        }

        # Write data
        if write_json(path, data):
            hou.ui.displayMessage(
                f"Successfully wrote the '{name}' node shape to\n{path}"
            )

    def update_path(self) -> None:
        """Update the export path parameter and label.

        Updates the path parameter with the full normalized path and creates a
        truncated version for the display label if path is too long.

        Raises:
            RuntimeError: If path parameters cannot be updated
            ValueError: If directory or shape name is invalid
        """
        path_str = f'{self.node.evalParm("dir")}/{self.node.evalParm("shape_name")}.json'
        path_str = hou.text.normpath(hou.text.expandString(path_str))

        self.node.parm("path").set(path_str)

        # Truncate long paths in label
        if len(path_str) > 65:
            path_str = path_str[:25] + "....." + path_str[-45:]
        self.node.parm("lbl_path").set(path_str)

    def update_size(self) -> None:
        """Update the node shape size parameter and label.

        Updates the size parameter based on current width/height settings and
        refreshes the size display label.

        Raises:
            RuntimeError: If size parameters cannot be updated
            ValueError: If width or height values are invalid
        """
        if self.node.input(0):
            bounds = self.node.node("Set_groups_colors").geometry().boundingBox().sizevec()
            bounds = (round(bounds[0], 2), round(bounds[1], 2))

            self.node.parm("lbl_size").set(f"{bounds[0]} x {bounds[1]}")

            if self.node.evalParm("restrict_to_shape"):
                self.node.parm("icon_scale").set(
                    min(bounds[0], bounds[1], self.node.evalParm("icon_scale"))
                )

"""Callback functions for the custom node shape creator."""

def match_start(kwargs: Dict[str, Any]) -> None:
    """Match the curve end parameter to the start parameter.

    Synchronizes the end parameter value based on the start parameter when
    matching is enabled.

    Args:
        kwargs (Dict[str, Any]): Callback keyword arguments containing:
            - node: The HDA node instance
            - parm: The parameter being modified
            - parm_name: Name of the parameter

    Returns:
        None

    Raises:
        KeyError: If required kwargs are missing
    """
    node = kwargs["node"]
    curve_start = kwargs["parm"]
    curve_end = node.parm(kwargs["parm_name"].replace("start", "end"))
    match_toggle = node.parm(kwargs["parm_name"].replace("start", "end_match"))

    if match_toggle.eval():
        curve_end.set(1 - curve_start.eval())

def on_example_create(kwargs: Dict[str, Any]) -> None:
    """Create an example node shape network.

    Creates a demonstration network showing custom node shape usage.

    Args:
        kwargs (Dict[str, Any]): Callback keyword arguments containing:
            - node: The HDA node instance

    Returns:
        None

    Raises:
        RuntimeError: If example creation fails
    """
    creator = CustomNodeShapeCreator(kwargs["node"])
    creator.create_example()

def on_export_shape(kwargs: Dict[str, Any]) -> None:
    """Export node shape data to JSON.

    Saves the current node shape configuration to a JSON file.

    Args:
        kwargs (Dict[str, Any]): Callback keyword arguments containing:
            - node: The HDA node instance

    Returns:
        None

    Raises:
        IOError: If export fails
    """
    creator = CustomNodeShapeCreator(kwargs["node"])
    creator.export_shape_data()

def on_update_path(kwargs: Dict[str, Any]) -> None:
    """Update the export path parameter.

    Updates the path parameter and display label based on current settings.

    Args:
        kwargs (Dict[str, Any]): Callback keyword arguments containing:
            - node: The HDA node instance

    Returns:
        None

    Raises:
        RuntimeError: If path update fails
    """
    creator = CustomNodeShapeCreator(kwargs["node"])
    creator.update_path()

def on_update_size(kwargs: Dict[str, Any]) -> None:
    """Update the node shape size parameter.

    Updates size parameter and display label based on current dimensions.

    Args:
        kwargs (Dict[str, Any]): Callback keyword arguments containing:
            - node: The HDA node instance

    Returns:
        None

    Raises:
        RuntimeError: If size update fails
    """
    creator = CustomNodeShapeCreator(kwargs["node"])
    creator.update_size()