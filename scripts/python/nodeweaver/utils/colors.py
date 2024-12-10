"""Color manipulation and conversion utilities for Houdini.

This module provides functions for converting between different color formats
and managing node color palettes within Houdini. It handles hex colors, RGB floats,
and Houdini's native color representations.

Functions:
    hex_to_float_rgb: Convert hex color strings to RGB float values
    float_rgb_to_hex: Convert RGB float values to hex color strings
    color_selected_nodes: Apply colors to selected nodes
    validate_palette_file: Validate Houdini color palette files
    load_default_palette: Get Houdini's default color palette
"""
from typing import Tuple, List, Union
from pathlib import Path
import hou

def hex_to_float_rgb(hex_value: str) -> Tuple[float, float, float]:
    """Convert a hex color string to RGB float values.

    Args:
        hex_value: Hex color string (e.g. "FF0000" or "#FF0000")

    Returns:
        Tuple of RGB float values from 0-1

    Examples:
        >>> hex_to_float_rgb("#FF0000")
        (1.0, 0.0, 0.0)
        >>> hex_to_float_rgb("00FF00")
        (0.0, 1.0, 0.0)
    """
    hex_value = hex_value.lstrip("#")
    lv = len(hex_value)
    rgb = tuple(int(hex_value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return tuple(float(i)/256 for i in rgb)


def float_rgb_to_hex(red: float, green: float, blue: float) -> str:
    """Convert RGB float values to hex color string.

    Args:
        red: Red value (0-1)
        green: Green value (0-1)
        blue: Blue value (0-1)

    Returns:
        6-character hex color string without # prefix

    Examples:
        >>> float_rgb_to_hex(1.0, 0.0, 0.0)
        'ff0000'
        >>> float_rgb_to_hex(0.0, 1.0, 0.0)
        '00ff00'
    """
    red = int(red * 255)
    green = int(green * 255)
    blue = int(blue * 255)
    return f"{red:02x}{green:02x}{blue:02x}"


def color_selected_nodes(node:hou.Node) -> None:
    """Changes the color of the selected nodes with a color palette window.

    Opens a color picker dialog and applies the chosen color to selected nodes
    and an optional target node.

    Args:
        node (Optional[hou.Node]): Additional node to apply color to besides selection.
            If None, only selected nodes will be colored.

    Returns:
        None

    Raises:
        RuntimeError: If color application fails
        ValueError: If node is invalid

    Example:
        >>> change_node_color(hou.node('/obj/geo1'))  # Colors geo1 and selection
    """
    sel = list(hou.selectedNodes())+[node]
    color = (None, sel[0].color())[len(sel) > 0]
    color = hou.ui.selectColor(color)
    if len(sel) > 0 and color != None:
        print(f"The picked color is {color}\nNote: You need to disable the 'Color Correction' flag in the color picker (ramp in the top right) for the colors to be accurate.")
        for sel_node in sel:
            sel_node.setColor(color)


def validate_palette_file(file_path: Union[str, Path], importing: bool = True) -> bool:
    """Validate if a file is a valid Houdini color palette file.

    Args:
        file_path: Path to the palette file
        importing: Whether file is being imported (requires content)

    Returns:
        True if file is valid, False if invalid

    Notes:
        Valid palette files must:
        - Be named "opColorPalette.def"
        - Exist at the specified path
        - Contain content if importing=True

    Example:
        >>> validate_palette_file("path/to/opColorPalette.def")
        True
    """
    file_path = Path(file_path)
    if file_path.name != "opColorPalette.def":
        hou.ui.displayMessage("The selected file is not called opColorPalette.def, therefore it is not a Houdini node color palette file.")
        return False

    if not file_path.exists():
        hou.ui.displayMessage("The selected file does not exist. Use the 'Reset to Houdini Standard' button to populate the main list with the default colors.")
        return False

    if file_path.stat().st_size == 0 and not importing:
        hou.ui.displayMessage("The selected file is empty, so cannot import.")
        return False

    return True


def load_default_palette() -> List[Tuple[float, float, float]]:
    """Get Houdini's default 36 color palette.

    Returns:
        List of RGB float tuples representing default colors

    Note:
        The default palette includes white, black, grays, and various hues.
        Colors are returned as RGB float tuples with values from 0-1.
    """
    return [
        (1, 1, 1), (0.839, 0.839, 0.839), (0.6, 0.6, 0.6),
        (0.478, 0.478, 0.478), (0.306, 0.306, 0.306), (0, 0, 0),
        (0.384, 0.184, 0.329), (0.576, 0.208, 0.475),
        (0.89, 0.412, 0.761), (0.565, 0.494, 0.863),
        (0.451, 0.369, 0.796), (0.322, 0.259, 0.58),
        (0.38, 0.408, 0.553), (0.518, 0.561, 0.741),
        (0.71, 0.784, 1), (0.584, 0.776, 1),
        (0.29, 0.565, 0.886), (0.094, 0.369, 0.69),
        (0.188, 0.529, 0.459), (0.145, 0.667, 0.557),
        (0.616, 0.871, 0.769), (0.765, 1, 0.576),
        (0.475, 0.812, 0.204), (0.302, 0.525, 0.114),
        (1, 0.725, 0), (0.996, 0.933, 0),
        (1, 0.976, 0.666), (0.976, 0.78, 0.263),
        (0.71, 0.518, 0.004), (0.573, 0.353, 0),
        (0.624, 0.329, 0.396), (1, 0.529, 0.624),
        (0.996, 0.682, 0.682), (0.98, 0.275, 0.275),
        (1, 0, 0), (0.8, 0.016, 0.016)
    ]