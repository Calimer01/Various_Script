import maya.cmds as cmds
from wombatAutoRig.src.core import Offset
from wombatAutoRig.src.core import MatrixConstrain


def createCtrl(target):
    #create a circle that match all the transform of the target then offset it and connstrain the target to it
    circle = cmds.circle(name=target.replace("Ribbon_", ""), normal=(0,1,0), radius=1)[0]
    cmds.matchTransform(circle, target)
    Offset.offset(circle, nbr=3)
    MatrixConstrain.MatrixConstrain([circle], target)


if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    for item in selection:
        createCtrl(item)