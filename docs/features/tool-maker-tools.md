<!-- omit in toc -->
# Tool Maker Tools

> [← Back to features](./README.md)

I created the Tool Maker Tools to handle repetitive tasks I kept running into while developing HDAs. It's still growing as I find new needs, but I've focused on the utilities that have made my TD work easier (that I'm allowed to add for now).

Unlike my other tools that focus on customizing Houdini's look, this is more of a collection of helpful utilities that I've built up over time, but it's a bit sparse at the moment.

<!-- omit in toc -->
## Table of Contents
- [Overview](#overview)
- [HDA Tool Maker](#hda-tool-maker)
  - [Script Generator \[In Progress\]](#script-generator-in-progress)
  - [Copy to Instance Converter](#copy-to-instance-converter)
- [Node Weaver Shelf](#node-weaver-shelf)
  - [Script Inspector](#script-inspector)
- [Right-Click Menus](#right-click-menus)
  - [Node Context Menu](#node-context-menu)
  - [Parameter Context Menu](#parameter-context-menu)
- [Troubleshooting](#troubleshooting)
  - [Need Help?](#need-help)

## Overview

So far, the toolset is small but includes:
- Tools to speed up HDA development
- Network management helpers
- Script generators for common tasks
- Parameter manipulation shortcuts

## HDA Tool Maker

### Script Generator [In Progress]
I found myself writing the same kinds of menu and action button scripts over and over, so I made this to handle the repetitive parts. It's set up for the most common cases I run into, but you can extend it for your own needs too.

### Copy to Instance Converter
This one's actually more for artists than TDs - it converts Copy to Points setups to instancing for better performance. I included it here since it's part of the same toolkit, even though it's a bit of an outlier.

## Node Weaver Shelf

### Script Inspector
This one's great when you need to see a list of all the scripts involved with a node. I use it when refactoring code or renaming parameters in particular. Select a node and it'll show you all its:
- Callback scripts
- Default value expressions
- Menu scripts

Unfortunately, I haven't found a way to access action button scripts - seems to be a Houdini limitation.

## Right-Click Menus

### Node Context Menu
- **Node Color Picker**: Normally, you need to create a custom color in the Network View Color Palette then apply it, but this removes the need for that.
- **Node Renaming** [In Progress]: Working on a better way to rename nodes in bulk with a lot of control.

### Parameter Context Menu
- **Value Editor** [In Progress]: Building a more powerful way to edit parameter values... same tool as above

## Troubleshooting

Once I get more tools into here I'm sure troubleshooting will fill out.

### Need Help?
If you encounter issues:
1. Try restarting Houdini
2. Check [existing issues](https://github.com/EJaworenko/Node-Weaver/issues)
3. [Open a new issue](https://github.com/EJaworenko/Node-Weaver/issues/new)