import maya.cmds as cmds

"""
Start with creating an uv Pin node, then use the function below to place it at the right place with the right connection.
A relay CTRL will be created
"""



def attachControllerToMesh(geo, ctrl, pin, deform=True):
    #region Pin
    #find the uv pin node from the pin locator
    pinNode = cmds.listConnections(pin + ".offsetParentMatrix", s=True, t="uvPin")[0]

    #get the deformer skin cluster of the geo to connect it to the derormed geo of the pin node
    history = cmds.listHistory(geo + "Shape", ac=True, lv=5, pdo=True)
    for h in history:
        if cmds.objectType(h) == "skinCluster":
            if "deforme" in h.lower() and deform:
                skinCluster = h
                break
            else:
                if not "deforme" in h.lower():
                    skinCluster = h
                    break

    #get the original connection of the deformedGeo attribute of the pin and disconnect it
    deformedGeo = cmds.listConnections(pinNode + ".deformedGeometry", s=True)[0]

    if cmds.objectType(deformedGeo+"Shape") == "mesh":
        cmds.disconnectAttr(deformedGeo + ".worldMesh[0]", pinNode + ".deformedGeometry")
    else:
        cmds.disconnectAttr(deformedGeo + ".outMesh", pinNode + ".deformedGeometry")
    
    #connect the skinCluster output geometry to the pin node
    if cmds.objectType(skinCluster) == "skinCluster":
        cmds.connectAttr(skinCluster + ".outputGeometry[0]", pinNode + ".deformedGeometry", f=True)
    



if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    geo = selection[0]
    ctrl = selection[1]
    pin = selection[2]
    attachControllerToMesh(geo, ctrl, pin, deform=False)