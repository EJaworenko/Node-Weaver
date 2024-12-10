import os
import shutil
from pathlib import Path
import re

def fix_doc_links(content: str, is_features: bool = False) -> str:
    """Fix relative links in documentation files."""
    # Remove 'docs/' prefix from links
    content = re.sub(r'\[([^\]]+)\]\(docs/', r'[\1](', content)

    # Fix relative links to README.md and other files
    content = content.replace('../README.md', '../index.md')
    content = content.replace('./README.md', 'README.md')
    content = content.replace('.troubleshooting.md', '../troubleshooting.md')
    content = content.replace('../index.md', 'index.md')  # Add this line
    content = content.replace('(features/)', '(features/README.md)')  # Add this line

    return content

# Get root docs directory (3 levels up from current directory + docs)
root_docs = Path(__file__).parent.parent.parent.parent / 'docs'
root_path = Path(__file__).parent.parent.parent.parent
local_docs = Path(__file__).parent / 'docs'

# Create required directories
local_docs.mkdir(exist_ok=True)

# Copy main README.md to docs/index.md
main_readme = root_path / 'README.md'
if main_readme.exists():
    content = main_readme.read_text(encoding='utf-8')
    content = fix_doc_links(content)
    (local_docs / 'index.md').write_text(content, encoding='utf-8')

# Copy LICENSE file
license_file = root_path / 'LICENSE'
if license_file.exists():
    shutil.copy(license_file, local_docs / 'LICENSE')

# Copy features README
features_readme = root_docs / 'features' / 'README.md'
if features_readme.exists():
    features_dir = local_docs / 'features'
    features_dir.mkdir(exist_ok=True)
    content = features_readme.read_text(encoding='utf-8')
    content = fix_doc_links(content, True)
    (features_dir / 'README.md').write_text(content, encoding='utf-8')

# Copy images
images_src = root_docs / 'features' / 'images'
if images_src.exists():
    images_dest = local_docs / 'features' / 'images'
    if images_dest.exists():
        shutil.rmtree(images_dest)
    shutil.copytree(images_src, images_dest)

# File mapping for docs
file_map = {
    'features/color-palette.md': 'features/color-palette.md',
    'features/node-shape.md': 'features/node-shape.md',
    'features/tool-maker-tools.md': 'features/tool-maker-tools.md',
    'installation.md': 'installation.md',
    'contributing.md': 'contributing.md',
    'git-guide.md': 'git-guide.md',
    'troubleshooting.md': 'troubleshooting.md'
}

# Create directories and copy files
for dest, src in file_map.items():
    dest_path = local_docs / dest
    src_path = root_docs / src

    # Create parent directories
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy content and fix links
    if src_path.exists():
        content = src_path.read_text(encoding='utf-8')
        content = fix_doc_links(content, 'features' in dest)
        dest_path.write_text(content, encoding='utf-8')

# Create symbolic link to nodeweaver package for proper imports
# First, ensure we're in the correct directory
pkg_path = Path(__file__).parent
os.chdir(pkg_path)

# Create nodeweaver symlink if it doesn't exist
if not os.path.exists('nodeweaver'):
    try:
        if os.name == 'nt':  # Windows
            # On Windows, we need administrator privileges to create symlinks
            # As a fallback, copy the directory structure
            shutil.copytree('.', 'nodeweaver', dirs_exist_ok=True,
                          ignore=shutil.ignore_patterns('nodeweaver', '__pycache__', '*.pyc'))
        else:  # Unix
            os.symlink('.', 'nodeweaver')
    except Exception as e:
        print(f"Warning: Could not create symlink: {e}")