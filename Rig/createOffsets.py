import maya.cmds as cmds

#create a function that simply create a group, rename it base on the joint, match all its transform and then parent it under "EyeRelay_Offset_GRP"

def createOffset(joint):
    offset = cmds.group(empty=True, name=joint.replace("Bind", "Loc")+"_Offset")
    pin = joint.replace("Bind", "Pin")
    cmds.matchTransform(offset, joint)
    cmds.parent(offset, "EyeLid_Loc_GRP")
    MatrixConstraint(pin, offset)
    return offset

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

if __name__ == "__main__":
    selection = cmds.ls(sl=True)
    for s in selection:
        createOffset(s)