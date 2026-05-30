import maya.cmds as cmds
from wombatAutoRig.src.core import Offset
from wombatAutoRig.src.core import MatrixConstrain

"""
Create an CTRL without shape and connect it to the relay loc. This will be used to drive the relay loc
The pin transform will be driven the offset of the ctrl with local transform and a 50 difference in tY
All the mouth CTRLs will be store in a mouthCTRL grp constraint to the head CTRL
"""

def ctrlFromRelay(locOffset):
    ctrl = cmds.group(empty=True, n=locOffset.replace("Loc", "CTRL").split("_Offset")[0])
    cmds.matchTransform(ctrl, locOffset)

    Offset.offset(ctrl, nbr=3)

    cmds.parent(ctrl+"_Offset", "CTRLs_Mouth_GRP")

    #addY = cmds.createNode("addDoubleLinear", n=ctrl.replace("CTRL", "Add")+"Y")
    #cmds.connectAttr(locOffset + ".translateX", addY + ".input1")
    #cmds.setAttr(addY + ".input2", -50)
    #addZ = cmds.createNode("addDoubleLinear", n=ctrl.replace("CTRL", "Add")+"Z")
    #cmds.connectAttr(locOffset + ".translateZ", addZ + ".input1")
    #cmds.setAttr(addZ + ".input2", -4.808)


    #cmds.connectAttr(addY + ".output", ctrl + "_Offset.translateY")
    #cmds.connectAttr(locOffset + ".translateX", ctrl + "_Offset.translateX")
    cmds.connectAttr(locOffset + ".t", ctrl + "_Offset.t")
    #cmds.connectAttr(addZ + ".output", ctrl + "_Offset.translateZ")
    cmds.connectAttr(locOffset + ".r", ctrl + "_Offset.r")
    cmds.connectAttr(locOffset + ".s", ctrl + "_Offset.s")

    loc = cmds.spaceLocator(n=ctrl.replace("CTRL", "LocRelay"))[0]
    cmds.matchTransform(loc, ctrl)
    cmds.parent(loc, ctrl+"_Offset")

    MatrixConstrain.MatrixConstrain([ctrl], loc)

    cmds.connectAttr(loc+".t", locOffset.split("_Offset")[0]+".translate")
    cmds.connectAttr(loc+".r", locOffset.split("_Offset")[0]+".rotate")
    cmds.connectAttr(loc+".s", locOffset.split("_Offset")[0]+".scale")

    #hide the locator
    cmds.setAttr(loc + ".visibility", 0)

def ctrlFromNurbs(DrvJnt, groupName):
    #there is 2 type of drvjnt here, the main (direct control) and the secondary (driven by the nurbs so it need to plug the transfrom of the offset)

    if "Main" in DrvJnt:
        #create an empty group that match the transform of the drvjnt and parent it under "groupName"
        ctrl = cmds.group(empty=True, n=DrvJnt.replace("DrvJnt", "CTRL"))
        #ctrl = cmds.circle(n=DrvJnt.replace("DrvJntMain", "CTRL"))
        cmds.matchTransform(ctrl, DrvJnt)
        cmds.parent(ctrl, groupName)
        #create an offset group for the ctrl
        Offset.offset(ctrl, nbr=3)
        #connect the transform of the ctrl to the drvjnt
        cmds.connectAttr(ctrl + ".t", DrvJnt + ".translate")
        cmds.connectAttr(ctrl + ".r", DrvJnt + ".rotate")
        cmds.connectAttr(ctrl + ".s", DrvJnt + ".scale")
    else:
        jntOffset = DrvJnt + "_Offset"
        #create an empty group that match the transform of the drvjnt and parent it under "groupName"
        ctrl = cmds.group(empty=True, n=DrvJnt.replace("DrvJnt", "CTRL"))
        #ctrl = cmds.circle(n=DrvJnt.replace("DrvJnt", "CTRL"))
        cmds.matchTransform(ctrl, DrvJnt)
        cmds.parent(ctrl, groupName)
        #create an offset group for the ctrl
        Offset.offset(ctrl, nbr=3)
        #plug the transform of the jntOffset to the ctrl offset
        cmds.connectAttr(jntOffset + ".t", ctrl + "_Offset.translate")
        cmds.connectAttr(jntOffset + ".r", ctrl + "_Offset.rotate")
        cmds.connectAttr(jntOffset + ".s", ctrl + "_Offset.scale")
        #connect the transform of the ctrl to the drvjnt
        cmds.connectAttr(ctrl + ".t", DrvJnt + ".translate")
        cmds.connectAttr(ctrl + ".r", DrvJnt + ".rotate")
        cmds.connectAttr(ctrl + ".s", DrvJnt + ".scale")

if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    for s in selection:
        #ctrlFromRelay(s)
        ctrlFromNurbs(s, "CTRLs_Glasses_GRP")