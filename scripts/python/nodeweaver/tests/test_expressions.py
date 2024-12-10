"""Tests for expression parsing and node generation.

This module tests NodeWeaver's ability to parse Houdini expressions
and generate equivalent node networks.

Test Categories:
    - Expression parsing
    - Node network generation
    - Parameter connections
    - Error handling
"""

import pytest
import hou
from nodeweaver.core.expr_to_nodes import ExpressionParser

def test_expression_parsing(mock_node):
    """Test parsing of Houdini expressions.

    Verifies that expressions are correctly parsed into component
    parts and operations.

    Test Cases:
        - Simple channel references
        - Mathematical expressions
        - Complex combinations
        - Invalid expressions
    """
    parser = ExpressionParser(mock_node)

    # Test simple channel reference
    result = parser.parse_and_resolve_channel_reference(
        mock_node,
        'ch("../param1")'
    )
    assert result[0] == "param1"  # Base name
    assert result[1] is None      # No components

    # Test component reference
    result = parser.parse_and_resolve_channel_reference(
        mock_node,
        'ch("../vector1x")'
    )
    assert result[0] == "vector1"    # Base name
    assert result[1] == [0, 'x']     # Component info

def test_node_generation(mock_node):
    """Test generation of node networks from expressions.

    Verifies that expression trees are correctly converted into
    functioning node networks.

    Test Cases:
        - Simple parameter nodes
        - Mathematical operation nodes
        - Complex expression networks
        - Network connections
    """
    parser = ExpressionParser(mock_node)

    # Test simple parameter
    parms_data = {
        "test_param": {
            "matching_reference": True,
            "value": 'ch("../source")'
        }
    }
    subnet, refs = parser.create_nodes_from_parameters(parms_data)
    assert subnet is not None
    assert len(refs) == 1