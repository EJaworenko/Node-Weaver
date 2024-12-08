# Troubleshooting Guide

> [← Back to main documentation](../README.md)

This guide covers common issues you might encounter while using Node Weaver and how to solve them.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Update Issues](#update-issues)
- [Common Tool Issues](#common-tool-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Tools Not Showing Up in Houdini

#### Check Your Package Path
1. Find your `nodeweaver.json` file in your Houdini preferences folder:
   - Windows: `C:/Users/YourUsername/Documents/houdiniXX.X/packages/`
   - Mac: `~/Library/Preferences/houdini/XX.X/packages/`
   - Linux: `/home/YourUsername/houdini/XX.X/packages/`

2. Open `nodeweaver.json` and verify:
   - The path matches where you installed Node Weaver
   - There are no extra spaces in the path
   - Use forward slashes (/) even on Windows

Example of correct path (If you extracted the NodeWeaver folder there):
```json
{
    "env": [
        {
            "NODEWEAVER": "C:/Users/YourName/Documents/NodeWeaver"
        }
    ]
}
```

#### Can't Find Houdini Preferences Folder?
1. Open Houdini
2. Go to File → Open
3. Type `$HOUDINI_USER_PREF_DIR` in the address bar
4. Press Enter
5. The window now shows your preferences folder
6. Right click the address bar and click "Expand Path" and it will show you the actual location

### Package Installation Issues

#### Missing Packages Folder
1. Go to your Houdini preferences folder
2. Create a new folder called "packages"
3. Copy `nodeweaver.json` into it
4. Restart Houdini

#### Wrong Houdini Version
- Node Weaver requires Houdini 19.5 or later, which is a bit older at this point.
- Check your Houdini version: Help → About Houdini

## Update Issues

### Manual Download Updates
If you downloaded Node Weaver manually:
1. Download the new version
2. Replace old Node Weaver folder with new version
3. Your `nodeweaver.json` shouldn't need to update, but compare the old file to the new one.
   If everything looks the same except the path, you're fine.
4. Restart Houdini

### Git Update Issues

#### Changes Won't Download
```bash
# Force update (will overwrite local changes)
git fetch --all
git reset --hard origin/main
```

#### Local Changes Blocking Update
If you've modified Node Weaver files:
```bash
# Save your changes
git stash

# Get updates
git pull origin main

# Restore your changes
git stash pop
```

## Common Tool Issues

**As problems in the tools appear, I'll document them here.**

## Getting Help

### Before Asking for Help
1. Check if your issue is listed in this guide
2. Search existing [GitHub issues](https://github.com/EJaworenko/Node-Weaver/issues)
3. Try the solutions mentioned above
4. Collect relevant error messages

### How to Report an Issue
1. Go to the [Issues page](https://github.com/EJaworenko/Node-Weaver/issues)
2. Click "New Issue"
3. Include:
   - What you were trying to do
   - What happened instead
   - Steps to reproduce the issue
   - Your Houdini version
   - Error messages (if any)
   - Screenshots (if relevant)

### Getting Quick Help
- Join Node Weaver GitHub discussions
- Check existing issues for solutions
- Include as much detail as possible in new issues

Remember: The more information you provide about your issue, the faster I can help you solve it!