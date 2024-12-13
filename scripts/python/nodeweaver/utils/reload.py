"""Module reloading utilities for development.

This module provides functionality for recursively reloading Python packages
and their submodules, maintaining proper dependency order and handling
circular imports safely.

The module exposes a simple reload_all() function while hiding the complexity
of proper module reloading in the internal _ModuleReloader class.

Example:
    >>> import nodeweaver
    >>> nodeweaver.reload_all()  # Reloads entire package hierarchy
"""

import sys
import types
import importlib
from pathlib import Path
from typing import Set, Dict

class _ModuleReloader:
    """Handles recursive module reloading while managing dependencies.

    This class maintains the state needed to properly reload a module hierarchy,
    handling circular dependencies and ensuring modules are reloaded in the
    correct order.

    Attributes:
        _visited: Set of module names that have been processed
        _reloaded: Set of module names that have been reloaded
        _processing: Set of module names currently being processed (for cycle detection)
        _dependencies: Dict mapping module names to their dependencies
    """

    def __init__(self):
        """Initialize reloader state."""
        self._visited: Set[str] = set()
        self._reloaded: Set[str] = set()
        self._processing: Set[str] = set()
        self._dependencies: Dict[str, Set[str]] = {}

    def reload_package(self, package_name: str) -> None:
        """Reload a package and all its submodules.

        Args:
            package_name: Name of package to reload (e.g. 'nodeweaver')

        Note:
            This first maps the module dependency graph, then reloads modules
            in dependency order to avoid issues with circular imports.
        """
        # Reset state
        self._visited.clear()
        self._reloaded.clear()
        self._processing.clear()
        self._dependencies.clear()

        # Map dependencies first
        self._map_dependencies(package_name)

        # Then reload in dependency order
        self._reload_mapped_modules()

    def _map_dependencies(self, module_name: str) -> None:
        """Map the dependency graph for a module and its submodules.

        Args:
            module_name: Name of module to map

        Note:
            This recursively processes all submodules, building a complete
            dependency graph before any reloading occurs.
        """
        if module_name in self._visited:
            return

        self._visited.add(module_name)
        self._processing.add(module_name)

        try:
            module = sys.modules.get(module_name)
            if not module:
                return

            # Track dependencies
            dependencies = set()
            self._dependencies[module_name] = dependencies

            # Process all submodules
            if hasattr(module, '__path__'):
                pkg_path = Path(module.__path__[0])
                for child in pkg_path.glob('**/*.py'):
                    if child.stem == '__init__':
                        submodule = f"{module_name}"
                    else:
                        # Convert path to module name
                        rel_path = child.relative_to(pkg_path.parent)
                        submodule = '.'.join(rel_path.with_suffix('').parts)

                    if submodule in sys.modules:
                        dependencies.add(submodule)
                        self._map_dependencies(submodule)

            # Process imported modules within the package
            for attr_name, attr_value in module.__dict__.items():
                if isinstance(attr_value, types.ModuleType):
                    if attr_value.__name__.startswith(module_name.split('.')[0]):
                        dependencies.add(attr_value.__name__)
                        self._map_dependencies(attr_value.__name__)

        finally:
            self._processing.remove(module_name)

    def _reload_mapped_modules(self) -> None:
        """Reload all mapped modules in dependency order.

        This processes the dependency graph built by _map_dependencies,
        reloading modules only after their dependencies have been reloaded.
        """
        while self._dependencies:
            # Find modules with no unprocessed dependencies
            ready = {
                name for name, deps in self._dependencies.items()
                if not (deps - self._reloaded)
            }

            if not ready:
                # If no modules are ready but some remain,
                # we have a circular dependency
                remaining = self._dependencies.keys()
                remaining_str = ' ,'.join(list(remaining))
                print(f"Warning: Possible circular dependencies detected between: {remaining_str}")
                ready = set(remaining)

            # Reload ready modules
            for name in ready:
                if name in sys.modules:
                    try:
                        importlib.reload(sys.modules[name])
                    except Exception as e:
                        print(f"Error reloading {name}: {e}")
                self._reloaded.add(name)
                del self._dependencies[name]

def reload_all(package_name: str = 'nodeweaver') -> None:
    """Reload the entire package hierarchy.

    This function handles reloading the package and all its submodules
    in the correct order, managing dependencies and circular imports.

    Note:
        This is primarily intended for development use to reload modified
        code without restarting Python.

    Example:
        >>> import nodeweaver
        >>> nodeweaver.reload_all()
    """
    reloader = _ModuleReloader()
    reloader.reload_package(package_name)