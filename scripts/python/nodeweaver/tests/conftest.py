"""Test configuration and fixtures for NodeWeaver.

This module provides pytest fixtures and configuration for testing NodeWeaver
functionality. It handles test environment setup, mock object creation, and
cleanup.

Fixtures:
    mock_node: Mock Houdini node for testing
    temp_hip: Temporary Houdini scene file
    mock_generator: Script generator with test configuration
"""

import pytest
import hou
from pathlib import Path
from typing import Generator, Any

@pytest.fixture
def mock_node(request: pytest.FixtureRequest) -> Generator[hou.Node, None, None]:
    """Provide a mock Houdini node for testing.

    Creates a temporary node with basic parameters and settings for testing.
    Automatically cleans up after tests complete.

    Yields:
        Temporary test node

    Example:
        >>> def test_node_customization(mock_node):
        ...     customize_node(mock_node, color=hou.Color((1,0,0)))
        ...     assert mock_node.color() == hou.Color((1,0,0))
    """
    # Create temporary node
    parent = hou.node("/obj")
    node = parent.createNode("null", "test_node")

    # Add test parameters
    ptg = hou.ParmTemplateGroup()
    ptg.append(hou.FloatParmTemplate("test_float", "Test Float", 1))
    ptg.append(hou.StringParmTemplate("test_string", "Test String", 1))
    node.setParmTemplateGroup(ptg)

    yield node

    # Cleanup
    node.destroy()

@pytest.fixture
def temp_hip(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary Houdini scene file.

    Sets up a clean Houdini environment with a temporary scene file
    for testing operations that require scene context.

    Args:
        tmp_path: Pytest temporary directory fixture

    Yields:
        Path to temporary hip file

    Example:
        >>> def test_scene_operation(temp_hip):
        ...     hou.hipFile.save(str(temp_hip))
        ...     assert temp_hip.exists()
    """
    hip_path = tmp_path / "test.hip"
    hou.hipFile.save(str(hip_path))

    yield hip_path

    # Cleanup
    if hip_path.exists():
        hip_path.unlink()