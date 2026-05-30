import maya.cmds as cmds
import maya.api.OpenMaya as om

"""
Create some kind of secondary movement joint with it's ctrl
"""

def followJoint(name, xform, skincluster, mesh, dropoff=0.0):
    cmds.select(clear=True)
    #create the joint and match its transform to the given xform
    joint = cmds.joint(name="Bind_" + name)
    cmds.setAttr(joint + ".visibility", 0)
    jointOffset = cmds.group(n=joint + "_Offset", empty=True)
    jointMove = cmds.group(n=joint + "_Move", empty=True)

    #create a ctrl for the joint
    ctrl = cmds.circle(name="CTRL_" + name, normal=(1, 0, 0), center=(.2, 0, 0), radius=1)[0]
    cmds.setAttr(ctrl + "Shape.overrideEnabled", 1)
    cmds.setAttr(ctrl + "Shape.overrideColor", 25)
    cmds.parent(ctrl, jointMove)
    cmds.connectAttr(ctrl + ".translate", joint + ".translate")
    cmds.connectAttr(ctrl + ".rotate", joint + ".rotate")
    cmds.connectAttr(ctrl + ".s", joint + ".s")

    #○color the Move in pink
    cmds.setAttr(jointMove + ".overrideEnabled", 1)
    cmds.setAttr(jointMove + ".overrideColor", 9)

    cmds.parent(joint, jointMove)
    cmds.parent(jointMove, jointOffset)

    #get what comes just before the skin cluster
    beforeSkin = cmds.listConnections(skincluster + ".input[0].inputGeometry", s=True, d=False)[0]

    #create the UvPin Manually
    uvPinNode = cmds.createNode("uvPin", name="UvPin_" + name)
    cmds.connectAttr(mesh + "ShapeOrig.outMesh", uvPinNode + ".originalGeometry")
    cmds.connectAttr(beforeSkin + ".outputGeometry[0]", uvPinNode + ".deformedGeometry")
    #get the closest uv of the joint to the mesh
    jointPos = cmds.xform(xform, q=True, ws=True, t=True)
    closestUV = get_closest_uv(mesh, jointPos)
    cmds.setAttr(uvPinNode + ".coordinate[0].coordinateU", closestUV[0])
    cmds.setAttr(uvPinNode + ".coordinate[0].coordinateV", closestUV[1])

    InverseMatrix = cmds.createNode("inverseMatrix", name="InverseMatrix_" + name)
    cmds.connectAttr(uvPinNode + ".outputMatrix[0]", InverseMatrix + ".inputMatrix")

    cmds.connectAttr(uvPinNode + ".outputMatrix[0]", jointOffset + ".offsetParentMatrix", f=True)


    #add the influence of the joint to the skincluster
    cmds.skinCluster(skincluster, e=True, ai=joint, wt=0)
    cmds.skinCluster(skincluster, e=True, inf=joint, wt=.3, dropoffRate=dropoff)
    connectBindPreMatrix(InverseMatrix, joint, skincluster)

    #constrain the move to ctrl head

    #rangement
    if not cmds.objExists("FollowJoint_GRP"):
        cmds.group(empty=True, name="FollowJoint_GRP")
        cmds.parent("FollowJoint_GRP", "GlobalMove_01")
        cmds.parentConstraint("CTRL_Head_01", "FollowJoint_GRP", mo=True)
    cmds.parent(jointOffset, "FollowJoint_GRP")


def get_closest_uv(mesh_name, world_point):
    # Selection list
    sel = om.MSelectionList()
    sel.add(mesh_name)
    dag = sel.getDagPath(0)

    mesh_fn = om.MFnMesh(dag)

    # Convert point
    point = om.MPoint(world_point)

    # Get UV
    uv = mesh_fn.getUVAtPoint(point, space=om.MSpace.kWorld)

    return uv  # (u, v)

def connectBindPreMatrix(InverseMatrix, Joint, skinCluster):
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

    cmds.connectAttr(InverseMatrix + ".outputMatrix", f"{skinCluster}.bindPreMatrix[{index}]", force=True)

if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    followJoint("Test", selection[0], "Skin_SlyBase", "SlyBody_GEO", dropoff=10)