"""Convert Houdini VOP parameter expressions to node networks.

This module provides functionality to convert VOP parameter expressions and
references into equivalent node networks, enabling channel expressions to
maintain functionality once a material node is converted to a subnet, HDA, or
otherwise needs to be compiled.

Attributes:
    MATERIALX_PREFIXES (List[str]): MaterialX type prefixes used in parameters

Functions:
    convert_parameter_references: Convert parameter references to node networks
    create_parameter_inputs: Create parameter inputs for node inputs
    process_parameter_inputs: Process parameter inputs with various operations

Examples:
    >>> node = hou.node('/obj/geo1/material1')
    >>> convert_parameter_references(node, process_subnodes=True)
    >>> create_parameter_inputs(node, promote_ui=True)

Notes:
    This module is part of the nodeweaver package for Houdini node manipulation.
"""
from typing import List, Dict, Union, Tuple, Optional
import hou
from nodeweaver.core._impl._expr_to_nodes import (
    convert_parm_references_to_parm_nodes,
    create_parm_inputs_for_all_inputs,
    process_all_parm_inputs,
    HoudiniExpressionParser as _HoudiniExpressionParser
)

class ExpressionParser:
    """Parser for Houdini parameter expressions and channel references.

    Provides utilities for parsing and analyzing parameter expressions,
    with focus on channel references and MaterialX naming conventions.

    Attributes:
        MATERIALX_PREFIXES (List[str]): List of MaterialX type prefixes ('f_', 'v_', etc.)

    Methods:
        strip_materialx_type_prefixes: Removes MaterialX type prefixes from strings
        parse_and_resolve_channel_reference: Resolves channel references to components

    Example:
        >>> parser = ExpressionParser()
        >>> clean_name = parser.strip_materialx_type_prefixes("f_base_color")
        >>> print(clean_name)
        'base_color'
    """
    @staticmethod
    def strip_materialx_type_prefixes(s: str) -> str:
        """Strip MaterialX type prefixes from strings.

        MaterialX parameters include type prefixes like 'i_', 'f_', 'v_', etc. in
        some nodes. This function removes these prefixes to get the base string
        while preserving other underscores in the name.

        Args:
            s: String that may contain MaterialX type prefixes

        Returns:
            String with MaterialX type prefixes removed

        Examples:
            >>> strip_materialx_type_prefixes("f_base_color")
            'base_color'
            >>> strip_materialx_type_prefixes("v_normal_vector")
            'normal_vector'
            >>> strip_materialx_type_prefixes("my_f_param")  # Won't strip internal prefixes
            'my_f_param'
        """
        return _HoudiniExpressionParser.strip_materialx_type_prefixes(s)

    @staticmethod
    def parse_and_resolve_channel_reference(node: hou.Node, channel_ref: str) -> Tuple[Optional[str], Optional[List], Optional[hou.ParmTuple], Optional[str]]:
        """Parse and resolve a channel reference to its components.

        Handles both absolute and relative channel references, resolving them to their
        actual parameter locations and component indices.

        Args:
            node: Node containing the channel reference
            channel_ref: Channel reference string (e.g., 'ch("../param1")')

        Returns:
            Tuple containing:
            - Base parameter name without component suffix
            - Component indices and names if applicable
            - Referenced parameter tuple
            - Channel reference type (ch, chi, chs)
        """
        return _HoudiniExpressionParser.parse_and_resolve_channel_reference(node, channel_ref)

    @classmethod
    def create_nodes_from_parameters(cls, target_node: hou.Node,
                                   parms_data: Dict[str, Dict[str, Union[str, bool]]],
                                   match_reference_parm_names: bool = True,
                                   parameters_as_subnet_connectors: bool = True) -> Tuple[hou.Node, Dict[str, str]]:
        """Convert parameter data into a node network.

        Creates a subnet containing nodes that represent the parameter expressions
        and references, properly connected to maintain the same behavior.

        Args:
            target_node: Node whose parameters are being converted
            parms_data: Dictionary mapping parameter names to their expression data
            match_reference_parm_names: Whether to maintain referenced parameter names
            parameters_as_subnet_connectors: Whether to use subnet connectors for parameters

        Returns:
            Tuple containing:
            - Created subnet node
            - Dictionary of simple channel references
        """
        parser = _HoudiniExpressionParser(target_node)
        return parser.create_nodes_from_parameters(parms_data, match_reference_parm_names, parameters_as_subnet_connectors)


def convert_references_to_nodes(node: hou.Node,
                              process_subnodes: bool = None,
                              match_reference_names: bool = None,
                              use_subnet_connectors: bool = None) -> None:
    """Convert parameter references in a node to parameter nodes.

    Converts channel references and expressions in parameters to equivalent
    parameter nodes that preserve functionality.

    Args:
        node (hou.Node): The node to process
        process_subnodes (Optional[bool]): Whether to process child nodes.
            If None, will prompt user
        match_reference_names (Optional[bool]): Whether to match referenced parameter names.
            If None, will prompt user
        use_subnet_connectors (Optional[bool]): Whether to use subnet connectors.
            If None, will prompt user

    Returns:
        None

    Raises:
        ValueError: If node is None or invalid
        RuntimeError: If parameter conversion fails

    Example:
        >>> node = hou.node('/obj/geo1/material1')
        >>> convert_parameter_references(node, True, True, False)
    """
    convert_parm_references_to_parm_nodes(
        node,
        process_subnodes,
        match_reference_names,
        use_subnet_connectors
    )


def create_parameter_inputs(node: hou.Node,
                          add_node_prefix: bool = None,
                          promote_ui: bool = None,
                          process_selected: bool = None) -> None:
    """Create parameter inputs for all inputs on a node.

    Generates parameter nodes for each input on the specified node, with options
    for naming, UI promotion, and batch processing.

    Args:
        node (hou.Node): The node to process
        add_node_prefix (Optional[bool]): Whether to add node name prefix to parameters.
            If None, will prompt user
        promote_ui (Optional[bool]): Whether to promote parameters to the UI.
            If None, will prompt user
        process_selected (Optional[bool]): Whether to process all selected nodes.
            If None, will prompt user

    Returns:
        None

    Raises:
        ValueError: If node is None or invalid
        RuntimeError: If parameter creation fails

    Example:
        >>> node = hou.node('/obj/geo1/material1')
        >>> create_parameter_inputs(node, True, True, False)
    """
    create_parm_inputs_for_all_inputs(
        node,
        add_node_prefix,
        promote_ui,
        process_selected
    )


def process_parameter_inputs(nodes: Union[hou.Node, List[hou.Node]],
                           delete: bool = None,
                           hide: int = None,
                           convert: int = None) -> None:
    """Process parameter inputs with various operations.

    Performs bulk operations on parameter inputs including deletion, visibility changes,
    and type conversion across one or multiple nodes.

    Args:
        nodes (Union[hou.Node, List[hou.Node]]): Node or list of nodes to process
        delete (Optional[bool]): Whether to delete parameter inputs.
            If None, will prompt user
        hide (Optional[int]): Hide state for parameter inputs.
            - 0: No change
            - 1: Show
            - 2: Hide
            If None, will prompt user
        convert (Optional[int]): Conversion mode for parameters.
            - 0: None
            - 1: Subnet
            - 2: Parameter
            If None, will prompt user

    Returns:
        None

    Raises:
        ValueError: If nodes is empty or invalid
        TypeError: If parameter values are incorrect types
        RuntimeError: If operations fail

    Example:
        >>> node = hou.node('/obj/geo1/material1')
        >>> process_parameter_inputs(node, delete=False, hide=1, convert=0)
    """
    process_all_parm_inputs(nodes, delete, hide, convert)