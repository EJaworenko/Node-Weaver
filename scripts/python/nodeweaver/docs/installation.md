<!-- omit in toc -->
# Installation Guide

> [← Back to main documentation](index.md)

This guide walks you through installing Node Weaver in Houdini. Choose the installation method that works best for you.

<!-- omit in toc -->
## Table of Contents
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Method 1: Simple Installation](#method-1-simple-installation)
  - [Step 1: Download Node Weaver](#step-1-download-node-weaver)
  - [Step 2: Extract Files](#step-2-extract-files)
  - [Step 3: Set Up the Package](#step-3-set-up-the-package)
  - [Step 4:Start Houdini](#step-4start-houdini)
- [Method 2: Git Installation](#method-2-git-installation)
- [Verifying Installation](#verifying-installation)
- [Common Installation Paths](#common-installation-paths)
  - [Windows](#windows)
  - [Mac](#mac)
  - [Linux](#linux)
- [Troubleshooting](#troubleshooting)
  - [Can't Find Preferences Folder?](#cant-find-preferences-folder)
  - [Tools Not Showing Up?](#tools-not-showing-up)
  - [Permission Issues?](#permission-issues)
  - [Need More Help?](#need-more-help)

## Quick Start

1. Download Node Weaver
2. Put it somewhere on your computer (a dedicated Houdini tools folder ideally)
3. Add it as a Houdini package
4. Start Houdini and check that it installed

Need more detail? Read on!

## Prerequisites

- Houdini 19.5 or later
- Python 3.7+
- Admin rights on your computer (for some installation locations)
- Git (optional, only for Method 2)

## Method 1: Simple Installation

### Step 1: Download Node Weaver
1. Visit the [releases page](https://github.com/edwardmakesthings/Node-Weaver/releases)
2. Find the latest release
3. Click "Source code (zip)" under Assets
4. Save the zip file anywhere

### Step 2: Extract Files
1. Find a good location for Node Weaver:
   - ✅ A dedicated Houdini tools folder. Set one up if you don't have one for your own sanity
   - ❌ NOT in Houdini's program files
   - ❌ NOT in your Houdini preferences folder

2. Example good locations:
   - Windows: `C:/Users/YourUsername/Documents/HoudiniTools/NodeWeaver`
   - Mac: `/Users/YourUsername/Documents/HoudiniTools/NodeWeaver`
   - Linux: `/home/YourUsername/HoudiniTools/NodeWeaver`

3. Extract the zip file there

### Step 3: Set Up the Package
1. Find your Houdini preferences folder:
   - Windows: `C:/Users/YourUsername/Documents/houdiniXX.X`
   - Mac: `~/Library/Preferences/houdini/XX.X`
   - Linux: `/home/YourUsername/houdini/XX.X`
   Replace XX.X with your Houdini version (like 20.5)

2. In your preferences folder:
   - Look for a "packages" folder
   - If it doesn't exist, create it

3. Copy the Package File:
   - Find `nodeweaver.json` in your Node Weaver folder
   - Copy it to the packages folder

4. Edit the Package File:
   - Open `nodeweaver.json` in any text editor
   - Find the line with `"NODEWEAVER": `
   - Change the path to where you put Node Weaver

Example `nodeweaver.json`:
```json
    "env": [
        {
            "NODEWEAVER": "C:/Path/To/Nodeweaver/Installation/NodeWeaver"
        }
    ]
```

### Step 4:Start Houdini
- Close Houdini completely (if it was open)
- Start Houdini

## Method 2: Git Installation

This method makes updating easier but requires Git. New to Git? Check my [Git Guide](git-guide.md).

1. Open Terminal/Git Bash
2. Navigate to where you want Node Weaver:
   ```bash
   cd C:/Path/To/Nodeweaver/Installation/NodeWeaver
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/edwardmakesthings/Node-Weaver.git
   ```
4. Follow Steps 3-4 from Method 1 above

## Verifying Installation

1. Start Houdini
2. Press Tab in a network view  (OBJ or SOP context)
3. Look for "Node Weaver Toolkit" in the categories
4. Try creating a tool from the tab menu

If you don't see the tools:
1. Try restarting Houdini
2. Check your package path
3. See [Troubleshooting](#troubleshooting)

## Common Installation Paths

### Windows
```
Node Weaver Location:
C:/Users/YourUsername/Documents/HoudiniTools/NodeWeaver

Package File:
C:/Users/YourUsername/Documents/houdini19.5/packages/nodeweaver.json
```

### Mac
```
Node Weaver Location:
/Users/YourUsername/Documents/HoudiniTools/NodeWeaver

Package File:
~/Library/Preferences/houdini/19.5/packages/nodeweaver.json
```

### Linux
```
Node Weaver Location:
/home/YourUsername/HoudiniTools/NodeWeaver

Package File:
/home/YourUsername/houdini19.5/packages/nodeweaver.json
```

## Troubleshooting

### Can't Find Preferences Folder?
In Houdini:
1. Go to File → Open
2. Type $HOUDINI_USER_PREF_DIR in the address bar at the top and press enter.
3. Right click the address and press "Expand Path"
4. That's your preferences folder!

### Tools Not Showing Up?
1. Check your `nodeweaver.json`:
   - Path should match your Node Weaver location exactly
   - Use forward slashes (/) even on Windows
   - Spaces in the path may cause problems, ideally use _ or - instead.
2. Make sure the packages folder exists
3. Restart Houdini

### Permission Issues?
- Don't install in Program Files
- Try running Houdini as administrator
- Check folder permissions

### Need More Help?
- See the [Troubleshooting Guide](troubleshooting.md)
- [Open an issue](https://github.com/edwardmakesthings/Node-Weaver/issues)
- Check existing issues for solutions

Remember: If something's not working, don't hesitate to ask for help!