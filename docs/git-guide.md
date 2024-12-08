<!-- omit in toc -->
# Git Guide for Beginners

> [← Back to main documentation](../README.md)

I've provided this guide because as someone who came out of arts, I remember struggling with Github projects and how to use them in my own work. I hope it helps.

<!-- omit in toc -->
## Table of Contents
- [What is Git?](#what-is-git)
  - [Git vs. GitHub: What's the Difference?](#git-vs-github-whats-the-difference)
- [Why is Node Weaver on Github?](#why-is-node-weaver-on-github)
- [Installing Git](#installing-git)
  - [Windows](#windows)
  - [Mac](#mac)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
- [Common Git Tasks](#common-git-tasks)
  - [Getting Node Weaver for the First Time](#getting-node-weaver-for-the-first-time)
  - [Updating Node Weaver](#updating-node-weaver)
  - [What If You Made Changes?](#what-if-you-made-changes)
- [Visual Git Tools](#visual-git-tools)
- [Troubleshooting](#troubleshooting)
  - ["Git isn't recognized as a command"](#git-isnt-recognized-as-a-command)
  - ["Permission denied" Errors](#permission-denied-errors)
  - ["Refusing to merge unrelated histories"](#refusing-to-merge-unrelated-histories)
  - [Changes Not Downloading](#changes-not-downloading)
  - [Still Stuck?](#still-stuck)

## What is Git?

Git is like a very powerful "Save As" for your projects. It:
- Keeps track of all changes you make
- Lets you go back to any previous version
- Helps you get updates without losing your changes
- Makes it easy to share improvements with others

### Git vs. GitHub: What's the Difference?
- **Git** is the tool that tracks changes on your computer
- **GitHub** is the website where people share their Git projects
- In other words:
  - Git = The tool you write with
  - GitHub = The library where you share your writing

## Why is Node Weaver on Github?

Downloading Node Weaver using Git gives you several benefits:
1. **Easy Updates**: Get new features and fixes with a single command
2. **Safe Customization**: Make your own changes without breaking updates
3. **Contribution**: Share your improvements if you want to
4. **History**: Track changes you make to your tools

## Installing Git

### Windows
1. Download Git from [git-scm.com](https://git-scm.com/download/windows)
2. Run the installer
3. Use these recommended settings:
   - When asked about line ending conversions, choose "Checkout as-is, commit as-is"
   - For the default editor, choose "Visual Studio Code" if you have it, or "Notepad" if not
   - For everything else, the defaults are fine

### Mac
1. Open Terminal
2. Type `git --version`
3. If Git isn't installed, macOS will prompt you to install it

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install git
```

## Common Git Tasks

### Getting Node Weaver for the First Time
```bash
# 1. Open Terminal (Mac/Linux) or Git Bash (Windows)
# 2. Go to where you want to install. For example, the Documents folder
cd Documents

# 3. Get Node Weaver
git clone https://github.com/EJaworenko/Node-Weaver.git
```

### Updating Node Weaver
```bash
# 1. Open Terminal/Git Bash in your Node Weaver folder
# 2. Get updates
git pull origin main
```

### What If You Made Changes?
If you've modified any Node Weaver files and try to update, Git will warn you. Here's what to do:

1. **If you want to keep your changes**:
   ```bash
   # Save your changes temporarily
   git stash

   # Get updates
   git pull origin main

   # Bring your changes back
   git stash pop
   ```

2. **If you want to discard your changes**:
   ```bash
   # Reset everything to original state
   git reset --hard

   # Get updates
   git pull origin main
   ```

## Visual Git Tools

If you prefer using a visual interface instead of commands, try these free tools:
- [GitHub Desktop](https://desktop.github.com/) - Simplest option, works with GitHub
- [Sourcetree](https://www.sourcetreeapp.com/) - More powerful, but more complex
- [Visual Studio Code](https://code.visualstudio.com/) - Good if you also write code

## Troubleshooting

### "Git isn't recognized as a command"
- Windows: Reinstall Git and make sure to select "Add to PATH" during installation
- Mac/Linux: Make sure Git is installed by running `git --version`

### "Permission denied" Errors
- Make sure you're not in a protected folder (like Program Files on Windows)
- Try running your terminal/Git Bash as administrator

### "Refusing to merge unrelated histories"
```bash
# Use this command instead of regular pull
git pull origin main --allow-unrelated-histories
```

### Changes Not Downloading
1. Make sure you're connected to the internet
2. Try forcing an update:
   ```bash
   git fetch --all
   git reset --hard origin/main
   ```

### Still Stuck?
1. Check if others had the same issue in the [Issues section](https://github.com/EJaworenko/Node-Weaver/issues)
2. If not, feel free to [open a new issue](https://github.com/EJaworenko/Node-Weaver/issues/new)
3. Include:
   - What you were trying to do
   - The exact error message
   - What you've tried so far

Remember: Everyone was a beginner once. Don't be afraid to ask for help!