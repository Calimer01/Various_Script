import maya.cmds as cmds

#UTILITY

def hookWithCustomPivot(hook, pivot):
    #this function must be used when having and Offset/Hook/Move hierarchy and has as purpose to have the pivot of the hook at the same position as a given pivot
    offset = cmds.listRelatives(hook, parent=True)[0]
    move = cmds.listRelatives(hook, children=True)[0]

    cmds.matchTransform(hook, pivot, pos=True, rot=True)

    #rematch the move to the offstet to avoid having the offset with a different position than the move
    cmds.matchTransform(move, offset, pos=True, rot=True)

    #put a new offset on the hook to have its transforms reset
    newOffset = cmds.duplicate(hook, n=hook+"_offset", parentOnly=True)[0]
    cmds.parent(hook, newOffset)

    #optionnally connect the transform of the given pivot to the hook
    cmds.connectAttr(pivot+".translate", hook+".translate")
    cmds.connectAttr(pivot+".rotate", hook+".rotate")
    cmds.connectAttr(pivot+".scale", hook+".scale")

def extractRelativesTransform(drvjnt, groupName):
    #this function create a group in an offste matching the transforms of a given drvjnt 
    offset = cmds.group(empty=True, n=drvjnt.replace("DrvJnt", "Offset"))
    cmds.matchTransform(offset, drvjnt)
    move = cmds.group(empty=True, n=drvjnt.replace("DrvJnt", "Move"))
    cmds.matchTransform(move, offset)
    cmds.parent(move, offset)

    #get the drvJntOffset and constrain the offset to it
    drvJntOffset = drvjnt + "_Offset"
    MatrixConstraint(drvJntOffset, offset)

    #parent the offset under a given group
    cmds.parent(offset, groupName)

def MatrixConstraint(master, slave):
    #create the matrix nodes
    MultMatX = cmds.createNode("multMatrix", n="MultMatX_"+slave)
    DecMatX = cmds.createNode("decomposeMatrix", n="DecMatX_"+slave)

    MutlMatXOffset = cmds.createNode("multMatrix", n="MultMatXOffset_"+slave)
    DecMatXOffset = cmds.createNode("decomposeMatrix", n="DecMatXOffset_"+slave)

    #connection
    cmds.connectAttr(slave + ".worldMatrix[0]", MutlMatXOffset + ".matrixIn[0]", f=True)
    cmds.connectAttr(master + ".worldInverseMatrix[0]", MutlMatXOffset + ".matrixIn[1]", f=True)
    cmds.connectAttr(MutlMatXOffset + ".matrixSum", DecMatXOffset + ".inputMatrix", f=True)
    cmds.disconnectAttr(MutlMatXOffset + ".matrixSum", DecMatXOffset + ".inputMatrix")
    cmds.delete(MutlMatXOffset)

    cmds.connectAttr(DecMatXOffset + ".inputMatrix", MultMatX + ".matrixIn[0]", f=True)
    cmds.connectAttr(master + ".worldMatrix[0]", MultMatX + ".matrixIn[1]", f=True)
    cmds.connectAttr(slave + ".parentInverseMatrix[0]", MultMatX + ".matrixIn[2]", f=True)

    cmds.connectAttr(MultMatX + ".matrixSum", DecMatX + ".inputMatrix", f=True)

    cmds.connectAttr(DecMatX + ".outputTranslate", slave + ".translate", f=True)
    cmds.connectAttr(DecMatX + ".outputRotate", slave + ".rotate", f=True)
    cmds.connectAttr(DecMatX + ".outputScale", slave + ".scale", f=True)

def changeMatXSlave(offset):
    #the idea is to put the current matrix constraint of a given offset to its children (unplug connection to offset and do it on the move)
    multMatXOffset = cmds.listConnections(offset + ".parentInverseMatrix[0]", type="multMatrix")[0]
    decMatXOffset = cmds.listConnections(offset + ".translate", type="decomposeMatrix")[0]
    move = cmds.listRelatives(offset, children=True)[0]
    cmds.connectAttr(move +".parentInverseMatrix[0]", multMatXOffset + ".matrixIn[2]", f=True)
    cmds.disconnectAttr(decMatXOffset + ".outputTranslate", offset + ".translate")
    cmds.disconnectAttr(decMatXOffset + ".outputRotate", offset + ".rotate")
    cmds.disconnectAttr(decMatXOffset + ".outputScale", offset + ".scale")

    cmds.connectAttr(decMatXOffset + ".outputTranslate", move + ".translate", f=True)
    cmds.connectAttr(decMatXOffset + ".outputRotate", move + ".rotate", f=True)
    cmds.connectAttr(decMatXOffset + ".outputScale", move + ".scale", f=True)

if __name__ == "__main__":
    #example of usage
    selection = cmds.ls(selection=True)
    for s in selection:
        changeMatXSlave(s)