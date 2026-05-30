import maya.cmds as cmds

def blendMatrix(master:list, slave:str, weight:float, transform=True):
    blendMatX = cmds.createNode("blendMatrix", n='BlendMatX_'+slave)
    for Master in master:
        # Creation des differents Nodes Matrix

        MultMatX  = cmds.shadingNode('multMatrix',asUtility=True, n='MultMatX_'+slave+Master)
        #ComPivMatX = cmds.shadingNode('composeMatrix', asUtility=True, n='ComPivMatX_'+Master)
        MultPivMatX  = cmds.shadingNode('multMatrix',asUtility=True, n='MultPivMatX_'+slave+Master)
        #DecParInvMatX = cmds.createNode("decomposeMatrix", n="Cache_ParnetInvMatX_"+slave+Master)
        #DecWorldMatXOffset = cmds.createNode("decomposeMatrix", n="Cache_WorldMatXOffset_"+Master)

        #offset = Master+"_Offset"

        #cmds.connectAttr(Master+'.rotatePivot',ComPivMatX+'.inputTranslate')
        #cmds.connectAttr(ComPivMatX+'.outputMatrix',MultPivMatX+'.matrixIn[0]')
        #cmds.connectAttr(offset+".worldMatrix[0]", DecWorldMatXOffset+".inputMatrix")
        #cmds.disconnectAttr(offset+".worldMatrix[0]", DecWorldMatXOffset+".inputMatrix")
        cmds.connectAttr(Master+'.worldMatrix[0]',MultPivMatX+'.matrixIn[0]')
        #cmds.connectAttr(offset+'.worldInverseMatrix[0]',MultPivMatX+'.matrixIn[1]')
        #cmds.connectAttr(DecWorldMatXOffset+'.inputMatrix',MultPivMatX+'.matrixIn[2]')
        cmds.connectAttr(MultPivMatX+'.matrixSum',MultMatX+'.matrixIn[1]')
        #cmds.connectAttr(slave+'.parentInverseMatrix[0]',DecParInvMatX+'.inputMatrix')
        #cmds.disconnectAttr(slave+'.parentInverseMatrix[0]',DecParInvMatX+'.inputMatrix')
        #cmds.connectAttr(DecParInvMatX+'.inputMatrix',MultMatX+'.matrixIn[2]')
        cmds.connectAttr(slave+'.parentInverseMatrix[0]',MultMatX+'.matrixIn[2]')


        MultMatX_Offset = cmds.shadingNode('multMatrix',asUtility=True, n='MultMatX_Offset_'+slave+Master)
        DecMatX_Offset = cmds.shadingNode('decomposeMatrix', asUtility=True, n='DecMatX_Offset_'+slave+Master)
        InversePivMatX = cmds.shadingNode('inverseMatrix', asUtility=True, n='InversePiv_MatX_Offset_'+Master)

        # Creation et recuperation de l'Offset

        cmds.connectAttr(MultPivMatX+'.matrixSum',InversePivMatX+'.inputMatrix')
        cmds.connectAttr(slave+'.worldMatrix[0]',MultMatX_Offset+'.matrixIn[0]')
        cmds.connectAttr(InversePivMatX+'.outputMatrix',MultMatX_Offset+'.matrixIn[1]')
        cmds.connectAttr(MultMatX_Offset+'.matrixSum',DecMatX_Offset+'.inputMatrix')
        cmds.disconnectAttr (MultMatX_Offset+'.matrixSum',DecMatX_Offset+'.inputMatrix')
        cmds.delete(MultMatX_Offset)

        # Connexion de l'Offset, du slave et du Master dans le Multiply Matrix puis dans le Decompose Matrix

        cmds.connectAttr(DecMatX_Offset+'.inputMatrix',MultMatX+'.matrixIn[0]')

        # Connexion du Decompose Matrix dans le BlendMatrix
        if Master == master[0]:
            cmds.connectAttr(MultMatX+'.matrixSum', blendMatX+".inputMatrix")
        else:
            cmds.connectAttr(MultMatX+'.matrixSum', blendMatX+".target[0].targetMatrix")
        
    cmds.setAttr(blendMatX+'.envelope', weight)

    if transform:
        DecMatX = cmds.shadingNode('decomposeMatrix', asUtility=True, n='DecMatX_'+slave)
        cmds.connectAttr(blendMatX+'.outputMatrix', DecMatX+'.inputMatrix')

        cmds.connectAttr(DecMatX+'.outputTranslate', slave+'.translate')
        cmds.connectAttr(DecMatX+'.outputRotate', slave+'.rotate')
        cmds.connectAttr(DecMatX+'.outputScale', slave+'.scale')
    else :
        cmds.connectAttr(blendMatX+".outputMatrix", slave+".offsetParentMatrix", f=True)

if __name__ == "__main__":
    s = cmds.ls(selection=True)
    Master = [s[0], s[1]]
    Slave = s[2]
    Weight = .3
    blendMatrix(Master, Slave, Weight)