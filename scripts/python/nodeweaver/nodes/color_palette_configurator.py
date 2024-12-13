"""Color palette configuration node implementation for Houdini.

This module provides functionality for creating, modifying, and managing color
palettes in Houdini through a specialized node interface. It handles:

- Importing and exporting Houdini color palette files
- Converting between hex and RGB color formats
- Gradient-based color generation including cosine gradients
- Text-based color parsing and extraction
- Screen color sampling
- Default Houdini color palette management

The module uses a singleton pattern to ensure consistent state management per node
instance, with separate managers for gradient and text-based operations.

Classes:
    ColorPaletteConfigurator: Core color palette management
    GradientManager: Gradient-based color operations
    TextColorManager: Text-based color parsing and conversion

Note:
    This node implementation relies on the nodeweaver.utils.colors module for
    core color manipulation functions and nodeweaver.config for gradient presets.
"""

from typing import Optional, Dict, List, Tuple, ClassVar
from pathlib import Path
import math
import json
import hou
from labsopui import screensampling
from nodeweaver.utils import colors as color_util


class ColorPaletteConfigurator:
    """Manages color palette configuration node functionality.

    This class handles importing, exporting and modifying color palettes
    for use in Houdini's interface. It maintains a singleton instance per node
    to ensure consistent state.

    Attributes:
        node: HDA node this instance manages

    Example:
        >>> configurator = ColorPaletteConfigurator.get_instance(node)
        >>> configurator.import_colors()

    Note:
        Use get_instance() instead of direct instantiation to maintain
        singleton pattern.
    """
    _instances: ClassVar[Dict[str, 'ColorPaletteConfigurator']] = {}

    @classmethod
    def get_instance(cls, node: hou.Node) -> 'ColorPaletteConfigurator':
        """Get or create configurator instance for a node.

        Args:
            node: HDA node requiring configurator

        Returns:
            Singleton instance for the node

        Example:
            >>> configurator = ColorPaletteConfigurator.get_instance(node)
            >>> configurator.reset_colors()
        """
        node_path = node.path()
        if node_path not in cls._instances:
            cls._instances[node_path] = cls(node)
        return cls._instances[node_path]

    def __init__(self, node: hou.Node):
        """Initialize with the node instance.

        Args:
            node (hou.Node): The Houdini node containing color palette parameters.
                Must be a valid node with color parameters.

        Raises:
            ValueError: If node is None or invalid
            TypeError: If node is not of type hou.Node
        """
        self.node = node

    # Core color palette methods

    def import_colors(self) -> None:
        """Import colors from a palette file.

        Reads colors from a Houdini color palette file and creates corresponding
        entries in the node's color list.

        Notes:
            - Validates file format and existence
            - Prompts for confirmation if colors exist
            - Converts color formats automatically
            - Updates both RGB and hex representations

        Example:
            >>> configurator.import_colors()  # Imports from node's file parameter
        """
        mparm = self.node.parm("colors")

        if mparm.eval():
            if hou.ui.displayMessage("Colors appear to exist in the main list already. Are you sure you'd like to overwrite?",
                                   buttons=("Yes", "No")) == 1:
                return

        file_path = self.node.parm("file").evalAsString()
        if not color_util.validate_palette_file(file_path):
            return

        mparm.set(0)
        with open(file_path, "r") as file:
            lines = file.read().splitlines()
            count = lines.pop(0)
            lines.reverse()
            lines = [line for line in lines if line]

            for i, line in enumerate(lines):
                color = line.split(" ")
                color.pop(0)
                mparm.insertMultiParmInstance(i)
                self.node.parmTuple(f"rgb{i+1}").set(color)
                self.node.parm(f"hex{i+1}").set(
                    color_util.float_rgb_to_hex(float(color[0]), float(color[1]), float(color[2]))
                )

    def export_colors(self) -> None:
        """Export colors to a palette file.

        Saves the current color palette configuration to a file in the specified format.

        Returns:
            bool: True if export successful, False otherwise

        Raises:
            ValueError: If filepath is invalid or format_type not supported
            IOError: If file cannot be written

        Example:
            >>> configurator = ColorPaletteConfigurator(node)
            >>> success = configurator.export_palette('C:/colors.json')
        """
        if hou.ui.displayMessage("Would you like export these colors?",
                               buttons=("Yes", "No")) == 1:
            return

        file_path = self.node.parm("file").evalAsString()
        if not color_util.validate_palette_file(file_path, importing=False):
            return

        mparm = self.node.parm("colors")
        lines = []

        for i in range(mparm.evalAsInt()):
            line = "D3"
            color = self.node.parmTuple(f"rgb{i+1}").evalAsFloats()
            for j in color:
                line += f" {j:.3}"
            lines.append(line)

        lines.reverse()
        lines.insert(0, mparm.evalAsString())
        lines_s = "\n".join(lines)

        with open(file_path, "w+") as file:
            file.write(lines_s)

        hou.ui.displayMessage("Colors successfully exported.")

    def reset_colors(self) -> None:
        """Reset colors to Houdini defaults.

        Resets all color parameters to their original Houdini default values, discarding
        any custom color palette settings.

        Raises:
            RuntimeError: If default values cannot be restored
            ValueError: If color parameters are invalid

        Example:
            >>> configurator = ColorPaletteConfigurator(node)
            >>> configurator.reset_colors()  # Restores default Houdini colors
        """
        if hou.ui.displayMessage("Would you like to reset the colors to the Houdini Defaults?",
                               buttons=("Yes", "No")) == 1:
            return

        default_colors = color_util.load_default_palette()
        default_colors.reverse()
        mparm = self.node.parm("colors")
        mparm.set(0)

        for i, color in enumerate(default_colors):
            mparm.insertMultiParmInstance(i)
            self.node.parmTuple(f"rgb{i+1}").set(color)
            self.node.parm(f"hex{i+1}").set(
                color_util.float_rgb_to_hex(color[0], color[1], color[2])
            )

    def update_hex(self, kwargs: Dict) -> None:
        """Update hex value when RGB changed.

        Callback method that updates the hex color parameter whenever RGB values
        are modified by the user.

        Raises:
            ValueError: If RGB values are invalid
            RuntimeError: If hex parameter update fails

        Example:
            >>> # Automatically called when RGB parameters change
            >>> # node.parm('r').set(255)  # Triggers hex update
        """
        value = self.node.parmTuple(kwargs["script_parm"]).evalAsFloats()
        hex = color_util.float_rgb_to_hex(value[0], value[1], value[2])
        self.node.parm(f"hex{kwargs['script_multiparm_index']}").set(hex)

    def update_rgb(self, kwargs: Dict) -> None:
        """Update RGB values when hex changed.

        Callback method that updates the RGB color parameters whenever the hex color
        value is modified by the user.

        Raises:
            ValueError: If hex value is invalid
            RuntimeError: If RGB parameter updates fail

        Example:
            >>> # Automatically called when hex parameter changes
            >>> # node.parm('hex').set('#FF0000')  # Triggers RGB update
        """
        hex = color_util.hex_to_float_rgb(kwargs["script_value0"])
        self.node.parmTuple(f"rgb{kwargs['script_multiparm_index']}").set(hex)


class GradientManager:
    """Manages gradient-based color operations for the color palette configurator.

    Handles creation, sampling, and management of color gradients including
    cosine-based gradient generation.

    Example:
        >>> manager = GradientManager.get_instance(node)
        >>> manager.create_cosine_gradient()

    Note:
        Use get_instance() instead of direct instantiation.
    """
    _instances: ClassVar[Dict[str, 'GradientManager']] = {}

    @classmethod
    def get_instance(cls, node: hou.Node) -> 'GradientManager':
        """Get or create gradient manager instance for a node.

        Args:
            node (hou.Node): The Houdini node to manage gradients for.

        Returns:
            GradientManager: Instance associated with the node.

        Raises:
            TypeError: If node is not a hou.Node instance.
        """
        node_path = node.path()
        if node_path not in cls._instances:
            cls._instances[node_path] = cls(node)
        return cls._instances[node_path]

    def __init__(self, node: hou.Node):
        """Initialize with the node instance.

        Args:
            node (hou.Node): The Houdini node containing gradient parameters.

        Raises:
            ValueError: If node is None or invalid.
        """
        self.node = node

    def sample_gradient(self, kwargs: Dict, index: int = -1) -> None:
        """Sample a color from the defined gradient.

        Args:
            kwargs (Dict): Parameter kwargs from callback.
            index (int, optional): Specific index to sample. Defaults to -1 for current.

        Raises:
            ValueError: If gradient parameters are invalid.
        """
        ramp = self.node.parm("sample_grad").eval()
        i = kwargs['script_multiparm_index'] if index == -1 else index
        parm = self.node.parm(f"grad_pos{i}").eval()
        sample = ramp.lookup(parm)
        self.node.parmTuple(f"grad_rgb{i}").set(sample)

    def reset_gradient_samples(self, kwargs: Dict) -> None:
        """Reset colors on all gradient samples.

        Args:
            kwargs (Dict): Parameter kwargs from callback.

        Raises:
            RuntimeError: If gradient reset fails.
        """
        for i in range(self.node.parm("grads").eval()):
            self.sample_gradient(kwargs, i+1)

    def add_gradient_samples(self) -> None:
        """Add gradient samples to the main color list.

        Includes the option to delete samples from the gradient multiparm afterwards.

        Raises:
            RuntimeError: If sample addition fails.
            ValueError: If color parameters are invalid.
        """
        colors = self.node.parm("colors")
        tog_top = self.node.evalParm("tog_grad_top")

        for i in range(self.node.parm("grads").eval()):
            if self.node.parm(f"tog_grad{i+1}").eval():
                color = self.node.parmTuple(f"grad_rgb{i+1}").eval()
                iter = [colors.eval(), 0][tog_top]
                colors.insertMultiParmInstance(iter)
                self.node.parmTuple(f"rgb{iter+1}").set(color)
                self.node.parm(f"hex{iter+1}").set(
                    color_util.float_rgb_to_hex(float(color[0]), float(color[1]), float(color[2]))
                )

        if self.node.parm("tog_del_grad").eval():
            self.node.parm("grads").set(0)

        hou.ui.displayMessage("Colors successfully added to main list.")

    def create_auto_samples(self) -> None:
        """Create automatically spaced gradient samples.

        Creates evenly spaced samples along the gradient, optionally replacing
        existing samples.

        Raises:
            RuntimeError: If auto sample creation fails.
            ValueError: If sample count is invalid.
        """
        if self.node.parm("grads").eval() > 0:
            if hou.ui.displayMessage("Replace gradient samples with automatically spaced ones?",
                                   buttons=("Yes", "No")) == 1:
                return

        total = self.node.parm("grad_auto_sample").eval()
        samples = self.node.parm("grads")
        samples.set(0)

        for i in range(total):
            samples.insertMultiParmInstance(i)
            frac = float(i)/float(total-1)
            self.node.parm(f"grad_pos{i+1}").set(frac)
            self.sample_gradient({"script_multiparm_index":-1}, i+1)

    def create_cosine_gradient(self) -> None:
        """Create a cosine-based color gradient.

        Generates a gradient using cosine functions with configurable
        parameters for each color channel.

        Notes:
            - Uses separate cosine functions for R, G, B channels
            - Maintains smooth color transitions
            - Automatically updates gradient samples

        Example:
            >>> manager.create_cosine_gradient()
        """
        def calc_val(t: float) -> Tuple[float, float, float]:
            color = []
            for i in ["r", "g", "b"]:
                color.append(
                    self.node.evalParm(f"grad_a{i}") +
                    self.node.evalParm(f"grad_b{i}") *
                    math.cos((math.pi*2)*(self.node.evalParm(f"grad_c{i}")*t +
                                        self.node.evalParm(f"grad_d{i}")))
                )
            return tuple(color)

        count = 20
        basis, keys, values = [], [], []
        lin = hou.rampBasis.Linear

        for i in range(count):
            frac = float(i)/float(count-1)
            basis.append(lin)
            keys.append(frac)
            values.append(calc_val(frac))

        ramp = hou.Ramp(basis, keys, values)
        self.node.parm("sample_grad").set(ramp)
        self.reset_gradient_samples({"script_multiparm_index":-1})

    def apply_cosine_preset(self) -> None:
        """Apply a predefined cosine gradient preset.

        Applies a preset gradient using cosine interpolation between colors, creating
        smooth transitions between complementary colors.

        Raises:
            RuntimeError: If gradient preset cannot be applied
            ValueError: If gradient parameters are invalid

        Example:
            >>> manager = GradientManager.get_instance(node)
            >>> manager.apply_cosine_preset()  # Applies cosine gradient
        """
        config_path = Path(__file__).parent.parent / "config/gradients/gradient_presets.json"
        with open(config_path, encoding='utf-8') as f:
            presets = json.load(f)

        preset_name = self.node.parm("cosine_presets").menuItems()[
            self.node.parm("cosine_presets").eval()
        ]

        if preset_name in presets:
            preset = presets[preset_name]
            for i, component in enumerate(['a', 'b', 'c', 'd']):
                self.node.parmTuple(f"grad_{component}").set(preset[i])

        self.create_cosine_gradient()
        self.node.parm("cosine_presets").set(0)


def sample_screen_color(kwargs: Dict, ramp_parm_name: str) -> None:
    """
    Sample a color from the screen using a custom python state from SideFX Labs.
    The sampled color is applied to the parameter specified in the kwargs.

    Args:
        kwargs: Node callback kwargs dictionary containing 'parms' key
               that specifies target parameters to receive the color value

    Note:
        This is a wrapper around screensampling.sample_ramp_color() that
        handles the parameter formatting required by the underlying function.
    """
    screensampling.sample_ramp_color([kwargs['node'].parm(ramp_parm_name)])


class TextColorManager:
    """Manages text-based color operations for the color palette configurator.

    A class that handles text input parsing and color extraction for the color palette
    configurator, supporting different text formats and gradient generation.

    Attributes:
        node (hou.Node): The Houdini node containing text and color parameters
        _instances (Dict[str, TextColorManager]): Class-level dictionary of instances

    Methods:
        get_instance: Get or create manager instance for a node
        extract_text_colors: Parse text input for color values
        add_text_samples: Add extracted colors to main palette
        add_text_gradient: Create gradient from text colors

    Example:
        >>> node = hou.node('/obj/palette1')
        >>> manager = TextColorManager.get_instance(node)
        >>> manager.extract_text_colors()
    """
    _instances: ClassVar[Dict[str, 'TextColorManager']] = {}

    @classmethod
    def get_instance(cls, node: hou.Node) -> 'TextColorManager':
        """Get or create text color manager instance for a node.

        Args:
            node (hou.Node): The Houdini node to manage text colors for

        Returns:
            TextColorManager: Instance associated with the node

        Raises:
            TypeError: If node is not a hou.Node instance
        """
        node_path = node.path()
        if node_path not in cls._instances:
            cls._instances[node_path] = cls(node)
        return cls._instances[node_path]

    def __init__(self, node: hou.Node):
        self.node = node

    def extract_text_colors(self, delete_lines: bool = False) -> Tuple[int, List[str], str]:
        """Extract color values from text input.

        Parses text input for hex color values in different formats based on mode.

        Args:
            delete_lines (bool, optional): Whether to remove color lines from text.
                Defaults to False.

        Returns:
            Tuple[int, List[str], str]: Contains:
                - Number of colors found
                - List of extracted hex color values
                - Updated text with colors optionally removed

        Raises:
            ValueError: If text input is invalid
        """
        lines = self.node.evalParm("text").splitlines()
        mode = self.node.evalParm("text_mode")
        delete = self.node.evalParm("tog_del_text")
        colors = []
        new_text = []
        count = 0

        for line in lines:
            found = -1
            # Hex color
            if mode == 0 and (len(line) == 7 and line.startswith("#") or len(line) == 6):
                found = 1
                color = line.replace("#", "")
            # Adobe CSS color
            elif mode == 1 and line.find("hex { color:") != -1:
                found = line.find("hex { color:") + 14
                color = line[found:found + 6]

            if found != -1 and len(color) == 6:
                count += 1
                colors.append(color)
                if delete == 0 and delete_lines is True or delete_lines is False:
                    new_text.append(line)
            else:
                new_text.append(line)

        return count, colors, "\n".join(new_text)

    def add_text_samples(self) -> None:
        """Add text-based colors to the main color list.

        Extracts colors from text input and adds them to the main color parameter list,
        with options for positioning and text cleanup.

        Raises:
            RuntimeError: If color addition fails
        """
        if hou.ui.displayMessage("Add text-based colors to the main color list?", buttons=("Yes", "No")) == 1:
            return

        top = self.node.evalParm("tog_text_top")
        delete = self.node.evalParm("tog_del_text")
        count, text_colors, new_text = self.extract_text_colors(delete_lines=True)
        colors_parm = self.node.parm("colors")

        for color in text_colors:
            iter = [colors_parm.eval(), 0][top]
            colors_parm.insertMultiParmInstance(iter)
            self.node.parmTuple(f"rgb{iter+1}").set(color_util.hex_to_float_rgb(color))
            self.node.parm(f"hex{iter+1}").set(color)

        if count:
            self.node.parm("text").set(new_text)
            hou.ui.displayMessage(f"{count} colors added to the main color list.")
        else:
            hou.ui.displayMessage("No colors found, no colors added.")

    def add_text_gradient(self) -> None:
        """Create a gradient from text-based colors.

        Creates a gradient ramp using colors extracted from text input,
        with linear interpolation between colors.

        Raises:
            RuntimeError: If gradient creation fails
            ValueError: If no valid colors found in text
        """
        if hou.ui.displayMessage(
                "Create gradient from listed colors?"+
                "\nNote: does not delete them from this tab.", buttons=("Yes", "No")) == 1:
            return

        count, text_colors, _ = self.extract_text_colors(delete_lines=True)
        if not count:
            return

        basis = [hou.rampBasis.Linear] * count
        keys = [(float(1)/(count-1))*i for i in range(count)]
        values = [color_util.hex_to_float_rgb(color) for color in text_colors]

        ramp = hou.Ramp(basis, keys, values)
        self.node.parm("sample_grad").set(ramp)
        hou.ui.displayMessage("Check Gradient-Based tab for created gradient.")