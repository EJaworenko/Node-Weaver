import ast
from datetime import datetime
from pathlib import Path

AUTHOR = "Edward Jaworenko"
VERSION = "1.0.0"

ORDERED_MODULES = [
    'patterns',
    'utils',
    'decorators',
    'parsers',
    'core',
    'configuration',
    'factories',
    'files',
    'filesets',
    'collectors',
    'departments',
    'managers', # This is a directory with its own modules
    'commands',
]

# Add manager modules order
MANAGER_MODULES = [
    'base_manager',
    'project_manager',
    'asset_manager',
    'level_manager',
    'sequence_manager',
    'shot_manager',
]

def getClassesAndFunctions(file_path: Path) -> tuple:
    """
    Extract classes and functions from a Python file.

    Args:
        file_path (Path): Path to the Python file.

    Returns:
        tuple: Two dictionaries containing class and function names as keys,
                and their docstring summaries as values.
    """
    with file_path.open('r') as file:
        node = ast.parse(file.read())

    classes = {}
    functions = {}
    for item in node.body:
        if isinstance(item, ast.ClassDef):
            docstring = ast.get_docstring(item)
            classes[item.name] = docstring.split('\n')[0].strip() if docstring else "No description available."
        elif isinstance(item, ast.FunctionDef):
            if not item.name.startswith('_'):  # Exclude private functions
                docstring = ast.get_docstring(item)
                functions[item.name] = docstring.split('\n')[0].strip() if docstring else "No description available."
    return classes, functions


def getAllFromInit(init_path: Path) -> list:
    """
    Extract the __all__ list from an __init__.py file.

    Args:
        init_path (Path): Path to the __init__.py file.

    Returns:
        list: Contents of the __all__ list in the __init__.py file.
    """
    with init_path.open('r') as file:
        module = ast.parse(file.read())
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    if isinstance(node.value, ast.List):
                        return [elt.s for elt in node.value.elts if isinstance(elt, ast.Str)]
    return []


def generateReloadCode(module_items: dict, is_managers: bool = False) -> str:
    """Generate the reload code block based on module items."""
    if is_managers:
        return '''def reload_all(warn:bool = False):
    """Reload all manager modules."""
    import importlib
    from . import ''' + ", ".join(MANAGER_MODULES) + '''

    modules = [''' + ", ".join(MANAGER_MODULES) + ''']

    for module in modules:
        importlib.reload(module)

    if warn:
        print("Manager modules have been reloaded")
'''
    else:
        submodules = [f"'invapi.inv_io.{module}'" for module in ORDERED_MODULES if module in module_items]
        return '''def reload_all(warn:bool = True):
    """Reload inv_io and all its submodules."""
    import importlib
    import sys

    submodules = [
        ''' + ",\n        ".join(submodules) + '''
    ]

    # Reload submodules
    for submodule in submodules:
        if submodule in sys.modules:
            importlib.reload(sys.modules[submodule])

    # Reload main module
    if 'invapi.inv_io' in sys.modules:
        importlib.reload(sys.modules['invapi.inv_io'])

    if warn:
        print("inv_io and its submodules have been reloaded")
'''


def generateManagersInit(managers_items: dict) -> str:
    """Generate content for managers/__init__.py file."""
    imports = []
    all_items = []

    for manager, items in managers_items.items():
        classes = items.get('classes', [])
        functions = items.get('functions', [])
        if classes or functions:
            all_items.extend(classes + functions)
            imports.append(f"from .{manager} import {', '.join(classes + functions)}")

    # Join imports with newlines
    imports_str = '\n'.join(imports)

    # Format all_items with proper indentation
    all_items_str = '",\n    "'.join(all_items)

    content = f'''"""
Manager classes for the IO system.

This module provides a collection of manager classes for handling different
components of the project structure. Each manager type specializes in
organizing and tracking specific project elements.
"""

{imports_str}

__all__ = [
    "{all_items_str}"
]

def reload_all(warn:bool = False):
    """Reload all manager modules."""
    import importlib
    from . import {", ".join(MANAGER_MODULES)}

    modules = [{", ".join(MANAGER_MODULES)}]

    for module in modules:
        importlib.reload(module)

    if warn:
        print("Manager modules have been reloaded")
'''
    return content


def updateInit(package_dir: Path):
    """
    Update the __init__.py file with imports and __all__ declaration.
    """
    init_path = package_dir / '__init__.py'
    all_items = []
    imports = []
    descriptions = {}
    module_items = {}
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ensure managers directory exists
    managers_dir = package_dir / 'managers'
    managers_dir.mkdir(exist_ok=True)

    for module in ORDERED_MODULES:
        module_path = package_dir / module

        # Handle managers subpackage specially
        if module == 'managers':
            if module_path.is_dir():
                managers_items = {}

                for manager in MANAGER_MODULES:
                    manager_file = module_path / f"{manager}.py"
                    if manager_file.exists():
                        classes, functions = getClassesAndFunctions(manager_file)
                        if classes or functions:
                            managers_items[manager] = {
                                'classes': list(classes.keys()),
                                'functions': list(functions.keys())
                            }
                            all_items.extend(list(classes.keys()) + list(functions.keys()))
                            descriptions.update(classes)
                            descriptions.update(functions)

                # Create managers/__init__.py
                managers_init = module_path / '__init__.py'
                managers_init.write_text(generateManagersInit(managers_items))

                # Add managers import to main init (as one line)
                manager_classes = []
                for items in managers_items.values():
                    manager_classes.extend(items.get('classes', []))
                if manager_classes:
                    imports.append(f"from .managers import ({', '.join(manager_classes)})")

                module_items['managers'] = managers_items
                continue

        # Handle regular modules
        file_path = package_dir / f"{module}.py"
        if file_path.exists():
            classes, functions = getClassesAndFunctions(file_path)
            if classes or functions:
                module_items[module] = {
                    'classes': list(classes.keys()),
                    'functions': list(functions.keys())
                }
                all_items.extend(list(classes.keys()) + list(functions.keys()))
                imports.append(
                    f"from .{module} import {', '.join(list(classes.keys()) + list(functions.keys()))}"
                )
                descriptions.update(classes)
                descriptions.update(functions)

    # Format imports and all_items with proper indentation
    imports_str = '\n'.join(imports)
    all_items_str = '",\n    "'.join(all_items)

    docstring = '''"""
inv_io __init__ structure makes it simpler to access the inv_io submodules.
Allows calling:
from invapi.inv_io import NameOfClass
Instead of:
from invapi.inv_io.core import NameOfClass

File generated by update_init.py at {current_time}
"""'''.format(current_time=current_time)

    content = f'''{docstring}

{imports_str}

__all__ = [
    "{all_items_str}"
]

{generateReloadCode(module_items)}'''

    # Write main __init__.py
    with init_path.open('w', encoding='utf-8') as init_file:
        init_file.write(content)

    return module_items, descriptions


def updateInv_io(package_dir: Path):
    """
    Update the inv_io.py file with imports, docstrings, and __all__ declaration.

    This function generates a comprehensive facade module for easy importing
    of the invapi IO system components.

    Args:
        package_dir (Path): Path to the package directory.
    """
    module_items, descriptions = updateInit(package_dir)
    inv_io_path = package_dir.parent / 'inv_io.py'
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    import_statements = []
    all_items = []
    all_classes = []
    all_functions = []
    for module in ORDERED_MODULES:
        if module in module_items:
            classes = module_items[module]['classes']
            functions = module_items[module]['functions']
            items = classes + functions
            if items:
                items_join = ',\n    '.join(items)
                import_statements.append(f"from invapi.inv_io.{module} import (\n    {items_join}\n)")
                all_items.extend(items)
            if classes:
                all_classes.extend(classes)
            if functions:
                all_functions.extend(functions)

    imports = "\n\n".join(import_statements)
    all_declaration = "__all__ = [\n    '" + "',\n    '".join(all_items) + "'\n]"

    class_docstrings = "\n".join([f"    {item}: {descriptions.get(item, 'No description available.')}" for item in all_classes])
    function_docstrings = "\n".join([f"    {item}: {descriptions.get(item, 'No description available.')}" for item in all_functions])

    reload_code = generateReloadCode(module_items)

    content = f'''"""
inv_io - Simplified interface for the invapi IO system

This module provides a streamlined import interface for the invapi IO system,
allowing users to easily access key classes and functions without navigating
the full package structure.

The inv_io module acts as a facade for the invapi.io package, exposing only
the essential components that are intended for general use. This abstraction
layer simplifies imports and usage while allowing for more flexible internal
package management.

Classes:
{class_docstrings}

Functions:
{function_docstrings}

Usage:
    from inv_io import AssetManager, ProjectPathGenerator, utility_function
    asset_manager = AssetManager('/path/to/asset')
    project_path = ProjectPathGenerator.generatePath(...)
    result = utility_function(...)

Note:
    This module is the recommended way to import invapi IO components.
    It provides a stable API that can be maintained even if the internal
    structure of the invapi package changes.

See Also:
    invapi.io: The full IO package with additional utilities and internal modules.

Version:
    {VERSION} - File generated by update_init.py at {current_time}

Author:
    {AUTHOR}
"""

{imports}

{all_declaration}

{reload_code}
'''
    inv_io_path.write_text(content)
    print("Successfully updated inv_io.py")


if __name__ == "__main__":
    io_dir = Path(__file__).parent / 'inv_io'
    updateInit(io_dir)
    # updateInv_io(io_dir)
