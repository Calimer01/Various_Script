import maya.cmds as cmds

def renamer(list, mode, argument):
    #there is 3 mode "prefix", "suffix", "replace"
    if mode == 0:  #prefix
        for item in list:
            cmds.rename(item, argument + item)
    elif mode == 1:  #suffix
        for item in list:
            cmds.rename(item, item + argument)
    elif mode == 2:  #replace
        for item in list:
            try:
                cmds.rename(item, item.replace(argument[0], argument[1]))
            except:
                pass

renamer(cmds.ls(selection=True), mode=2, argument=["Cluster", "Deformer"])