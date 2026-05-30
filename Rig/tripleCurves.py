import maya.cmds as cmds

def fourByFour(pointInfo, offset, method):
    MatX = cmds.createNode('fourByFourMatrix', n=offset + '_fourByFour')
    decMatX = cmds.createNode('decomposeMatrix', n=offset + '_decMatX')
    #connect all the point info attribute into the four by four matrix, in a loop having the attribute and axis
    attribs = ['normalizedNormal', 'normalizedTangent', 'curvatureCenter', 'position']
    axis = ['X', 'Y', 'Z']

    #the destination attrib are compose like 00 01  02  03  10  11 12 13 20 21 22 23 30 31 32 33
    for i, attrib in enumerate(attribs):
        for j, ax in enumerate(axis):
            cmds.connectAttr(pointInfo + '.' + attrib + ax, MatX + '.in' + str(i) + str(j))


    cmds.connectAttr(MatX + '.output', decMatX + '.inputMatrix')
    cmds.connectAttr(decMatX + '.outputTranslate', offset + '.translate')
    if method == 1:
        cmds.connectAttr(decMatX + '.outputRotate', offset + '.rotate')
    elif method == 2:
        cmds.connectAttr(decMatX + '.outputRotateZ', offset + '.rotateZ')
    return MatX, decMatX

def tripleCurves(crv1, DrvJnt1, DrvJnt2, BindJnt, name, method=0):
    #@method : choose the type of follow of the drvJnt : 0 ==> pos only 1==> pos and orient 2 ==> pos and orient only Z
    #get the first curve as the base high curve and duplicate it twice to have the mid and low ones
    crvLow = cmds.duplicate(crv1, name="Crv" + name + "_low")
    crvMid = cmds.duplicate(crv1, name="Crv" + name + "_mid")
    crvHigh = cmds.rename(crv1, "Crv" + name + "_high")

    #rebuild the curves
    cmds.rebuildCurve(crvLow, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=cmds.getAttr(crvLow[0] + ".spans") / 4, d=3)
    cmds.rebuildCurve(crvMid, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=cmds.getAttr(crvMid[0] + ".spans") / 2, d=3)

    #delete the history of the curves
    cmds.delete(crvLow, ch=True)
    cmds.delete(crvMid, ch=True)
    cmds.delete(crvHigh, ch=True)

    #region DrvJnt1
    #based on the number of wanted drvjnt create the drvjnt and put an offset on them to then connect a pointoncurveinfo to the offset with a different parameter
    DrvJntlist1 = []
    DrvJnt1Grp = cmds.group(empty=True, name="DrvJntMain_" + name + "_GRP")
    for i in range(DrvJnt1):
        jnt = cmds.joint(name="DrvJntMain_" + name + "_" + str(i).zfill(2))
        #give it a yellow color
        cmds.setAttr(jnt+".overrideEnabled", 1)
        cmds.setAttr(jnt+".overrideColor", 25)
        DrvJntlist1.append(jnt)
        offset = cmds.group(jnt, name=jnt + "_Offset")
        cmds.parent(offset, DrvJnt1Grp)
        pointOnCurveInfo = cmds.createNode("pointOnCurveInfo", name="POnCrvInfo_"+offset)
        cmds.connectAttr(crvLow[0] + ".worldSpace[0]", pointOnCurveInfo + ".inputCurve")
        cmds.setAttr(pointOnCurveInfo + ".turnOnPercentage", 1)
        cmds.setAttr(pointOnCurveInfo + ".parameter", i / (DrvJnt1 - 1))
        cmds.connectAttr(pointOnCurveInfo + ".position", offset + ".translate")
        
    #region DrvJnt2
    DrvJntlist2 = []
    DrvJnt2Grp = cmds.group(empty=True, name="DrvJnt_" + name + "_GRP")
    for i in range(DrvJnt2):
        jnt = cmds.joint(name="DrvJnt_" + name + "_" + str(i).zfill(2))
        cmds.setAttr(jnt + ".radius", .7)
        cmds.setAttr(jnt+".overrideEnabled", 1)
        cmds.setAttr(jnt+".overrideColor", 25)
        DrvJntlist2.append(jnt)
        offset = cmds.group(jnt, name=jnt + "_Offset")
        cmds.parent(offset, DrvJnt2Grp)
        pointOnCurveInfo = cmds.createNode("pointOnCurveInfo", name="POnCrvInfo_"+offset)
        cmds.connectAttr(crvMid[0] + ".worldSpace[0]", pointOnCurveInfo + ".inputCurve")
        cmds.setAttr(pointOnCurveInfo + ".turnOnPercentage", 1)
        cmds.setAttr(pointOnCurveInfo + ".parameter", (i) / (DrvJnt2 - 1))
        if method:
            fourByFour(pointOnCurveInfo, offset, method)
        else:
            cmds.connectAttr(pointOnCurveInfo + ".position", offset + ".translate")    
    #region BindJnt
    BindJntlist = []
    BindJntGrp = cmds.group(empty=True, name="BindJnt_" + name + "_GRP")
    for i in range(BindJnt):
        jnt = cmds.joint(name="BindJnt_" + name + "_" + str(i).zfill(2))
        cmds.setAttr(jnt + ".radius", .3)
        cmds.setAttr(jnt+".overrideEnabled", 1)
        cmds.setAttr(jnt+".overrideColor", 16)
        BindJntlist.append(jnt)
        offset = cmds.group(jnt, name=jnt + "_Offset")
        cmds.parent(offset, BindJntGrp)
        pointOnCurveInfo = cmds.createNode("pointOnCurveInfo", name="POnCrvInfo_"+offset)
        cmds.connectAttr(crvHigh + ".worldSpace[0]", pointOnCurveInfo + ".inputCurve")
        cmds.setAttr(pointOnCurveInfo + ".turnOnPercentage", 1)
        cmds.setAttr(pointOnCurveInfo + ".parameter", i / (BindJnt - 1))
        if method:
            fourByFour(pointOnCurveInfo, offset, method)
        else:
            cmds.connectAttr(pointOnCurveInfo + ".position", offset + ".translate")    
    #region crv skinning
    #the drvjnt1 skin the mid curve, the drvjnt2 skin the high curve
    cmds.skinCluster(DrvJntlist1, crvMid[0], toSelectedBones=True)
    cmds.skinCluster(DrvJntlist2, crvHigh, toSelectedBones=True)

    #region clean up
    mainGrp = cmds.group(empty=True, name=name + "_system_GRP")
    CrvGrp = cmds.group(crvLow, crvMid, crvHigh, name="Crv_" + name + "_GRP")
    cmds.parent(CrvGrp, mainGrp)
    cmds.parent(DrvJnt1Grp, mainGrp)
    cmds.parent(DrvJnt2Grp, mainGrp)
    cmds.parent(BindJntGrp, mainGrp)

if __name__ == '__main__':
    selection = cmds.ls(selection=True)
    if len(selection) != 1:
        cmds.error("Please select one curve")
    else:
        tripleCurves(selection[0], DrvJnt1=3, DrvJnt2=5, BindJnt=10, name="Test")