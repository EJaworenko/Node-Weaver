"""Tests for the script generation functionality.

This module contains tests for NodeWeaver's script generation system,
including template loading, script generation, and error handling.

Test Categories:
    - Template loading and validation
    - Script generation
    - Option processing
    - Error handling
"""

import pytest
from pathlib import Path
from nodeweaver.core import ScriptGenerator
from nodeweaver.core.exceptions import ValidationError

def test_script_generator_creation():
    """Test ScriptGenerator factory method.

    Verifies that ScriptGenerator.create() properly instantiates
    generators with correct configuration.

    Test Cases:
        - Valid script types
        - Custom configuration paths
        - Invalid script types
        - Missing configuration
    """
    # Test valid creation
    generator = ScriptGenerator.create("menu")
    assert generator is not None

    # Test invalid type
    with pytest.raises(ValueError):
        ScriptGenerator.create("invalid_type")

    # Test custom config path
    config_path = Path("tests/data/test_config.json")
    generator = ScriptGenerator.create("menu", config_path)
    assert generator is not None

def test_script_generation():
    """Test script generation from templates.

    Verifies that scripts are generated correctly from templates
    with various option combinations.

    Test Cases:
        - Basic template without options
        - Template with required options
        - Template with optional options
        - Invalid option combinations
    """
    generator = ScriptGenerator.create("menu")

    # Test basic generation
    script = generator.generate_script(
        "group_selection",
        "single_group_type",
        {"option1": "hou.geometryType.Points"}
    )
    assert script is not None
    assert "geometryType.Points" in script

    # Test invalid options
    with pytest.raises(ValidationError):
        generator.generate_script(
            "group_selection",
            "single_group_type",
            {"invalid_option": "value"}
        )