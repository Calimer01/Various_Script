import maya.cmds as cmds


def jiggleBend(joint, ribbon):
    #create a cluster for the ribbon that will be driven by the local rotate of the joint
    cmds.cluster(f"{ribbon}.cv[3][0]", f"{ribbon}.cv[3][1]", f"{ribbon}.cv[3][2]", f"{ribbon}.cv[3][3]", f"{ribbon}.cv[4][0]", f"{ribbon}.cv[4][1]", f"{ribbon}.cv[4][2]", f"{ribbon}.cv[4][3]", n="Clt_"+ribbon)

    jointParent = cmds.listRelatives(joint, p=True)[0]
    plusminusNode = cmds.shadingNode("plusMinusAverage", n=f"{joint}_jiggleBend_plusMinus", asUtility=True)

    cmds.connectAttr(f"{joint}.rotate", f"Clt_{ribbon}Handle.rotate", f=True)
    cmds.connectAttr(f"{joint}.translate", plusminusNode+".input3D[0]", f=True)
    cmds.connectAttr(f"{jointParent}.translate", plusminusNode+".input3D[1]", f=True)
    cmds.connectAttr(plusminusNode+".output3D", f"Clt_{ribbon}Handle.rotatePivot", f=True)

    #parent the cluster in the cluster grp (create the groupe if it doesn't exist)
    if not cmds.objExists("cluster_GRP"):
        cmds.group(empty=True, name="cluster_GRP")
        cmds.parent("cluster_GRP", "Extra_Nodes_To_Hide_01")
    cmds.parent(f"Clt_{ribbon}Handle", "cluster_GRP")

if __name__ == "__main__":
    joint = cmds.ls(selection=True)[0]
    ribbon = cmds.ls(selection=True)[1]
    jiggleBend(joint, ribbon)