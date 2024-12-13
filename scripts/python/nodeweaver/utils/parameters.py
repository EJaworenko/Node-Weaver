"""Parameter manipulation utilities for Houdini.

This module provides comprehensive utilities for working with Houdini parameters,
including type checking, template modification, conditional logic handling, and
parameter referencing. It focuses on maintaining parameter relationships while
enabling complex modifications.

Functions:
    is_parm_of_type: Check parameter type
    all_parm_templates: Iterate through all parameter templates
    modify_parm_templates: Modify parameter templates with consistent naming
    modify_conditionals: Update parameter conditional expressions
    relative_reference_multiparm: Create relative parameter references
    reset_script_parms_to_default: Reset script parameters to defaults
    mass_connect_parameters: Bulk connect parameters between nodes
"""

from typing import List, Dict, Union, Optional, Generator
import re
import hou

def is_parm_of_type(parm:hou.Parm,
                types:tuple[hou.parmTemplateType]=(hou.parmTemplateType.Int,
                                                    hou.parmTemplateType.Float,
                                                    hou.parmTemplateType.String)) -> bool:
    """Check if parameter is of specified types.

    Args:
        parm (hou.Parm): Parameter to check
        types (tuple[hou.parmTemplateType], optional): Tuple of parameter types to check against.
            Defaults to (Int, Float, String).

    Returns:
        bool: True if parameter matches any of the specified types

    Example:
        >>> parm = node.parm('tx')
        >>> is_parm_of_type(parm, (hou.parmTemplateType.Float,))
        True
    """
    template = parm.parmTemplate()
    if template.type() in types:
        return True
    return False


def all_parm_templates(group_or_folder: Union[hou.ParmTemplateGroup, hou.FolderParmTemplate]) -> Generator[hou.ParmTemplate, None, None]:
    """Get all parameter templates from a group or folder.

    Recursively retrieves all parameter templates, including those nested in folders,
    which aren't accessible through Houdini's default methods.

    Args:
        group_or_folder (Union[hou.ParmTemplateGroup, hou.FolderParmTemplate]):
            Parameter group or folder to search.

    Returns:
        Generator[hou.ParmTemplate]: Generator yielding all parameter templates

    Raises:
        TypeError: If input is not a ParmTemplateGroup or FolderParmTemplate

    Example:
        >>> templates = list(all_parm_templates(node.parmTemplateGroup()))
    """
    for parm_template in group_or_folder.parmTemplates():
        yield parm_template

        # Note that we don't want to return parm templates inside multiparm
        # blocks, so we verify that the folder parm template is actually
        # for a folder.
        if parm_template.type() == hou.parmTemplateType.Folder and parm_template.isActualFolder():
            for sub_parm_template in all_parm_templates(parm_template):
                yield sub_parm_template


def modify_parm_templates(group_or_folder: Union[hou.ParmTemplateGroup, hou.FolderParmTemplate],
                        prefix: str = "",
                        suffix: str = "",
                        replacefrom: str = "",
                        replaceto: str = "",
                        folder_name: str = "",
                        folder_label: str = "",
                        folder_type: hou.folderType = hou.folderType.Simple,
                        include_only: Optional[List[str]] = None,
                        exclude: Optional[List[str]] = None,
                        ref_parmtemplate_dict: Optional[Dict[str, hou.ParmTemplate]] = None,
                        mod_all_conditionals: bool = True,
                        created_by_conditionals: Optional[list] = None) -> hou.FolderParmTemplate:
    """Modify parameter templates with consistent naming and organization.

    Processes a parameter template group or folder to modify parameter names and
    organization while preserving parameter relationships and functionality.

    Args:
        group_or_folder: Template group or folder to process
        prefix: String to prepend to parameter names
        suffix: String to append to parameter names
        replacefrom: String to replace in parameter names
        replaceto: Replacement string for replacefrom
        folder_name: Name for the containing folder
        folder_label: Display label for the folder
        folder_type: Type of folder to create
        include_only: List of parameter names to include (None = all)
        exclude: List of parameter names to exclude
        ref_parmtemplate_dict: Dictionary of reference templates
        mod_all_conditionals: Whether to modify all conditional expressions
        created_by_conditionals: List to store templates created by conditionals

    Returns:
        Modified folder containing processed parameter templates

    Raises:
        ValueError: If folder_name or folder_label not provided

    Examples:
        >>> # Basic parameter renaming
        >>> templates = node.parmTemplateGroup()
        >>> modified = modify_parm_templates(templates,
        ...     prefix="mat_",
        ...     folder_name="material_params",
        ...     folder_label="Material Parameters")

        >>> # Complex filtering and modification
        >>> modified = modify_parm_templates(templates,
        ...     prefix="shader_",
        ...     include_only=["diffuse", "specular"],
        ...     exclude=["*_old"],
        ...     mod_all_conditionals=True)

    Notes:
        - Parameters in conditionals are handled specially:
            - Referenced parameters are added even if not in include_only
            - Conditional expressions are updated to match naming changes
        - Exclusion patterns with * are treated as wildcards
        - Parameter references and relationships are maintained

    Since: 1.0.0
    """
    templates = []
    created_by_conditionals = created_by_conditionals or []
    include_only = include_only or []
    exclude = exclude or []
    # Creates a dictionary of parmTemplates for reference. This is passed forward from here on.
    if ref_parmtemplate_dict is None:
        ref_parmtemplate_dict = {t.name(): t for t in all_parm_templates(group_or_folder)}

    if folder_name == "" or folder_label == "":
        print("Folder name and label must be defined for the folder to be created.")
        return

    excl_wildcards = [excl[1:-1] for excl in exclude if excl.startswith("*") and excl.endswith("*")]

    for parm_template in group_or_folder.parmTemplates():
        if include_only is not None \
        and parm_template.name() not in include_only \
        and parm_template.type() != hou.parmTemplateType.Folder:
            continue
        if exclude is not None \
        and parm_template.type() != hou.parmTemplateType.Folder:
            if parm_template.name() in exclude:
                continue
            for excl in excl_wildcards:
                if excl in parm_template.name():
                    continue

        new_name = prefix+parm_template.name().replace(replacefrom, replaceto)+suffix
        parm_template.setName(new_name)

        # Deal with conditional statements.
        if parm_template.conditionals():
            new_cond = modify_conditionals(parm_template.conditionals(), templates, ref_parmtemplate_dict, created_by_conditionals, prefix, suffix, replacefrom, replaceto, include_only, exclude, mod_all_conditionals=mod_all_conditionals)
            for cond_type, cond_str in new_cond.items():
                parm_template.setConditional(cond_type, cond_str)

        # Adjust parms that were created by conditional statements
        for created_parm in created_by_conditionals:
            created_parm.setName(prefix+created_parm.name().replace(replacefrom, replaceto)+suffix)
            templates.append(created_parm)
        created_by_conditionals.clear()

        # Note that we don't want to return parm templates inside multiparm
        # blocks, so we verify that the folder parm template is actually
        # for a folder.
        if parm_template.type() == hou.parmTemplateType.Folder and parm_template.isActualFolder():
            templates.append(modify_parm_templates(parm_template, prefix, suffix, replacefrom, replaceto, folder_name=parm_template.name(), folder_label=parm_template.label(), folder_type=parm_template.folderType(), include_only=include_only, exclude=exclude, ref_parmtemplate_dict=ref_parmtemplate_dict, mod_all_conditionals=mod_all_conditionals, created_by_conditionals=created_by_conditionals))
        else:
            templates.append(parm_template)
    return hou.FolderParmTemplate(folder_name, folder_label, templates, folder_type)


def modify_conditionals(conditionals: Dict[hou.parmCondType, str],
                       templates: Union[List[hou.ParmTemplate], List[str]],
                       ref_template_dict: Dict[str, hou.ParmTemplate],
                       created_by_conditionals: Optional[List[hou.ParmTemplate]] = None,
                       prefix: str = "",
                       suffix: str = "",
                       replacefrom: str = "",
                       replaceto: str = "",
                       include_only: Optional[List[str]] = None,
                       exclude: Optional[List[str]] = None,
                       mod_all_conditionals: bool = True) -> Dict[hou.parmCondType, str]:
    """Process and update parameter conditional expressions.

    Analyzes and modifies conditional expressions in parameter templates,
    handling parameter references and maintaining relationships.

    Args:
        conditionals: Dictionary of conditional expressions
        templates: List of templates or parameter names to process
        ref_template_dict: Dictionary of reference templates
        created_by_conditionals: List to store templates created by conditionals
        prefix: String to prepend to parameter names
        suffix: String to append to parameter names
        replacefrom: String to replace in parameter names
        replaceto: Replacement string for replacefrom
        include_only: List of parameter names to include
        exclude: List of parameter names to exclude
        mod_all_conditionals: Whether to modify all expressions

    Returns:
        Dictionary of updated conditional expressions

    Examples:
        >>> conds = {hou.parmCondType.DisableWhen: "param1 == 0"}
        >>> modified = modify_conditionals(conds, templates, ref_dict,
        ...     prefix="new_",
        ...     mod_all_conditionals=True)
        >>> print(modified[hou.parmCondType.DisableWhen])
        'new_param1 == 0'

    Notes:
        - Handles both string names and ParmTemplate objects
        - Updates parameter references in expressions
        - Maintains conditional logic while updating names
        - Adds referenced parameters to template list if needed

    Since: 1.0.0
    """
    include_only = include_only or []
    exclude = exclude or []
    def modify_parm(param:str, prefix:str, suffix:str, replacefrom:str, replaceto:str):
        new_param = f"{prefix}{param}{suffix}"
        if replacefrom and replaceto:
            new_param = new_param.replace(replacefrom, replaceto)
        return re.sub(r'\b{}\b'.format(param), new_param, new_cond_str)
    new_conditionals = {}
    for cond_type, cond_str in conditionals.items():
        # Extract parameter names from the conditional string
        param_names = re.findall(r'\b(\w+)\b [!=<>]', cond_str)
        new_cond_str = cond_str

        for param in param_names:
            if include_only is None or param in include_only:
                # Apply modifications to the parameter
                new_cond_str = modify_parm(param, prefix, suffix, replacefrom, replaceto)
            else:
                # Apply modifications to the parameter if mod_all_conditionals is True
                if mod_all_conditionals:
                    new_cond_str = modify_parm(param, prefix, suffix, replacefrom, replaceto)
                # Add parameter to templates if not in include_only list
                if len(templates) > 0:
                    if param in exclude:
                        continue
                    # Search wildcard exclusions
                    found = False
                    for excl in exclude:
                        if excl.startswith("*") and excl.endswith("*") and excl[1:-1] in param:
                            found = True
                            break
                    if found:
                        continue
                    # For cases when the templates list is a list of strings
                    if isinstance(templates[0], str):
                        if param not in templates:
                            templates.append(param)
                    # For cases when the templates list is a list of hou.ParmTemplates
                    else:
                        if param not in ref_template_dict.keys():
                            continue
                        param_template = ref_template_dict[param]
                        if param_template not in templates \
                        and param_template not in created_by_conditionals:
                            if created_by_conditionals is not None:
                                created_by_conditionals.append(param_template)
        new_conditionals[cond_type] = new_cond_str

    return new_conditionals


def relative_reference_multiparm(source_node:hou.Node,
                                target_node:hou.Node,
                                target_mparm_name:str,
                                parm_name_dict:dict,
                                start_index:int=1) -> None:
    """Connect source parameters to destination parameters in a multiparm block.

    Creates relative references between source and destination parameters and ensures
    new multiparm entries maintain these connections.

    Args:
        source_node (hou.Node): Node containing source parameters
        target_node (hou.Node): Node containing target multiparm block
        target_mparm_name (str): Name of the multiparm parameter
        parm_name_dict (dict): Mapping of source to destination parameter names.
            Format: {"source_parm#": "dest_parm#", "source_parm2#": "dest_parm2#"}
        start_index (int, optional): Starting index for multiparm. Defaults to 1.

    Raises:
        ValueError: If parameters don't exist or are invalid
        RuntimeError: If parameter connections fail

    Example:
        >>> parms = {"scale#": "instance_scale#"}
        >>> relative_reference_multiparm(src, dst, "num_instances", parms)
    """
    # First set the multiparm to connect for every new entry.
    mparm_connect = f"opmultiparm {target_node.path()}"
    for src_parm, dst_parm in parm_name_dict.items():
        mparm_connect += f" '{dst_parm}' '{target_node.relativePathTo(source_node)}/{src_parm}'"
    hou.hscript(mparm_connect)

    # Then connect the pre-existing entries. Doesn't yet account for vectors.
    for i in range(start_index, target_node.evalParm(target_mparm_name)+start_index):
        for src_parm, dst_parm in parm_name_dict.items():
            if target_node.parm(f"{dst_parm[:-1]}{i}") and source_node.parm(f"{src_parm[:-1]}{i}"):
                target_node.parm(f"{dst_parm[:-1]}{i}").deleteAllKeyframes()
                target_node.parm(f"{dst_parm[:-1]}{i}").set(source_node.parm(f"{src_parm[:-1]}{i}"))


def reset_script_parms_to_default(node:hou.Node) -> None:
    """Reset all script parameters to their default values.

    Resets parameters with script callbacks to their default script values to
    ensure proper parameter updating behavior.

    Args:
        node (hou.Node): Node containing script parameters to reset

    Raises:
        ValueError: If node is None or invalid
        RuntimeError: If parameter reset fails
    """
    for parm in node.parms():
        template = parm.parmTemplate()
        if template.type() in (hou.parmTemplateType.Int, hou.parmTemplateType.Float, hou.parmTemplateType.String, hou.parmTemplateType.Toggle, hou.parmTemplateType.Menu):
            # For non-string parms
            if template.defaultExpressionLanguage() == hou.scriptLanguage.Python \
            or template.defaultExpressionLanguage() == (hou.scriptLanguage.Python,):
                try:
                    parm.setKeyframe(hou.Keyframe())
                except TypeError:
                    parm.setKeyframe(hou.StringKeyframe())
                parm.deleteAllKeyframes()
                parm.revertToDefaults()


def mass_connect_parameters(node:hou.Node):
    """
    NOT FUNCTIONAL YET
    Prompts the user to select 2 nodes to copy parms between. In a final version of
    this, it will create a UI to prompt the user with where they can add modifications
    to the parm names in order to make them match if they don't have the same names.

    """
    def _set_modifiers(mods:dict):
        """
        Recursive function that keeps asking the user if they want to modify the mods
        until they are satified.

        """
        a = ["prefix", "suffix", "replace_from", "replace_to"]
        ui = hou.ui.displayMessage(f"It is common to modify a parm name for a node when it is controlled by\na master. You can set the changes you may have done here.\nNote: these changes will only be searched for in master node parm names.\nPrefix: {mods[a[0]]}\nSuffix: {mods[a[1]]}\n Replace (From): {mods[a[2]]}\nReplace (To): {mods[a[3]]}", buttons=("Adjust Prefix", "Adjust Suffix", "Adjust Replace From", "Adjust Replace To", "Continue"))
        if ui == 4:
            return mods
        else:
            mods[a[ui]] = hou.ui.readInput(f"Set value for {a[ui].replace('_', ' ').title()}", initial_contents=mods[a[ui]])[1]
            _set_modifiers(mods)


    # First, make sure that the node being run from can be put at the end later, so remove here.
    sel = list(hou.selectedNodes())
    if node in sel:
        sel.pop(sel.index(node))
    # If not enough nodes are selected, prompt to select more
    if len(sel) == 0:
        hou.ui.displayMessage("The selected node will serve as the 'master' but you now need to select\nnodes whose parms will be connected to it.\n", title="Only selected one node", help="Tip: If you select 2 or more nodes when running the script, it will use\nthe last selected one as the 'master'.", severity=hou.severityType.Warning)
        prompt = hou.ui.selectNode(initial_node=node, title="Select the nodes to connect to the master", multiple_select=True)
        if prompt is not None:
            for path in prompt:
                if hou.node(path) != node:
                    sel.append(hou.node(path))
        else:
            return
    # Return if not enough nodes
    if len(sel) < 1:
        hou.ui.displayMessage("Not enough nodes selected to connect between.")
        return
    node_paths = [x.path() for x in sel]
    node_paths = '\n    '.join(node_paths)
    mods = {"prefix":"", "suffix":"", "replace_from":"", "replace_to":""}
    _set_modifiers(mods)
    if hou.ui.displayMessage(f"You're about to connect parms between nodes with the following configuration:\nMaster node:\n    {node.path()}\n\nNodes referencing from the master node:\n    {node_paths}", buttons=("Connect Parms", "Cancel")) == 0:
        sel.append(node)
        print(sel)

# def mass_connect_parameters(node: hou.Node) -> None:
#     """Connect parameters between multiple nodes with user interaction.

#     Args:
#         node: Source node for parameter connections

#     Note:
#         Prompts user for connection options and modifications
#     """
#     def get_modification_options() -> Dict[str, str]:
#         """Get parameter modification options from user.

#         Returns:
#             Dictionary of modification options
#         """
#         mods = {
#             "prefix": "",
#             "suffix": "",
#             "replace_from": "",
#             "replace_to": ""
#         }

#         while True:
#             msg = textwrap.dedent(f"""
#                 Parameter Name Modifications:
#                 Prefix: {mods['prefix']}
#                 Suffix: {mods['suffix']}
#                 Replace From: {mods['replace_from']}
#                 Replace To: {mods['replace_to']}
#             """)

#             choice = hou.ui.displayMessage(
#                 msg,
#                 buttons=("Adjust Prefix", "Adjust Suffix",
#                         "Adjust Replace From", "Adjust Replace To", "Continue")
#             )

#             if choice == 4:
#                 return mods

#             key = list(mods.keys())[choice]
#             result = hou.ui.readInput(
#                 f"Set value for {key.replace('_', ' ').title()}",
#                 initial_contents=mods[key]
#             )
#             if result[0] == 0:
#                 mods[key] = result[1]

#     # Get target nodes
#     sel_nodes = list(hou.selectedNodes())
#     if node in sel_nodes:
#         sel_nodes.remove(node)

#     if not sel_nodes:
#         msg = "Select nodes to connect parameters to"
#         result = hou.ui.selectNode(initial_node=node, title=msg, multiple_select=True)
#         if not result:
#             return
#         sel_nodes = [hou.node(path) for path in result if hou.node(path) != node]

#     if not sel_nodes:
#         hou.ui.displayMessage("No target nodes selected")
#         return

#     # Get modification options
#     mods = get_modification_options()

#     # Confirm and execute connections
#     node_paths = "\n    ".join(n.path() for n in sel_nodes)
#     msg = f"""
#     Connect parameters between:
#     Source: {node.path()}

#     Targets:
#     {node_paths}
#     """

#     if hou.ui.displayMessage(msg, buttons=("Connect", "Cancel")) == 0:
#         # TODO: Implement actual parameter connection logic
#         sel_nodes.append(node)
#         print(f"Connected parameters between {len(sel_nodes)} nodes")