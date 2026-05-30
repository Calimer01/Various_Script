import maya.cmds as cmds


def connectBindPreMatrix(Offset, Joint, skinCluster):
    #get in which matrix matrix connection in the skinCluster the joint gets in
    matrixInput = cmds.listConnections(f"{Joint}.worldMatrix[0]", p=True, d=True)
    for m in matrixInput:
        if skinCluster in m:
            matrixInput = m
            break
        else:
            continue
    if type(matrixInput) == list:
        print(f"{Joint} is not connected to {skinCluster}")
        return
    #get the index of the matrix Input
    index = matrixInput.split("[")[-1].split("]")[0]
    skinCluster = matrixInput.split(".")[0]

    cmds.connectAttr(Offset + ".worldInverseMatrix[0]", f"{skinCluster}.bindPreMatrix[{index}]", force=True)

if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    """
    for s in selection:
        joint = s
        Offset = s.replace("Bind", "Loc") + "_Offset"
        connectBindPreMatrix(Offset, joint, "skinCluster369")
    """

    for s in selection:
        Offset = s
        joint = s.replace("Loc", "Bind").split("_Offset")[0]
        connectBindPreMatrix(Offset, joint, "skinCluster370")