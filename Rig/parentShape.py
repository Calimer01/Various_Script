import maya.cmds as cmds

def parentShapeToCtrl(ctrl, group):
    shapes = cmds.listRelatives(ctrl, s=True, f=True)
    cmds.makeIdentity(ctrl)
    if shapes:
        for shape in shapes:
            cmds.parent(shape, group, r=True, s=True)
        cmds.delete(ctrl)

if __name__ == "__main__":
    selection = cmds.ls(sl=True)
    if len(selection) != 2:
        cmds.error("Please select a control and a group")
    else:
        parentShapeToCtrl(selection[0], selection[1])