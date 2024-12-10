"""Generate the code reference pages and navigation."""
from pathlib import Path
import mkdocs_gen_files
import sys

# Add the package root to Python path
package_root = Path(__file__).parent.parent  # This points to scripts/python/nodeweaver
sys.path.insert(0, str(package_root))

nav = mkdocs_gen_files.Nav()

# Look for Python files in each main module
MODULE_PATHS = [
    "core",
    "utils",
    "nodes",
    "stringweaver"
]

for module in MODULE_PATHS:
    module_path = Path(module)

    # Skip if module directory doesn't exist
    if not (package_root / module_path).exists():
        continue

    for path in sorted((package_root / module_path).rglob("*.py")):
        rel_path = path.relative_to(package_root)
        doc_path = rel_path.with_suffix(".md")
        full_doc_path = Path("reference", doc_path)

        parts = tuple(rel_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        # Skip private modules (starting with _)
        if any(part.startswith("_") for part in parts):
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            # Create module path without .py extension
            module_path = path.relative_to(package_root).with_suffix("")
            # Convert path separators to dots for Python import
            module_name = str(module_path).replace("/", ".").replace("\\", ".")

            fd.write(f"# {parts[-1]}\n\n")
            fd.write(f"::: {module_name}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)

# Generate table of contents
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

# Create a module index
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())