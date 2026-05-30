import maya.cmds as cmds


def attachLocToNurbs(loc, nurbs):
    #create nodes
    closestPoint = cmds.createNode('closestPointOnSurface', n=loc + '_closestPoint')
    pointInfo = cmds.createNode('pointOnSurfaceInfo', n=loc + '_pointInfo')
    fourByFour = cmds.createNode('fourByFourMatrix', n=loc + '_fourByFour')
    decMatX = cmds.createNode('decomposeMatrix', n=loc + '_decMatX')
    decMatXEnd = cmds.createNode('decomposeMatrix', n=loc + '_decMatXEnd')

    #connect nodes
    cmds.connectAttr(nurbs + '.worldSpace[0]', closestPoint + '.inputSurface')

    cmds.connectAttr(loc + ".worldMatrix[0]", decMatX + '.inputMatrix')
    cmds.connectAttr(decMatX + '.outputTranslate', closestPoint + '.inPosition')

    cmds.connectAttr(nurbs + '.worldSpace[0]', pointInfo + '.inputSurface')
    cmds.connectAttr(closestPoint + '.parameterU', pointInfo + '.parameterU')
    cmds.connectAttr(closestPoint + '.parameterV', pointInfo + '.parameterV')

    #connect all the point info attribute into the four by four matrix, in a loop having the attribute and axis
    attribs = ['normalizedNormal', 'normalizedTangentU', 'normalizedTangentV', 'position']
    axis = ['X', 'Y', 'Z']

    #the destination attrib are compose like 00 01  02  03  10  11 12 13 20 21 22 23 30 31 32 33
    for i, attrib in enumerate(attribs):
        for j, ax in enumerate(axis):
            cmds.connectAttr(pointInfo + '.' + attrib + ax, fourByFour + '.in' + str(i) + str(j))

    #create a new loc and connect the four by four matrix to the offset parent matrix of the new loc
    Newloc = cmds.spaceLocator(n=loc + '_attachLoc')[0]

    cmds.connectAttr(fourByFour + '.output', decMatXEnd + '.inputMatrix')
    cmds.connectAttr(decMatXEnd + '.outputTranslate', Newloc + '.translate')
    cmds.connectAttr(decMatXEnd + '.outputRotate', Newloc + '.rotate')

    #○color the new loc in pink
    cmds.setAttr(Newloc + "Shape.overrideEnabled", 1)
    cmds.setAttr(Newloc + "Shape.overrideColor", 9)

if __name__ == '__main__':
    selection = cmds.ls(selection=True)
    
    for loc in selection:
        attachLocToNurbs(loc, "Nurbs_Eye_RShape")