"""Functions for advanced multi-parameter operations in Houdini.

This module provides functionality for performing operations on multiparms that
aren't possible with the default UI. It handles:

- Layer management and organization
- Parameter value manipulation
- Layer swapping and duplication
- Input/output management
- Layer isolation and stacking

Notes:
    Each instance of a multiparm is referred to as a layer in naming conventions.
    When setting up multiparms for swap buttons:
    1. Create layindex# and layendnum# parameters
    2. Set appropriate channels
    3. Configure disable conditions
"""

from typing import Dict, Any
import hou

# Functions used for performing operations on multiparms that aren't possible with the default UI.
# Each instance of a multiparm is referred to as a layer in naming conventions.
"""
When setting up a multiparm to have swap buttons, the following should be done so you can also
have the btnup and btndown buttons disabled if there is no layer above or below to swap with.
1. Create two parms in the multiparm block: layindex# and layendnum# (may need #_# depending on depth)
2. Set both to be hidden and set the channels as follows (both with python as default language):
    ↓ layindex# ↓
hou.pwd().parm(expandString('$CH')).name()[-1]
    ↓ layendnum# ↓
mparmCur = int(hou.pwd().parm(expandString('$CH')).name()[-1])
mparmMax = hou.pwd().parm(expandString('$CH')).parentMultiParm().evalAsInt()
return 1 if mparmCur == mparmMax else 0
3. Set disable when for btnup to { layindex#_# == 1 } and btndown to { layendnum#_# == 1 }
"""

def resetLayer(kwargs):
    """
    Resets all the parms per layer. Checks the parm it is called on to find its
    parent and then resets.

    """
    layerNum = kwargs['script_multiparm_index']
    allParms = kwargs['parm'].parentMultiParm().multiParmInstances()
    if hou.ui.displayMessage("Would you like to reset the parameters for this layer?", buttons=("Yes", "No")) == 1:
        return
    for parm in allParms:
        if int(parm.multiParmInstanceIndices()[-1]) == int(layerNum):
            if parm.parmTemplate().type() == hou.parmTemplateType.Ramp:
                parm.revertToRampDefaults()
            else:
                parm.revertToDefaults()


def duplicateLayer(kwargs):
    """
    Duplicate the UI and nodes of a layer in the mparm.
    UPDATED FOR 20.0: When inserting, uses int(index)+1 instead of int(index).

    """
    node = kwargs['node']
    button = kwargs['parm']
    index = kwargs['script_multiparm_index']

    #Raise error if parameter hierarchy is configured incorrectly
    if not button.tuple().isMultiParmInstance():
        raise hou.NodeWarning('Button is not inside a multiparm block.')

    mparm = button.tuple().parentMultiParm()
    # Get the other parameters inside this multiparm layer so we can duplicate them.
    mparm_template = mparm.parmTemplate().parmTemplates()
    # Create a new mparm instance just after this instance.
    mparm.insertMultiParmInstance(int(index)+1)

    #print(f'to duplicate = {int(index)-1}   |   duplicated = {index}')
    # Duplicate parm data
    prepForSwap(kwargs, mparm_template, index, 1, duplicate=True)


def swapLayers(kwargs: Dict[str, Any], swap_with_next: bool) -> None:
    """Swap the parameters of the layer with one in either direction.

    Args:
        kwargs: Node callback dictionary
        swap_with_next: Whether to swap with next layer (True) or previous (False)

    Notes:
        - Handles all parameter types
        - Preserves parameter relationships
        - Maintains keyframes and expressions
        - Updates UI appropriately

    Raises:
        hou.NodeWarning: If swap is not possible

    Example:
        >>> swapLayers(kwargs, True)  # Swap with next layer
    """
    node = kwargs['node']
    button = kwargs['parm']
    index = int(kwargs['script_multiparm_index'])
    target_swap_dir = int(swap_with_next)*2-1

    #Raise error if parameter hierarchy is configured incorrectly
    if not button.tuple().isMultiParmInstance():
        raise hou.NodeWarning('Button is not inside a multiparm block.')

    mparm = button.tuple().parentMultiParm()
    #Count the number of multiparm instances -> raise errors if swapping is not allowed
    mparm_count = node.parm(mparm.name()).evalAsInt()
    # Get the other parameters inside this multiparm block so we can start swapping.
    mparm_template = mparm.parmTemplate().parmTemplates()

    #Raise errors if trying to swap up on first block, or swap down on last block
    if swap_with_next is True and index == mparm_count:
            raise hou.NodeWarning('No value below to swap with.')
    elif swap_with_next is False and index == 1:
            raise hou.NodeWarning('No value above to swap with.')

    prepForSwap(kwargs, mparm_template, index, target_swap_dir)


def prepForSwap(kwargs, mparm_template:tuple, index:int, swap_dir:int, duplicate:bool=False):
    """
    Find the parms between 1 layer and the one being swapped with in order to switch values.
    mparm_template is the tuple of all the parms in the multiparm block. (hou.parmTemplate)

    """
    node = kwargs['node']
    debug = 0

    for i, parm_template in enumerate(mparm_template):
        # If the current parameter is of a valid type, check if it has channels
        if parm_template.type() in [
                hou.parmTemplateType.Int,
                hou.parmTemplateType.Float,
                hou.parmTemplateType.String,
                hou.parmTemplateType.Toggle,
                hou.parmTemplateType.Menu]:

            # Note that vector channels are suffixed after multiparm index - 'vector_#x' instead of 'vector_x#'
            parm_name = parm_template.name()
            parm_swap_name = parm_template.name()
            nesting_depth = int(kwargs["script_multiparm_nesting"])

            # Replace # with multiparm numbers, leaving the last # to be replaced depending on the swap direction
            if debug == 1:
                print(f'###########################################\nINITIAL:\nname1 = {parm_name}   |   name2 = {parm_swap_name}   |   parmTemplate = {parm_template}')
            for i in range(nesting_depth-1):
                # Create the name of the kwargs entry that correctly relates to the multiparm index.
                # The outermost index has the biggest number, while the innermost one doesn't have a number.
                index_find = nesting_depth-i
                mparm_index_name = f'script_multiparm_index{index_find}'
                if index_find == 1:
                    mparm_index_name = 'script_multiparm_index'
                index_for_replacing = kwargs[mparm_index_name]
                parm_name = parm_name.replace('#',f'{index_for_replacing}', 1) # Replace the first # with number from the main mparm
                parm_swap_name = parm_swap_name.replace('#',f'{index_for_replacing}', 1) # Replace the first # with number from the main mparm

            parm_name = parm_name.replace('#',f'{index}')
            parm_swap_name = parm_swap_name.replace('#',f'{int(index)+int(swap_dir)}')
            if debug == 1:
                print(f'AFTER RENAMING:\nname1 = {parm_name}   |   name2 = {parm_swap_name}')

            # If the parm is a vector, check if it has components then swap each one.
            if parm_template.numComponents() > 1:
                vec_comp = 'x'
                for c in range(parm_template.numComponents()):
                    if parm_template.namingScheme() == hou.parmNamingScheme.XYZW:
                        vec_comp = ['x','y','z','w'][c]
                    elif parm_template.namingScheme() == hou.parmNamingScheme.RGBA:
                        vec_comp = ['r','g','b','a'][c]
                    elif parm_template.namingScheme() == hou.parmNamingScheme.UVW:
                        vec_comp = ['u','v','w'][c]
                    elif parm_template.namingScheme() == hou.parmNamingScheme.Base1:
                        vec_comp = ['1','2','3','4'][c]
                    parm_name_vec = parm_name+vec_comp
                    parm_swap_name_vec = parm_swap_name+vec_comp
                    #print(f'name1 = {parm_name}   |   name2 = {parm_swap_name}')
                    swapValues(kwargs, parm_name_vec, parm_swap_name_vec, duplicate, debug)

            # If the parm is not a vector, simply swap the values.
            elif parm_template.numComponents() == 1: # If the parm has 1 value
                #print(f'name1 = {parm_name}   |   name2 = {parm_swap_name}')
                swapValues(kwargs, parm_name, parm_swap_name, duplicate, debug)

        #if a folder is found, determine if it's a nested multiparm
        elif parm_template.type() == hou.parmTemplateType.Folder:
            # If it is, compare the number of instances in each multiparm
            if parm_template.folderType() == hou.folderType.MultiparmBlock:
                get_nested_mparm = parm_template.name().replace('#',f'{index}')
                get_swap_nested_mparm = parm_template.name().replace('#',f'{index+swap_dir}')
                nested_mparm_count = node.evalParm(get_nested_mparm)
                swap_nested_mparm_count = node.evalParm(get_swap_nested_mparm)

                # If both multiparms have the same number of instances, swap nested parameter values
                if nested_mparm_count == swap_nested_mparm_count:
                    for j in range(nested_mparm_count):
                        parm_a = node.parm(get_nested_mparm).parmTemplate().parmTemplates()[j-1].name().replace('#',f'{index}')
                        parm_b = node.parm(get_swap_nested_mparm).parmTemplate().parmTemplates()[j-1].name().replace('#',f'{index+swap_dir}')
                        swapValues(kwargs, parm_a, parm_b, duplicate, debug)
                # Otherwise, save values to a temporary holder
                else:
                    temp_a = list()
                    temp_b = list()
                    for j in range(nested_mparm_count):
                        nested_parm = node.parm(get_nested_mparm).parmTemplate().parmTemplates()[j-1].name().replace('#',f'{index}')
                        if len(node.parm(nested_parm).keyframes()) > 0:
                            temp_a.append(node.parm(nested_parm).keyframes())
                        else:
                            temp_a.append(node.parm(nested_parm).rawValue())

                    for j in range(swap_nested_mparm_count):
                        nested_parm = node.parm(get_swap_nested_mparm).parmTemplate().parmTemplates()[j-1].name().replace('#',f'{index+swap_dir}')
                        if len(node.parm(nested_parm).keyframes()) > 0:
                            temp_b.append(node.parm(nested_parm).keyframes())
                        else:
                            temp_b.append(node.parm(nested_parm).rawValue())

                    # Initialize number of multiparm blocks
                    swapValues(kwargs, get_nested_mparm, get_swap_nested_mparm, duplicate, debug)

                    # And update each block from the temporary holders
                    for k in range(swap_nested_mparm_count):
                        parm_a = node.parm(get_nested_mparm).parmTemplate().parmTemplates()[k-1].name().replace('#',f'{index}')
                        node.parm(parm_a).deleteAllKeyframes()
                        try:
                            node.parm(parm_a).set(temp_b[k])
                        except:
                            node.parm(parm_a).setKeyframes(temp_b[k])
                    for k in range(nested_mparm_count):
                        parm_b = node.parm(get_swap_nested_mparm).parmTemplate().parmTemplates()[k-1].name().replace('#',f'{index+swap_dir}')
                        node.parm(parm_b).deleteAllKeyframes()
                        try:
                            node.parm(parm_b).set(temp_a[k])
                        except:
                            node.parm(parm_b).setKeyframes(temp_a[k])

            #if it's not a multiparm, dive inside and swap each nested parameter
            else:
                prepForSwap(kwargs, parm_template.parmTemplates(), index, swap_dir, duplicate)


def swapValues(kwargs, parm_a_name:str, parm_b_name:str, duplicate:bool=False, debug:int=0):
    """
    When supplied with two parameter names, this function will swap their values.

    """
    node = kwargs['node']
    parm_a = node.parm(parm_a_name)
    parm_b = node.parm(parm_b_name)

    #print(f'a = {a}   |   parm_a = {parm_a}   |   b = {b}   |   parm_b = {parm_b}')
    if len(parm_a.keyframes()) == 0:
        #if both params have no keyframes
        if len(parm_b.keyframes()) == 0:
            parm_a_value = parm_a.rawValue()
            parm_b_value = parm_b.rawValue()
            if parm_a_value == 'on':
                parm_a_value = 1
            elif parm_a_value == 'off':
                parm_a_value = 0
            if parm_b_value == 'on':
                parm_b_value = 1
            elif parm_b_value == 'off':
                parm_b_value = 0
            if duplicate == False:
                parm_a.set(parm_b_value)
                parm_b.set(parm_a_value)
            else:
                if debug == 1:
                    print(f'a = {parm_a}   |   parm_a_value = {parm_a_value}   |   b = {parm_b}   |   parm_b_value = {parm_b_value}')
                parm_a.set(parm_a_value)
                parm_b.set(parm_a_value)

        #if A has no keyframes but B does, b cant have keyframes if duplicated
        else:
            parm_a_value = parm_a.rawValue()
            parm_b_value = parm_b.keyframes()
            if parm_a_value == 'on':
                parm_a_value = 1
            elif parm_a_value == 'off':
                parm_a_value = 0
            if duplicate == False:
                parm_a.setKeyframes(parm_b_value)
                parm_b.deleteAllKeyframes()
                parm_b.set(parm_a_value)
            else:
                if debug == 1:
                    print(f'a = {parm_a}   |   parm_a_value = {parm_a_value}   |   b = {parm_b}   |   parm_b_value = {parm_b_value}')
                parm_a.set(parm_a_value)
                parm_b.set(parm_a_value)

    else:
        #if A has keyframes but B doesn't
        if len(parm_b.keyframes()) == 0:
            parm_a_value = parm_a.keyframes()
            parm_b_value = parm_b.rawValue()
            if parm_b_value == 'on':
                parm_b_value = 1
            elif parm_b_value == 'off':
                parm_b_value = 0
            if duplicate == False:
                parm_a.deleteAllKeyframes()
                parm_a.set(parm_b_value)
                parm_b.setKeyframes(parm_a_value)
            else:
                if debug == 1:
                    print(f'a = {parm_a}   |   parm_a_value = {parm_a_value}   |   b = {parm_b}   |   parm_b_value = {parm_b_value}')
                parm_a.setKeyframes(parm_a_value)
                parm_b.setKeyframes(parm_a_value)

        #if both params have keyframes
        else:
            parm_a_value = parm_a.keyframes()
            parm_b_value = parm_b.keyframes()
            if duplicate == False:
                parm_a.deleteAllKeyframes()
                parm_a.setKeyframes(parm_b_value)
                parm_b.deleteAllKeyframes()
                parm_b.setKeyframes(parm_a_value)
            else:
                if debug == 1:
                    print(f'a = {parm_a}   |   parm_a_value = {parm_a_value}   |   b = {parm_b}   |   parm_b_value = {parm_b_value}')
                parm_a.setKeyframes(parm_a_value)
                parm_b.deleteAllKeyframes()
                parm_b.setKeyframes(parm_a_value)