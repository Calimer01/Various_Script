import maya.cmds as cmds
from wombatAutoRig.src.core import Offset
"""
This module create a locator after the creation of a ribbon on curve. This will match the transform of the pin
    This will create an Offset Hook Move on the Loc
    This will create the constrain between the UVpin and the Offset Hook Move
    this will create the connection between the loc and the drvJnt
"""

def relayLoc(pin, drvJnt=False):
    joint=pin.replace("Pin", "Bind").replace("_attachLoc", "")
    Loc = cmds.spaceLocator(n=joint.replace("Bind", "Loc"))[0]
    cmds.matchTransform(Loc, joint)
    Offset.offset(Loc, nbr=3)

    MatrixConstraint(pin, Loc + "_Offset")
    if not drvJnt == False:
        MatrixConstraint(Loc, drvJnt)

    cmds.setAttr(Loc + ".visibility", 0)



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
    #test
    pin = cmds.ls(sl=True)[0]
    drvJnt = cmds.ls(sl=True)[1]
    relayLoc(pin, drvJnt)
