"""Utility functions for inspecting and loading Houdini node shape files.

This module provides functionality to read, parse, and apply node shape data
from JSON files. It handles:

- Loading shape files
- Applying shape data to nodes
- Generating shape statistics
- Parameter management

Functions:
    clear_parameters: Reset shape parameters
    generate_statistics: Calculate shape bounds
    fill_node_shape_parameters: Apply shape data to node
"""

from typing import Dict, Any
import hou
from nodeweaver.utils.files import read_json


def clear_parameters(kwargs: Dict[str, Any]) -> None:
    """Clear node shape parameters to default values.

    Resets all node shape parameters back to their original default values,
    including size, path, and curve parameters.

    Args:
        kwargs (Dict[str, Any]): Node callback kwargs containing:
            - node: The HDA node instance whose parameters should be cleared

    Returns:
        None

    Raises:
        KeyError: If required kwargs are missing
        RuntimeError: If parameters cannot be reset

    Example:
        >>> on_clear_parameters({'node': hou.node('/obj/myHDA')})
    """
    node = kwargs["node"]
    for parm_name in ["mparm_outline", "mparm_inputs", "mparm_outputs"]:
        node.parm(parm_name).set(0)

    for i in range(4):
        node.parm(f"mparm_flag{i}").set(0)

    node.parmTuple("icon_min").set((0, 0))
    node.parmTuple("icon_max").set((0, 0))


def generate_statistics(kwargs: Dict[str, Any]) -> None:
    """Calculate and display shape element bounds statistics.

    Analyzes the geometric bounds of various shape elements and updates
    label parameters with the information.

    Args:
        kwargs: Node callback kwargs containing node to analyze

    Notes:
        - Calculates bounds for shapes, inputs/outputs, icons
        - Updates label parameters with formatted information
        - Uses node's digit precision setting
        - Handles different geometry types appropriately

    Example:
        >>> generate_statistics({"node": shape_node})
    """
    node = kwargs["node"]
    digits = node.evalParm("digits")
    geometries = {
        "lbl_shape": node.node("COMBINED_SHAPES").geometry(),
        "lbl_inout": node.node("COMBINED_INOUT").geometry(),
        "lbl_icon": node.node("ICON").geometry(),
        "lbl_overall": node.node("OVERALL").geometry()
    }

    for lbl_name, geo in geometries.items():
        bbox = geo.boundingBox()
        min_vec = bbox.minvec()
        max_vec = bbox.maxvec()
        size_vec = bbox.sizevec()
        center = bbox.center()

        stats = (
            f"X: {round(min_vec[0], digits)} to {round(max_vec[0], digits)}  |  "
            f"Y: {round(min_vec[1], digits)} to {round(max_vec[1], digits)}  |  "
            f"Size: {round(size_vec[0], digits)} x {round(size_vec[1], digits)}  |  "
            f"Center: {round(center[0], digits)} x {round(center[1], digits)}"
        )
        node.parm(lbl_name).set(stats)


def fill_node_shape_parameters(kwargs: Dict[str, Any]) -> None:
    """Fill node parameters based on JSON shape file contents.

    Args:
        kwargs: Node callback kwargs containing target node

    Notes:
        - Clears existing parameters first
        - Handles flags, outline, inputs/outputs
        - Sets proper node name and comment
        - Maintains proper parameter organization
        - Updates statistics after loading

    Example:
        >>> fill_node_shape_parameters({"node": node})

    Raises:
        ValueError: If shape file is invalid or missing required data
    """
    node = kwargs["node"]
    data = read_json(node.evalParm("file"))
    if not data:
        return

    clear_parameters(kwargs)

    for key, value in data.items():
        if key == "name":
            node.setComment(f"Loaded: {value}")
            node.setGenericFlag(hou.nodeFlag.DisplayComment, True)

        elif key == "flags":
            for num, flag_data in value.items():
                node.parm(f"mparm_flag{num}").set(len(flag_data["outline"]))
                for i, pos in enumerate(flag_data["outline"]):
                    node.parmTuple(f"flag{num}_pos{i}").set(pos)

        elif key == "outline":
            node.parm("mparm_outline").set(len(value))
            for i, pos in enumerate(value):
                node.parmTuple(f"outline_pos{i}").set(pos)

        elif key in ["inputs", "outputs"]:
            node.parm(f"mparm_{key}").set(len(value))
            for i, pos in enumerate(value):
                node.parmTuple(f"{key}_pos{i}").set((pos[0], pos[1]))
                node.parm(f"{key}_angle{i}").set(pos[2])

        elif key == "icon":
            node.parmTuple("icon_min").set(value[0])
            node.parmTuple("icon_max").set(value[1])

    generate_statistics(kwargs)