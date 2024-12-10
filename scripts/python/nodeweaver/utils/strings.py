"""String manipulation utilities for NodeWeaver.

This module provides comprehensive string manipulation utilities focused on handling
Houdini-specific string operations, path management, and object representation.
It includes functions for sanitization, case conversion, tree visualization, and
detailed object inspection.

Functions:
    sanitize_string: Clean strings with custom transformations
    fix_slash: Replace backslashes with forward slashes
    fix_periods: Replace periods with underscores
    clean_posix_path: Normalize and validate POSIX paths
    is_camelcase: Check if string follows camelCase format
    to_camelcase: Convert string to camelCase format
    to_titlecase: Convert string to Title Case format
    camelcase_path: Convert path components to camelCase
    tree_from_string_list: Create tree visualization from path strings
    to_digits: Extract only digits from a string
    print_dict: Print nested dictionary structures with formatting
    comprehensive_repr: Generate detailed object representations
"""

from typing import List, Callable, Any, Optional
import sys
import re
import functools

def sanitize_string(s: str, transformations: Optional[List[Callable[[str], str]]] = None) -> str:
    """Apply a series of transformations to sanitize a string.

    Args:
        s: The input string to sanitize
        transformations: Optional list of functions to apply to the string.
            Default transformations handle special characters and spaces.

    Returns:
        The sanitized string

    Examples:
        >>> sanitize_string("Hello World!")
        'Hello_World_'

        >>> # Custom transformations
        >>> transformations = [str.lower, lambda x: x.replace(' ', '-')]
        >>> sanitize_string("Hello World!", transformations)
        'hello-world!'

    Note:
        Default transformations replace: *?:"<>| and spaces with underscores
    """
    default_transformations = [
        lambda x: re.sub(r'[*?:"<>| ]', "_", x)
    ]

    all_transformations = default_transformations + (transformations or [])

    return functools.reduce(lambda acc, func: func(acc), all_transformations, s)

# Helper functions for additional transformations
def fix_slash(s: str) -> str:
    """Replace backslashes with forward slashes in a string.

    Args:
        s (str): Input string containing slashes to fix

    Returns:
        str: String with backslashes replaced by forward slashes
    """
    return s.replace("\\", "/")


def fix_periods(s: str) -> str:
    """Replace periods with underscores in a string.

    Args:
        s (str): Input string containing periods to fix

    Returns:
        str: String with periods replaced by underscores
    """
    return s.replace(".", "_")


def clean_posix_path(path: str) -> str:
    """Clean and normalize a path to POSIX format.

    Removes invalid characters, normalizes slashes, and resolves relative paths.

    Args:
        path (str): The path to clean and normalize

    Returns:
        str: Cleaned POSIX-style path

    Raises:
        ValueError: If path contains invalid characters
    """
    path = re.sub(r'[<>:"|?*\s]', '', path.replace('\\', '/'))
    path = re.sub(r'/+', '/', path)
    components = [c for c in path.split('/') if c and c != '.']
    stack = []
    for c in components:
        if c == '..' and stack and stack[-1] != '..':
            stack.pop()
        else:
            stack.append(c)
    clean = '/'.join(stack)
    return f"/{clean}" if path.startswith('/') else clean or '.'


def is_camelcase(s) -> bool:
    """Check if a string is in camelCase format.

    Args:
        s (str): String to check

    Returns:
        bool: True if string is camelCase, False otherwise
    """
    pattern = r'^[a-z]+(?:[A-Z0-9][a-z0-9]*)*$'
    return bool(re.match(pattern, s))


def to_camelcase(s: str, check: bool = True) -> str:
    """Convert string to camelCase format.

    Handles multiple separator types and preserves existing camelCase if check=True.

    Args:
        s (str): String to convert
        check (bool, optional): Whether to preserve existing camelCase. Defaults to True.

    Returns:
        str: String in camelCase format
    """
    # Remove asterisks first to prevent empty strings
    s = s.replace("*", "")
    if not s:
        return ""

    s2 = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    if check and is_camelcase(s):
        return s
    elif s2:
        return ''.join([s2[0].lower(), s2[1:]])
    else:
        return ""


def to_titlecase(s: str) -> str:
    """Convert string to Title Case format.

    Args:
        s (str): String to convert

    Returns:
        str: String in Title Case format
    """
    return ' '.join(word.capitalize() for word in s.replace('_', ' ').split())


def camelcase_path(path: str) -> str:
    """Convert a full path to camelCase while preserving slashes.

    Args:
        path (str): Path string to convert

    Returns:
        str: Path with each component converted to camelCase
    """
    return '/'.join(to_camelcase(part) for part in path.split('/'))


def tree_from_string_list(paths: List[str]) -> str:
    """Create a tree visualization from a list of path strings.

    Converts a list of path strings into an ASCII tree structure representation,
    showing hierarchical relationships.

    Args:
        paths: List of path strings to visualize

    Returns:
        String containing ASCII tree visualization

    Example:
        >>> paths = ['/root/dir1/file1', '/root/dir1/file2', '/root/dir2']
        >>> print(tree_from_string_list(paths))
        root
        ├── dir1
        │   ├── file1
        │   └── file2
        └── dir2

    Notes:
        - Uses Unicode box-drawing characters
        - Properly handles mixed depth paths
        - Sorts entries for consistent output

    Since: 1.0.0
    """
    # Create a dictionary to store the tree structure
    tree = {}

    # Build the tree
    for path in paths:
        parts = path.strip('/').split('/')
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    # Helper function to build the tree string
    def build_branch(branch, prefix=''):
        lines = []
        for i, (key, value) in enumerate(sorted(branch.items())):
            is_last = i == len(branch) - 1
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{key}")
            lines.extend(build_branch(value, prefix + ('    ' if is_last else '│   ')))
        return lines

    # Build and return the tree string
    return '\n'.join(build_branch(tree))


def to_digits(s: str) -> str:
    """Convert string to digits by removing all non-digit characters.

    Args:
        s (str): Input string containing digits and other characters

    Returns:
        str: String containing only the digit characters from input

    Example:
        >>> to_digits("abc123def456")
        '123456'
    """
    s = ''.join(filter(lambda i: i.isdigit(), s))
    return s


def print_dict(d: dict, indent: int = 0, is_nested: bool = False) -> None:
    """Print dictionary or list with formatted indentation.

    Recursively prints dictionaries and lists with proper indentation for nested
    structures. Handles None values and non-dict/list objects appropriately.

    Args:
        d (dict): Dictionary or list to print
        indent (int, optional): Number of spaces to indent. Defaults to 0
        is_nested (bool, optional): Whether this is a nested call. Defaults to False.
            Used internally for recursive calls.

    Example:
        >>> data = {'a': 1, 'b': {'c': 2}}
        >>> print_dict(data)
        {
          "a": 1,
          "b": {
            "c": 2,
          },
        }
    """
    if d is None:
        print("Object is equal to 'None'.")
        return
    if not isinstance(d, (dict, list)) and not is_nested:
        print("Object is not a dictionary or list. Printing as-is.")
        print(d)
        return

    elif isinstance(d, dict):
        # not is_nested = top level dictionary
        if not is_nested:
            print(' ' * indent + '{')
        for key, value in d.items():
            if isinstance(value, dict):
                print(' ' * (indent + 2) + f'"{key}": {{')
                print_dict(value, indent + 4, is_nested=True)
                print(' ' * (indent + 2) + '},')
            elif isinstance(value, list):
                print(' ' * (indent + 2) + f'"{key}": [')
                print_dict(value, indent + 4, is_nested=True)
                print(' ' * (indent + 2) + '],')
            else:
                print(' ' * (indent + 2) + f'"{key}": {value},')
        if not is_nested:
            print(' ' * indent + '}')

    elif isinstance(d, list):
        if not is_nested:
            print(' ' * indent + '[')
        for value in d:
            if isinstance(value, dict):
                print(' ' * (indent + 2) + '{')
                print_dict(value, indent + 4, is_nested=True)
                print(' ' * (indent + 2) + '},')
            elif isinstance(value, list):
                print(' ' * (indent + 2) + f'[')
                print_dict(value, indent + 4, is_nested=True)
                print(' ' * (indent + 2) + '],')
            else:
                print(' ' * (indent + 2) + repr(value) + ',')
        if not is_nested:
            print(' ' * indent + ']')

    else:
        print(' ' * indent + repr(d))


def comprehensive_repr(obj: Any,
                        exclude: Optional[List[str]] = None,
                        prioritize: Optional[List[str]] = None,
                        include_private: bool = False,
                        include_callable: bool = False,
                        sort_keys: bool = False,
                        max_length: Optional[int] = None,
                        one_per_line: bool = False,
                        filter_func: Optional[Callable[[str, Any], bool]] = None,
                        _depth: int = 0,
                        _visited: Optional[set] = None) -> str:
    """Generate a comprehensive string representation of an object.

    Creates a detailed string representation of an object, with extensive
    customization options for controlling output format and content.

    Args:
        obj: The object to represent
        exclude: Attributes to exclude from representation
        prioritize: Attributes to list first in representation
        include_private: Include attributes starting with underscore
        include_callable: Include methods and other callable attributes
        sort_keys: Sort attributes alphabetically
        max_length: Truncate result to this length
        one_per_line: Put each attribute on a new line
        filter_func: Custom function to filter attributes
        _depth: Internal parameter tracking recursion depth
        _visited: Internal set tracking visited objects

    Returns:
        Formatted string representation

    Examples:
        >>> class Example:
        ...     def __init__(self):
        ...         self.a = 1
        ...         self.b = "test"

        >>> print(comprehensive_repr(Example(), one_per_line=True))
        Example(
            a=1
            b="test"
        )

        >>> # Exclude specific attributes
        >>> print(comprehensive_repr(Example(), exclude=['b']))
        Example(a=1)

    Notes:
        - Handles recursive structures safely
        - Provides cycle detection
        - Supports custom filtering and formatting
        - Preserves type information

    Since: 1.0.0
    """
    if _visited is None:
        _visited = set()
    if _depth > sys.getrecursionlimit() // 2 or id(obj) in _visited:
        return f"{obj.__class__.__name__}(...)"
    _visited.add(id(obj))

    exclude = exclude or []
    prioritize = prioritize or []
    attributes = []
    indent = "    " * (_depth + 1) if one_per_line else ""
    joiner = f"\n{indent}" if one_per_line else ", "
    starter = f"\n{indent}" if one_per_line else ""

    def _indent_repr(repr_str: str, depth: int) -> str:
        if not one_per_line or '\n' not in repr_str:
            return repr_str
        lines = repr_str.split('\n')
        indented_lines = [lines[0]] + [f"{'    ' * (depth + 1)}{line}" for line in lines[1:]]
        return '\n'.join(indented_lines)

    def _dict_repr(d: dict, depth: int) -> str:
        if not d:
            return "{}"
        items = []
        inner_indent = "    " * (depth + 2) if one_per_line else ""
        for k, v in d.items():
            if isinstance(v, dict):
                v_repr = _dict_repr(v, depth + 1)
            elif hasattr(v, '__repr__') and v.__repr__ is not object.__repr__:
                v_repr = _indent_repr(repr(v), depth + 1)
            elif hasattr(v, '__dict__'):
                v_repr = comprehensive_repr(v, exclude, prioritize, include_private, include_callable,
                                        sort_keys, None, one_per_line, filter_func, depth + 2, _visited.copy())
            else:
                v_repr = repr(v)
            items.append(f"{inner_indent}{repr(k)}: {v_repr}")
        if one_per_line:
            return "{\n" + ",\n".join(items) + f"\n{'    ' * (depth + 1)}}}"
        else:
            return "{" + ", ".join(items) + "}"

    def _handler(value: Any, depth: int):
        # Handle different types of values
        if isinstance(value, dict):
            return _dict_repr(value, depth)
        elif hasattr(value, '__repr__') and value.__repr__ is not object.__repr__:
            return _indent_repr(repr(value), depth)
        elif hasattr(value, '__dict__'):
            return comprehensive_repr(value, exclude, prioritize, include_private, include_callable,
                                    sort_keys, None, one_per_line, filter_func, depth + 1, _visited.copy())
        else:
            return repr(value)

    def _get_attributes(obj):
        if hasattr(obj, '__dict__'):
            return vars(obj).items()
        elif hasattr(obj, '__slots__'):
            return ((attr, getattr(obj, attr)) for attr in obj.__slots__ if hasattr(obj, attr))
        else:
            return ((attr, getattr(obj, attr)) for attr in dir(obj) if not attr.startswith('__'))

    for attr in prioritize:
        if hasattr(obj, attr) and attr not in exclude:
            value = getattr(obj, attr)
            value_repr = _handler(value, _depth)
            attributes.append(f"{attr}={value_repr}")

    for key, value in _get_attributes(obj):
        if key in prioritize or key in exclude:
            continue
        if not include_private and key.startswith('_'):
            continue
        if not include_callable and callable(value):
            continue
        if filter_func and not filter_func(key, value):
            continue

        value_repr = _handler(value, _depth)
        attributes.append(f"{key}={value_repr}")

    if sort_keys:
        attributes.sort()
    class_name = obj.__class__.__name__
    content = joiner.join(attributes)

    if one_per_line:
        result = f"{class_name}({starter}{content}\n{'    ' * _depth})"
    else:
        result = f"{class_name}({content})"
    if max_length and len(result) > max_length:
        result = result[:max_length-3] + "..."

    if len(exclude) > 0:
        excluded_str = ", ".join(exclude)
        if one_per_line:
            result += f"\n{'    ' * _depth}# Excluded attributes ({class_name}): {excluded_str}\n"
        else:
            result += f" # Excluded attributes ({class_name}): {excluded_str}"

    return result
