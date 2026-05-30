# PostPublish.py

name = "PostPublish"
classname = "PostPublish"

from os import path
import json
import os


class PostPublish:
    def __init__(self, core):
        self.core = core
        self.version = "v1.0.0"

        # register prePublish and preExport callbacks
        self.core.registerCallback("postPublish", self.postPublish, plugin=self)

    # this function will be called once before every publish
    def postPublish(self, origin, *args, **kwargs):
        # if this is a set dress publish, find the master of the setDressPublish produtc and run the code on it
        result = kwargs["result"][0]["result"]
        productName = result[0].split("(")[-1].split(")")[0]
        if self.core.fileInPipeline():
            #get the data path
            currentPath = self.core.appPlugin.getCurrentFileName(self.core)
            dataPath = currentPath[:-3] + "versioninfo.json"
            if os.path.exists(dataPath):
                with open(dataPath) as f:
                    self.data = json.load(f)

        if "setDress" in productName:
            self.runSDPostPublishChecks(self.find_all_curves())
        elif "rigPublish" in productName:
            self.runRigPostPublishChecks()
        elif "surfPublish" in productName:
            # if prop ou char set de select
            typeOfAsset = self.data["asset_path"].split("\\")[0]
            if typeOfAsset == "Chars" or typeOfAsset == "Props" or typeOfAsset == "CHAR":
                self.runSurfPostPublishChecks()

    def runSurfPostPublishChecks(self):
        try:
            import maya.cmds as cmds
            import maya.mel as mel
        except:
            return
        currentFileName = cmds.file(q=True, location=True)
        
        cmds.select("*_GEO*", r=True)
        polygons = cmds.ls(selection=True)
        cmds.select(clear=True)
        sets = cmds.ls(et="objectSet")
        correctName = self.data["asset_path"].split("\\")[0] + "_" + self.data["asset"]
        cmds.delete(sets)
        cmds.sets(polygons, n=correctName)

        products = self.core.products.getProductsFromEntity(self.data)

        for product in products:
            if "surfPublish" in product["product"]:
                path = product["path"]
                productName = product["product"]
                surfProduct = product
                break

        try:
            postVersion = self.core.products.getNextAvailableVersion(self.data, productName)
        except:
            postVersion = "v0002"
        version = "v" + str(int(postVersion[1:])-1).zfill(4)
        
        productPath = surfProduct["path"] + os.sep + version + os.sep + surfProduct["asset"] + "_" + surfProduct["product"] + "_" + version + ".ma"
        
        #Extract the product from the group "ASSET_GRP" and delete everything that isn't the product
        productGrp = surfProduct["asset"] + "_GRP"
        if cmds.objExists(productGrp):
            cmds.parent(productGrp, world=True)
            cmds.setAttr(productGrp + ".t", 0, 0, 0)
            cmds.setAttr(productGrp + ".r", 0, 0, 0)
            cmds.setAttr(productGrp + ".s", 1, 1, 1)
        
        try:
            self.importReference()
        except:
            pass

        topGroups = self.getTopParents()
        for group in topGroups:
            if group != productGrp:
                try:
                    cmds.delete(group)
                except Exception as e:
                    print("couldn't delete group " + group + ": " + str(e))
        try:
            cmds.delete("CONTROLS")
        except Exception as e:
            print("couldn't delete CONTROLS: " + str(e))
        
        mel.eval("hyperShadePanelMenuCommand(\"hyperShadePanel1\", \"deleteUnusedNodes\");")

        cmds.file(rename=productPath)
        cmds.select(clear=True)
        cmds.select(self.getTopParents())
        cmds.select(correctName, add=True, ne=True)
        print(f"exporting selection : {cmds.ls(selection=True)} to {productPath}")
        cmds.file(force=True, exportSelected=True)
        #update master version
        self.core.products.updateMasterVersion(productPath)

        #reopen the scenfile file to come back to the with curve version
        self.core.appPlugin.openScene(
            self, currentFileName, force=True
        )
        self.core.sm=None


    def runRigPostPublishChecks(self):
        try:
            import maya.cmds as cmds
        except:
            return
        currentFileName = cmds.file(q=True, location=True)

        cmds.select("*_GEO", r=True)
        if cmds.objExists("topHitCam"):
            cmds.select("topHitCam", add=True)
        polygons = cmds.ls(selection=True)

        sets = cmds.ls(et="objectSet")
        correctName = self.data["asset_path"].split("\\")[0] + "_" + self.data["asset"]
        cmds.delete(sets)
        cmds.sets(polygons, n=correctName)

        products = self.core.products.getProductsFromEntity(self.data)

        for product in products:
            if "rigPublish" in product["product"]:
                path = product["path"]
                productName = product["product"]
                rigProduct = product
                break

        postVersion = self.core.products.getNextAvailableVersion(self.data, productName)
        version = "v" + str(int(postVersion[1:])-1).zfill(4)
        
        productPath = rigProduct["path"] + os.sep + version + os.sep + rigProduct["asset"] + "_" + rigProduct["product"] + "_" + version + ".ma"
        
        cmds.file(rename=productPath)
        cmds.select(clear=True)
        cmds.select(self.getTopParents())
        cmds.select(correctName, add=True, ne=True)
        print(f"exporting selection : {cmds.ls(selection=True)} to {productPath}")
        cmds.file(force=True, exportSelected=True)
        #update master version
        self.core.products.updateMasterVersion(productPath)

        #reopen the scenfile file to come back to the with curve version
        self.core.appPlugin.openScene(
            self, currentFileName, force=True
        )
        self.core.sm=None

    def runSDPostPublishChecks(self, curves):
        try:
            import maya.cmds as cmds
            import maya.mel as mel
        except:
            print("couldn't load maya.cmds")
            return
        currentFileName = cmds.file(q=True, location=True) or ""
        for c in curves:
            # reparent the childs of the curve to the parent of the curve
            parent = cmds.listRelatives(c, parent=True, type='transform')
            if parent:
                children = cmds.listRelatives(c, children=True, type='transform') or []
                for child in children:
                    cmds.parent(child, parent[0])
                    cmds.delete(child, ch=True)
                cmds.delete(c)
                print(f"{c} has been deleted")
        
        #region Cleaning
        #delete all the joints and lambert

        joints = cmds.ls(type="joint")
        for j in joints:
            cmds.delete(j)
        lamberts = cmds.ls(type="lambert")
        for l in lamberts:
            cmds.delete(l)
        pxrTee = cmds.ls(type="pxrTee")
        for p in pxrTee:
            cmds.delete(p)
        #namespace
        # List all namespaces
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)

        # Default namespaces to ignore
        default_namespaces = {'UI', 'shared'}

        for ns in namespaces:
            if ns not in default_namespaces:
                try:
                    cmds.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)
                except RuntimeError:
                    print(f"Could not remove namespace: {ns}")
        
        self.hardcore_clean()

        #save the file as a product after the modifications
        dataPath = currentFileName.split(".")[0] + "versioninfo.json"
        with open(dataPath, "r") as f:
            data = json.load(f)
        products = self.core.products.getProductsFromEntity(data)

        computeProductname = "setDressPublish"
        if "Anim" in cmds.file(q=True, location=True):
            computeProductname = "setDressAnimPublish"

        for product in products:
            if computeProductname in product["product"]:
                path = product["path"]
                productName = product["product"]
                setDressProduct = product
                break

        postVersion = self.core.products.getNextAvailableVersion(data, productName)
        version = "v" + str(int(postVersion[1:])-1).zfill(4)

        productPath = setDressProduct["path"] + os.sep + version + os.sep + setDressProduct["sequence"] + "-" + setDressProduct["shot"] + "_" + setDressProduct["product"] + "_" + version + ".ma"
        print(f"{productPath} is the location of the master")

        cmds.file(rename=productPath)
        cmds.select(self.getTopParents(), replace=True)
        cmds.file(force=True, exportSelected=True)
        #update master version
        self.core.products.updateMasterVersion(productPath)

        #reopen the scenfile file to come back to the with curve version
        self.core.appPlugin.openScene(
            self, currentFileName, force=True
        )

    def find_all_curves(self):
        try:
            import maya.cmds as cmds
        except:
            return
        #find top group first
        topGroups = self.getTopParents()

        for group in topGroups:
            all_transforms = cmds.listRelatives(group, allDescendents=True, type='transform', fullPath=True) or []
            #list all descendant from top group gradnchildren first
            all_curves = []

            for transform in all_transforms:
                shapes = cmds.listRelatives(transform, shapes=True) or []
                for shape in shapes:
                    if "polySurfaceShape" in shape or "Orig" in shape:
                        continue
                    if cmds.nodeType(shape) == 'nurbsCurve':
                        all_curves.append(transform)
                        break  # No need to check other shapes under this transform
        
        return all_curves

    def getTopParents(self):
        try:
            import maya.cmds as cmds
        except:
            return
        '''
        Returns a list of the top most parents for the given transforms
        '''
        top_groups = [node for node in cmds.ls(assemblies=True) 
                      if cmds.objectType(node) == "transform"]

        for t in top_groups:
            if t == 'persp' or t=='top' or t=='front' or t=='side':
                top_groups.remove(t)

        return top_groups
    
    def importReference(self):
        try:
            import maya.cmds as cmds
        except:
            return
        refFiles = cmds.file(query=True, reference=True)

        for i in refFiles:
            cmds.file(i, removeReference=True)

    def hardcore_clean(self):
        try:
            import maya.cmds as cmds
            import maya.mel as mel
        except:
            return

        # 2. Kill constraints
        constraints = cmds.ls(type=[
            "parentConstraint", "pointConstraint", "orientConstraint",
            "scaleConstraint", "aimConstraint"
        ])
        if constraints:
            cmds.delete(constraints)

        # 3. Delete ALL typical rig utility nodes
        rig_nodes = cmds.ls(type=[
            "decomposeMatrix", "composeMatrix", "multMatrix", "wtAddMatrix",
            "pointOnCurveInfo", "pointOnSurfaceInfo", "curveInfo",
            "distanceBetween", "blendColors",
            "plusMinusAverage", "multiplyDivide", "remapValue",
            "animCurve", "unitConversion"
        ])
        if rig_nodes:
            cmds.delete(rig_nodes)

        # 4. Delete animation curves (in case some survived)
        anim = cmds.ls(type="animCurve")
        if anim:
            cmds.delete(anim)

        # 5. Delete unknown nodes
        unknown = cmds.ls(type="unknown")
        if unknown:
            cmds.delete(unknown)

        # 6. Remove unused shading networks
        cmds.hyperShade(removeUnusedShadingNetworks=True)

        # 7. MEL fallback cleanup
        try:
            mel.eval("deleteUnusedNodes;")
        except:
            pass

        print("Scene nuked")
