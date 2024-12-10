<!-- omit in toc -->
# Node Shape Creator HDA

> [← Back to features](README.md)

The Node Shape Creator makes it easy to design custom node shapes in Houdini. [Credit to Simon Fiedler and Bastian Schiffer](https://vimeo.com/221182957) for doing the initial exploration years ago.

<!-- omit in toc -->
## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Features](#features)
  - [Example Networks](#example-networks)
  - [Shape Definition](#shape-definition)
  - [Visualization Options](#visualization-options)
    - [Style Settings](#style-settings)
    - [Node Appearance](#node-appearance)
    - [Wire Preview](#wire-preview)
  - [Node Shape Configuration](#node-shape-configuration)
    - [Basic Settings](#basic-settings)
    - [Wire Settings](#wire-settings)
- [Node Shape Guidelines](#node-shape-guidelines)
  - [Shape Creation](#shape-creation)
  - [Default Node Stats](#default-node-stats)
  - [Wire Handling](#wire-handling)
- [File Management](#file-management)
  - [Save Locations](#save-locations)
- [Troubleshooting](#troubleshooting)
  - [File Export Issues](#file-export-issues)
  - [Need Help?](#need-help)

## Overview

Custom node shapes can make your networks more interesting and visually distinct. This tool helps you:
- Design custom shapes visually
- Test with different wire configurations
- Export directly to Houdini's format
- Analyze existing node shapes

## Getting Started

1. Access via: OBJ/SOP Tab Menu → Node Weaver → Custom Node Shape Creator
2. When first opened, the interface provides:
   - Examples of 3 distinct approaches to making shapes that generate a node network for study
   - Shape selection parameters
   After shapes have been selected the interface also provides:
   - Node shape information
   - Visualization options
   - A real-time preview (as a 3D model)
   - Shape modification options
   - Export options

## Features

### Example Networks
- Built-in examples show different approaches to shape creation
- Each example includes:
  - A subnet showing the technique
  - A sticky note explaining unique features of that technique

### Shape Definition
- Input geometry must have at least 5 polygon primitives (main shape and 4 flags)
- These primitives define the core shape definitions

### Visualization Options

#### Style Settings
- Four different color palettes representing different Houdini contexts
- Helps visualize how shape will look in different situations
- No effect on final output

#### Node Appearance
- Toggle different node flags to preview appearance
- Customize node color for visualization
- Preview with custom icons (load PNG files)
- No effect on final output

#### Wire Preview
- Toggle wire visualization
- Helps verify wire curvature before export
- Shows connections with varying numbers of inputs/outputs

### Node Shape Configuration

#### Basic Settings
- Set node shape name (defines output filename)
- Configure shape dimensions and positioning
- Apply transformations and adjustments

#### Wire Settings
- Adjust input wire curvature
- Configure output wire curvature
- Set wire connection points
- Preview wire behavior with different numbers of connections

## Node Shape Guidelines

### Shape Creation
- Node shapes require 5 polygon primitives for shape definition
- Shapes ideally exist inside the 0-1 space in X and Y
- Center on the 0.5x0.15 point (center of standard nodes)
- Tool will transform coordinates automatically
- Some settings allow working outside standard space if needed

### Default Node Stats
For consistency with Houdini's default nodes, consider these measurements:
- Most common node size: 1 × 0.3 units
- Most common icon size: 0.24 × 0.24 units
- Input vertical range: -0.2 to -0.09 units
- Output vertical range: 0.38 to 0.51 units
- Median input/output position: -0.09 × 0.38 units
- Circle node: 0.57 × 0.57 units with 0.21 × 0.21 icon

### Wire Handling
- Input and output curves can be non-centered
- Centered curves recommended for:
  - Clean wire connections
  - Proper node alignment with layout tools (hold "A")
- Wire curvature can be adjusted:
  - Settings under "Input Settings > Wire Curvature"
  - Settings under "Output Settings > Wire Curvature"
  - Affects aesthetic appearance of connections

## File Management

### Save Locations
Node shapes can be saved in several locations:

1. **User Preferences (Recommended for Personal Use)**
   ```
   $HOUDINI_USER_PREF_DIR/config/NodeShapes
   ```
   - Best for individual use
   - Remember to transfer to new preferences folder when updating Houdini

2. **Package Directory (Recommended for Distribution)**
   ```
   $NAMEOFPACKAGEPATH/config/NodeShapes
   ```
   - Used by Node Weaver itself
   - Best for package distribution

3. **Houdini Installation (Not Recommended)**
   ```
   C:/Program Files/Side Effects Software/Houdini XX.X.XXX/houdini/config/NodeShapes
   ```
   - Contains default Houdini shapes
   - Not recommended for custom shapes
   - Highlighting this folder for study vs to save there

## Troubleshooting

### File Export Issues
- Verify write permissions in target directory
- Check correct path structure (/config/NodeShapes/)
- Ensure valid node shape name
- Restart Houdini after adding new shapes if clicking "Reload Node Shape Palette" doesn't work

### Need Help?
If you encounter issues:
1. Try restarting Houdini
2. Check [existing issues](https://github.com/EJaworenko/Node-Weaver/issues)
3. [Open a new issue](https://github.com/EJaworenko/Node-Weaver/issues/new)