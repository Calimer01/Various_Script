import maya.cmds as cmds

def blendRotation(Joint):
    #get the current connection in the rotate of the joint
    decMatX = cmds.listConnections(Joint + ".rotateX", s=True)[0]

    #create a multiplyDivide node to blend the rotations
    multNode = cmds.shadingNode("multiplyDivide", n=Joint + "_blendRotate_mult", asUtility=True)
    cmds.connectAttr("Settings_Arm_{side}.sleevesTwist".format(side=Joint.split("_")[-2]), multNode + ".input2X", f=True)
    cmds.connectAttr("Settings_Arm_{side}.sleevesTwist".format(side=Joint.split("_")[-2]), multNode + ".input2Y", f=True)
    cmds.connectAttr("Settings_Arm_{side}.sleevesTwist".format(side=Joint.split("_")[-2]), multNode + ".input2Z", f=True)

    #deconnect the existing connection if it exists and then connect it to the multiplyDivide node
    if decMatX:
        cmds.disconnectAttr(decMatX + ".outputRotateX", Joint + ".rotateX")
        cmds.disconnectAttr(decMatX + ".outputRotateY", Joint + ".rotateY")
        cmds.disconnectAttr(decMatX + ".outputRotateZ", Joint + ".rotateZ")
        cmds.connectAttr(decMatX + ".outputRotate", multNode + ".input1", f=True)
    cmds.connectAttr(multNode + ".output", Joint + ".rotate", f=True)


if __name__ == "__main__":
    selectedJoints = cmds.ls(selection=True, type="joint")
    for joint in selectedJoints:
        blendRotation(joint)