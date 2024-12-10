"""Node manipulation utilities for Houdini.

This module provides functions for creating, modifying, and managing Houdini
nodes. It includes utilities for customization, replacement, and network
building from templates.

Classes:
    NetworkBuilder: Builds node networks from JSON configurations

Functions:
    customize_node: Apply common customizations to nodes
    replace_with_null: Replace nodes with null nodes
"""

from typing import Any, Dict, Optional
from pathlib import Path
import json
import hou

def customize_node(node: hou.Node,
                  pos: Optional[hou.Vector2] = None,
                  color: Optional[hou.Color] = None,
                  shape: Optional[str] = None,
                  comment: Optional[str] = None) -> None:
    """Apply common customizations to a node.

    Args:
        node: Node to customize
        pos: New position vector
        color: New color
        shape: New node shape name
        comment: New comment text

    Example:
        >>> node = hou.node('/obj/geo1')
        >>> customize_node(
        ...     node,
        ...     pos=hou.Vector2(0, 0),
        ...     color=hou.Color((1, 0, 0)),
        ...     shape="rect",
        ...     comment="Modified node"
        ... )

    Notes:
        - Only applies customizations for non-None arguments
        - Comments are automatically displayed when set

    Since: 1.0.0
    """
    if pos:
        node.setPosition(pos)
    if color:
        node.setColor(color)
    if shape:
        node.setUserData('nodeshape', shape)
    if comment:
        node.setComment(comment)
        node.setGenericFlag(hou.nodeFlag.DisplayComment,True)


def replace_with_null(node: hou.Node, null_name: str) -> hou.Node:
    """Create a null output node and return that if the current node isn't a null.

    Creates a null node connected to the input node's output and positioned
    below it. If the input node is already a null, returns it unchanged.

    Args:
        node: Node to potentially replace
        null_name: Name for the null node

    Returns:
        Either the original node if it's already a null, or the new null node

    Example:
        >>> geo = hou.node('/obj/geo1')
        >>> null = replace_with_null(geo, 'OUT_geo')

    Notes:
        - Positions null node 0.5 units left and 1 unit below input node
        - Does not delete or modify the original node
        - Returns existing null if one with the same name exists

    Since: 1.0.0
    """
    if node.type().name() == "null":
        return node

    parent = node.parent()
    find_node = parent.node(null_name)

    if find_node is None:
        find_node = node.createOutputNode("null", null_name)
        find_node.setPosition(node.position() + hou.Vector2((-0.5, -1)))

    return find_node


class NetworkBuilder:
    """Builds Houdini node networks from JSON configurations.

    This class handles the creation of node networks based on JSON template
    definitions, including proper node creation, parameter setting, and
    connection management.

    Attributes:
        parent: Parent node for network creation
        _created_nodes: Dictionary mapping node names to created nodes

    Example:
        >>> builder = NetworkBuilder(hou.node('/obj'))
        >>> last_node = builder.build_from_template("my_template")

    Since: 1.0.0
    """

    def __init__(self, parent_node: hou.Node):
        """Initialize with parent node for network creation.

        Args:
            parent_node: Node that will contain the network
        """
        self.parent = parent_node
        self._created_nodes: Dict[str, hou.Node] = {}

    def build_from_template(self, template_name: str) -> Optional[hou.Node]:
        """Build a network from a named template in the config file.

        Args:
            template_name: Name of template in example_networks.json

        Returns:
            The last created node or None if build fails

        Raises:
            ValueError: If template name is not found

        Notes:
            - Creates sticky note if template includes description
            - Maintains node connections defined in template
            - Preserves node positions and relationships

        Since: 1.0.0
        """
        config_path = Path(__file__).parent.parent / "config/node_shape/example_networks.json"
        try:
            with open(config_path) as f:
                templates = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            hou.ui.displayMessage(f"Error loading template: {str(e)}")
            return None

        if template_name not in templates:
            hou.ui.displayMessage(f"Template '{template_name}' not found")
            return None

        template = templates[template_name]

        # Create sticky note if description provided
        if "sticky" in template:
            sticky = self.parent.createStickyNote()
            sticky.setText(template["sticky"])
            sticky.setBounds(hou.BoundingRect(-2.7, -3.5, 3.7, -1))

        # Create nodes from tree
        last_node = None
        for node_data in template["tree"]:
            last_node = self._create_node(node_data)

        return last_node

    def _create_node(self, node_data: Dict[str, Any]) -> Optional[hou.Node]:
        """Create or configure a node based on template data.

        Args:
            node_data: Dictionary containing node configuration data

        Returns:
            Created/configured node
        """
        # Determine target node - either create new or use HDA
        if "name" in node_data:
            parent = (self._created_nodes[node_data["subnet"]]
                    if "subnet" in node_data else self.parent)
            node = parent.createNode(node_data["type_name"], node_data["name"])
            self._created_nodes[node_data["name"]] = node

            if "pos" in node_data:
                node.setPosition(hou.Vector2(node_data["pos"]))

            if "flags" in node_data:
                node.setRenderFlag("render" in node_data["flags"])
                node.setDisplayFlag("display" in node_data["flags"] and "nodisplay" not in node_data["flags"])
        else:
            node = self.parent

        # Configure parameters
        for parm_type in ["parms", "parmtuples", "expressions"]:
            if parm_type in node_data:
                for name, value in node_data[parm_type].items():
                    if parm_type == "parms":
                        node.parm(name).set(value)
                    elif parm_type == "parmtuples":
                        node.parmTuple(name).set(value)
                    elif parm_type == "expressions":
                        node.parm(name).setExpression(value)

        # Set inputs
        if "inputs" in node_data:
            for i, input_name in enumerate(node_data["inputs"]):
                input_node = self._created_nodes.get(input_name)
                if input_node:
                    node.setInput(i, input_node)

        return node