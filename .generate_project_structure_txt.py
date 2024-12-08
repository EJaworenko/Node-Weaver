import os
from pathlib import Path

# Files and directories to ignore
IGNORE_PATTERNS = [
    '__pycache__',
    '.git',
    '.pytest_cache',
    '.vscode',
    '.idea',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*.pyold',
    '.DS_Store',
    'node_modules',
    'venv',
    'env',
    'tests',
    'generate_project_structure_txt.py',
    'project_structure.txt',
    'folderStructure_v001.json',
    'folderStructure_v002.json',
    'usd_module_import.py'
]

def should_ignore(path):
    """Check if the path should be ignored based on IGNORE_PATTERNS."""
    path_str = str(path)
    return any(
        ignored in path_str or
        (ignored.startswith('*.') and path_str.endswith(ignored[1:]))
        for ignored in IGNORE_PATTERNS
    )

def scan_directory(start_path, use_tree_format=True):
    """
    Recursively scan directory and return formatted string of structure.

    Args:
        start_path: Path to start scanning from
        use_tree_format: If True, use indented tree format. If False, use filepath listing.
    """
    output = []

    if use_tree_format:
        for root, dirs, files in os.walk(start_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]

            # Calculate relative path and indent level
            relative_path = os.path.relpath(root, start_path)
            level = 0 if relative_path == '.' else relative_path.count(os.sep) + 1
            indent = '    ' * level

            # Add current directory to output
            if relative_path != '.':
                output.append(f"{indent}{os.path.basename(root)}/")

            # Add files to output
            for file in sorted(files):
                if not should_ignore(Path(root) / file):
                    output.append(f"{indent}    {file}")
    else:
        # Simple filepath listing
        for root, dirs, files in os.walk(start_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]

            # Add files to output
            for file in sorted(files):
                if not should_ignore(Path(root) / file):
                    filepath = os.path.relpath(os.path.join(root, file), start_path)
                    output.append(filepath)

    return '\n'.join(output)

def main(use_tree_format=True):
    """Main function to create project structure file."""
    try:
        # Get the directory where the script is located
        script_dir = Path(__file__).parent.absolute()

        # Generate both formats
        structure = scan_directory(script_dir, use_tree_format=use_tree_format)

        # Write file
        output_file = script_dir / "project_structure.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(structure)

        print(f"Project structure written to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main(use_tree_format=False)
