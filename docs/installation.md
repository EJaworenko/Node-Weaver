# Installation Guide

This guide will help you install Node Weaver in Houdini. There are two ways to download Node Weaver, but we'll focus on the simpler direct download method first.

**Important Notes:**
- **DO NOT** save it to your Houdini program directory (C:/Program Files/Side Effects Software/Houdini XX.X.XXX on Windows)
- For network drives, mapping to a drive letter is highly recommended

## Simple Installation (Recommended for Most Users)

### Step 1: Download Node Weaver
1. Visit the [releases page](https://github.com/EJaworenko/Node-Weaver/releases)
2. Find the latest release at the top of the page
3. Click on "Source code (zip)" under Assets
4. Save the zip file to your computer
5. Extract the zip file to a location of your choice
  - You can put it anywhere except your Houdini preferences folder. Ideally, you have a folder where you store all your Houdini plugin content.
  - Good locations include:
    - Windows: C:/Users/YourUsername/Documents/NodeWeaver
    - Mac: /Users/YourUsername/Documents/NodeWeaver
    - Linux: /home/YourUsername/NodeWeaver

### Step 2: Set Up the Package
1. Find your Houdini preferences folder:
  - Windows: Open Explorer and go to C:/Users/YourUsername/Documents/houdiniXX.X
  - Mac: Open Finder and go to ~/Library/Preferences/houdini/XX.X
  - Linux: Go to /home/YourUsername/houdini/XX.X
  (Replace XX.X with your Houdini version, like 19.5)

2. In your preferences folder:
  - Look for a folder called "packages"
  - If it doesn't exist, create it

3. Copy Files:
  - Find nodeweaver.json in the files you extracted
  - Copy it to the packages folder you just found/created

4. Configure the Package:
  - Open nodeweaver.json in a text editor
  - Find the line with $NODEWEAVER
  - Change the path to where you extracted Node Weaver
  Example:
  {
    "env": [
      {
        "NODEWEAVER": "C:/Users/YourUsername/Documents/NodeWeaver"
      }
    ]
  }

5. Start Houdini

You should now see Node Weaver tools in Houdini! To check, press tab and look for "Node Weaver Toolkit" in the categories.

## Alternative Installation Method (For Developers)

If you're comfortable with command line tools, you can install using Git. This makes updating easier:

1. Open Terminal (Mac/Linux) or Git Bash (Windows)
2. Navigate to where you want to install:
  cd C:/Users/YourUsername/Documents

3. Clone the repository:
  git clone https://github.com/EJaworenko/Node-Weaver.git

4. Follow steps 2-6 from the Simple Installation above

## Troubleshooting

### Common Issues

1. "I can't find my Houdini preferences folder"
  - In Houdini, go to File -> Open
  - Type $HOUDINI_USER_PREF_DIR in the address bar at the top and press enter.
  - Right click the address and press "Expand Path"
  - That's your preferences folder!

2. "The tools aren't showing up in Houdini"
  - Double-check that your nodeweaver.json path matches where you put the files
  - Make sure there are no extra spaces in the path
  - Try using forward slashes (/) even on Windows

Need more help? [Open an issue](https://github.com/EJaworenko/Node-Weaver/issues) on our GitHub page!
