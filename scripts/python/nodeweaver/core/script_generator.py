"""Public interface for generating Houdini scripts.

This module provides high-level functionality for generating menu scripts,
action button scripts, and managing script templates in Houdini Digital Assets.
It abstracts away the implementation details while providing a clean,
type-safe API.

Example:
    >>> generator = ScriptGenerator.create("menu")
    >>> script = generator.generate_script(
    ...     category="group_selection",
    ...     name="single_group_type",
    ...     options={"option1": "hou.geometryType.Points"}
    ... )

Classes:
    ScriptGenerator: High-level script generation interface
    HDAScriptManager: Script generation in HDAs
"""

from typing import Dict, List, Union, Optional, Literal
from pathlib import Path
import hou
from nodeweaver.core._impl import _script_generator
from nodeweaver.core.exceptions import ValidationError, ConfigurationError

ScriptType = Literal["menu", "action"]

class ScriptGenerator:
    """High-level interface for script generation.

    This class provides methods to generate Houdini scripts from templates
    while handling configuration loading and validation.

    Example:
        >>> generator = ScriptGenerator.create('menu')
        >>> script = generator.generate_script('groups', 'by_type', {
        ...     'type': 'points'
        ... })
    """

    @classmethod
    def create(cls, script_type: ScriptType,
                config_path: Optional[Path] = None) -> 'ScriptGenerator':
        """Create a script generator of the specified type.

        Args:
            script_type: Type of scripts to generate ("menu" or "action")
            config_path: Optional custom path to config file

        Returns:
            Configured script generator

        Raises:
            ValueError: If script_type is invalid
            ConfigurationError: If config loading fails

        Example:
            >>> generator = ScriptGenerator.create('menu')
            >>> generator.generate_script(...)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config/script_generator/default.json"

        generator_cls = {
            "menu": _script_generator.MenuScriptGenerator,
            "action": _script_generator.ActionButtonGenerator
        }.get(script_type)

        if not generator_cls:
            raise ValueError(f"Invalid script type: {script_type}")

        return cls(generator_cls(config_path))

    def __init__(self, impl: Union[
        _script_generator.MenuScriptGenerator,
        _script_generator.ActionButtonGenerator
    ]) -> None:
        """Initialize with implementation object.

        Args:
            impl (ScriptGeneratorImpl): Implementation object containing template handling logic

        Returns:
            None

        Raises:
            TypeError: If impl is not a ScriptGeneratorImpl instance
            ValueError: If impl is None
        """
        self._impl = impl

    def get_categories(self) -> List[str]:
        """Get available script categories.

        Retrieves all supported script template categories from the configuration.

        Returns:
            List[str]: List of available script categories.
                Example: ['node', 'tool', 'shelf']

        Raises:
            RuntimeError: If no categories are configured
        """
        return self._impl.get_categories()

    def get_templates(self, category: str) -> List[str]:
        """Get available templates in a category.

        Retrieves all template names available within the specified category.

        Args:
            category (str): Category to get templates for. Must be a valid category name.

        Returns:
            List[str]: List of template names available in the specified category.
                Example: ['delete_unused', 'create_group', 'export_fbx']

        Raises:
            KeyError: If category doesn't exist
            ValueError: If category is empty or None
        """
        return self._impl.get_templates(category)

    def get_template_info(self, category: str, name: str) -> Dict[str, any]:
        """Get detailed information about a template.

        Retrieves metadata and configuration details for a specific template.

        Args:
            category (str): Template category to look in
            name (str): Name of the template to get info for

        Returns:
            Dict[str, Any]: Dictionary containing template metadata including:
                - description: Template description
                - parameters: Template parameters
                - defaults: Default values
                - options: Available options

        Raises:
            ValidationError: If template not found
            KeyError: If category doesn't exist
        """
        template = self._impl.get_template(category, name)
        if not template:
            raise ValidationError(f"Template {name} not found in {category}")

        return {
            "name": template.name,
            "category": template.category,
            "description": template.description,
            "options": {
                name: {
                    "label": opt["label"],
                    "options": opt["options"]
                }
                for name, opt in template.options.items()
            }
        }

    def generate_script(self, category: str, name: str,
                        options: Dict[str, str]) -> str:
        """Generate a script from a template.

        Creates a Python script by applying the provided options to the specified template.

        Args:
            category (str): Template category (e.g. 'tool', 'shelf', 'node')
            name (str): Template name to use for generation
            options (Dict[str, Any]): Dictionary of option values to apply to the template.
                Keys must match template parameter names.

        Returns:
            str: The generated script code ready for use in Houdini

        Raises:
            ValidationError: If script generation fails due to:
                - Invalid template category or name
                - Missing required options
                - Option value validation failures
            KeyError: If template not found

        Example:
            >>> options = {'name': 'myTool', 'type': 'delete'}
            >>> script = generate('tool', 'basic', options)
        """
        return self._impl.generate_script(category, name, options)

class HDAScriptManager:
    """Manages script generation in Houdini Digital Assets.

    This class provides high-level functionality for handling script generation
    UI and script creation in HDAs.

    Attributes:
        node (hou.Node): The HDA node containing the UI
        generator (ScriptGenerator): The script generator instance

    Methods:
        update(): Updates UI based on current selections
        generate(): Creates script from current UI values
        get_node(): Returns the associated HDA node

    Example:
        >>> node = hou.node('/obj/myHDA')
        >>> script_ui = ScriptGenerator(node)
        >>> script_ui.update()
        >>> result = script_ui.generate()

    Raises:
        ValueError: If initialization fails
        RuntimeError: If script generation operations fail
    """

    def __init__(self, node: hou.Node) -> None:
        """Initialize with HDA node.

        Args:
            node (hou.Node): HDA node containing script generation UI.
                Must be a valid Digital Asset node.

        Raises:
            ValueError: If node is None or not an HDA node
            TypeError: If node is not of type hou.Node
        """
        self._impl = _script_generator.HDAScriptUI(node)

    def update_ui(self) -> None:
        """Update the HDA UI based on current selections.

        Updates parameter values, enables/disables fields, and refreshes menu items
        based on the current state of UI selections in the HDA.

        Raises:
            RuntimeError: If UI parameters cannot be updated
            ValueError: If parameter values are invalid
        """
        self._impl.update_ui()

    def generate_script(self) -> Optional[str]:
        """Generate script based on current UI selections.

        Creates a Python script by processing the current parameter values in the HDA UI
        and generating appropriate script content using the configured generator.

        Returns:
            Optional[str]: The generated script if successful, None if generation fails
                due to invalid selections or missing required values.

        Raises:
            ValueError: If required parameters are missing or invalid
            RuntimeError: If script generation fails

        Example:
            >>> script = hda.generate_script()
            >>> if script:
            ...     hou.node('/obj/geo1').setParms({'script': script})
        """
        return self._impl.generate_script()

    @property
    def node(self) -> hou.Node:
        """Get the associated HDA node.

        Returns:
            hou.Node: The HDA node containing the script generation UI

        Raises:
            RuntimeError: If node reference is invalid or None
        """
        return self._impl.node

# Convenience functions for common operations

def create_menu_script(category: str, name: str,
                        options: Dict[str, str]) -> str:
    """Create a menu script from a template.

    Convenience function for quick menu script generation without
    creating a generator instance.

    Args:
        category: Template category
        name: Template name
        options: Dictionary of option values

    Returns:
        Generated menu script

    Example:
        >>> script = create_menu_script(
        ...     "group_selection",
        ...     "single_group_type",
        ...     {"option1": "hou.geometryType.Points"}
        ... )

    Raises:
        ValidationError: If template or options are invalid
    """
    generator = ScriptGenerator.create("menu")
    return generator.generate_script(category, name, options)

def create_action_script(category: str, name: str,
                        options: Dict[str, str]) -> str:
    """Create an action button script from a template.

    Creates a Python script for a Houdini action button based on the specified
    template and options. Handles proper formatting and validation for button
    script requirements.

    Args:
        category (str): Template category ('tool', 'shelf', etc.)
        name (str): Template name to use for generation
        options (Dict[str, Any]): Configuration options for script generation.
            Values depend on the template requirements.

    Returns:
        str: The generated Python script code ready for use in Houdini

    Raises:
        ValidationError: If script generation fails due to invalid options
        KeyError: If template or category not found

    Example:
        >>> script = create_action_script(
        ...     "file_operations",
        ...     "open_in_explorer",
        ...     {"option1": "hip"}
        ... )
    """
    generator = ScriptGenerator.create("action")
    return generator.generate_script(category, name, options)