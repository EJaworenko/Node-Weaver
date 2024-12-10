"""Utility functions for working with Houdini Digital Assets (HDAs).

This module provides utilities for managing and updating HDAs, particularly
focusing on section management and source file synchronization.

Note:
    All operations that modify HDAs automatically handle update mode management
    to ensure consistent state.
"""

from typing import Optional, Union, List
from pathlib import Path
import hou
from nodeweaver.utils.decorators import pause_update_mode

@pause_update_mode
def update_hda_sections_from_source_files(hdas: Optional[Union[hou.Node, List[hou.Node]]] = None) -> None:
    """Update HDA sections with contents from their source files.

    Updates each section's content by reading from source files specified in the HDA's
    extra options. Source file paths should be defined in the extra options with keys
    in the format "{section_name}/Source".

    Args:
        hdas: HDA node or list of HDA nodes to update. If None, uses selected nodes.

    Example:
        # Update a specific HDA
        >>> node = hou.node('/obj/my_hda')
        >>> update_hda_sections_from_source_files(node)

        # Update multiple HDAs
        >>> nodes = [hou.node('/obj/hda1'), hou.node('/obj/hda2')]
        >>> update_hda_sections_from_source_files(nodes)

        # Update selected HDAs
        >>> update_hda_sections_from_source_files()

    Notes:
        - The function maintains a summary of successful updates and errors
        - Sections without specified source files are skipped
        - Empty source files are skipped
        - Updates are performed with update mode set to Manual

    Since: 1.0.0
    """
    # Handle input types
    if hdas is None:
        hdas = hou.selectedNodes()
    elif isinstance(hdas, hou.Node):
        hdas = [hdas]

    # Track overall success
    success_count = 0
    error_count = 0

    for hda in hdas:
        try:
            definition = hda.type().definition()
            if not definition:
                print(f"Warning: {hda.path()} is not an HDA")
                continue

            sections = definition.sections()
            extra_options = definition.extraFileOptions()
            section_updates = 0

            for section_name, section in sections.items():
                source_key = f"{section_name}/Source"

                # Skip if source not specified
                if source_key not in extra_options:
                    continue

                # Skip if source path is empty
                source_path = extra_options[source_key].strip()
                if not source_path:
                    continue

                source_path = Path(source_path)
                if not source_path.exists():
                    print(f"Warning: Source file not found for {definition.description()}: {source_path}")
                    continue

                try:
                    file_contents = source_path.read_text()
                    if file_contents.strip():
                        section.setContents(file_contents)
                        section_updates += 1
                        print(f"{definition.description()}: Updated section {section_name} from {source_path}")
                except Exception as e:
                    print(f"{definition.description()}: Error reading {source_path}: {str(e)}")
                    error_count += 1

            if section_updates > 0:
                print(f"{definition.description()}: Updated {section_updates} sections")
                success_count += 1

        except Exception as e:
            print(f"Error processing HDA {definition.description()}: {str(e)}")
            error_count += 1

    # Print summary
    if success_count or error_count:
        print(f"\nUpdate Summary:")
        print(f"Successfully processed: {success_count} HDAs")
        if error_count:
            print(f"Errors encountered: {error_count}")
    else:
        print("No HDAs were processed")