import maya.cmds as cmds

def copySkin(mesh1, mesh2):
    #the idea is to get all the joint of the skincluster of the first mesh, use it to skin the second and then copyskin

    skinCluster1 = cmds.ls(cmds.listHistory(mesh1), type='skinCluster')[0]
    joints = cmds.skinCluster(skinCluster1, query=True, influence=True)

    #unbind the second mesh if it is already skinned
    skinClusters2 = cmds.ls(cmds.listHistory(mesh2), type='skinCluster')
    if skinClusters2:
        cmds.skinCluster(skinClusters2[0], edit=True, unbind=True)

    # Create a new skin cluster on the second mesh
    skinCluster2 = cmds.skinCluster(joints, mesh2, toSelectedBones=True)[0]

    # Copy the skin weights from the first mesh to the second
    cmds.copySkinWeights(ss=skinCluster1, ds=skinCluster2, noMirror=True)

if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        cmds.error("Please select exactly two meshes.")
    else:
        mesh1 = selection[0]
        mesh2 = selection[1]
    copySkin(mesh1, mesh2)