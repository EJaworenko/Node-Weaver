### Node Weaver is a toolset that is intended to ease the workflow of Houdini TDs. Whether they are building tools or customizing Houdini.
# Making Tools
## Tool Maker Tools
A tool for making tools, automating tedious processes and improving TD quality of life. Included is an HDA with the following functions:
- Generator for menu and action button scripts
- Convert Copy to Points to Instancing: Create the necessary nodes to convert a copy to points setup into an instanced setup. 
There is also a Node Weaver shelf with:
- A shelf tool to print out all callback scripts, default value expressions, and menu scripts in a node.  
A right-click menu item that makes it possible to set node colors with the color wheel window.  
# Customizing Houdini
## Color Palette Configurator HDA
A convenience utility for making adjustments or additions to the 36 node colours you get in the network view palette by default in Houdini. By default it is quite tedious to modify. This tool allows you to rearrange colors, change them with ease, and add new ones through a few methods (manual, gradient, and hex-code). The gradient can be created manually, by sampling the screen, or by using a cosine formula that is surprisingly good at generating pleasing gradients (Credit to Inigo Quilez for the formula https://iquilezles.org/articles/palettes/).
## Custom Node Shape Creator HDA
While we use nodes all the time in Houdini, the process of creating custom shapes for them is not well documented nor straightforward. Credit to Simon Fiedler and Bastian Schiffer for doing the initial exploration year ago. https://vimeo.com/221182957
The aim of this tool is to make the process of creating custom node shapes as easy as possible. Examples are provided for educational purposes and to show the capabilities of the tool. Alongside being able to adjust any element of the node shape, you can also visualize the tool in a large variety of ways to make sure it looks exactly how you want it to when you export. 
The documentation has information about where to put your custom node shape files, how to make them blend well with the default node shapes, and how to deal with wire curvature. The tool itself was designed in a way to minimize the actual steps an artist takes to create their shapes and tries to automate things where possible.
With any luck, we should be seeing more custom node shapes in the future!
## Inspect Node Shape File HDA
If you want to analyze a node shape file, this will open it and allow you to see the prims that make it up. You can see the stats of it, modify elements, and even feed it back into the Node Shape Creator to output a new node with the changes you made. 
This node has a bunch of stats about the default node shapes in Houdini as well. You can use these when creating your own node shapes if you want to make sure that your shapes integrate well!
# Installation
- In Progress -
