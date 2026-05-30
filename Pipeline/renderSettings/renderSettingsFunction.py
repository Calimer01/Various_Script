import maya.app.renderSetup.model.override as override
import maya.app.renderSetup.model.selector as selector
import maya.app.renderSetup.model.collection as collection
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.views.renderSetupPreferences as prefs
import maya.cmds as cmds
import maya.mel as mel
import os
import rfm2.ui.globals
import rfm2.ui.widgets as wgt

#region Render Settings

def setup_render_settings():
    prefs.loadUserPreset("topHitRenderSettings")


def set_resolution(data, percent):
    if not data:
        return
    
    base_w = data.get("width")
    base_h = data.get("height")
    w = int(base_w * percent)
    h = int(base_h * percent)

    cmds.setAttr("defaultResolution.width", w)
    cmds.setAttr("defaultResolution.height", h)
    cmds.setAttr("defaultResolution.deviceAspectRatio", w/h)

    print(f"Resolution set to {w}x{h}")

def set_sampling(data, precision):
    reset_render_setup()
    #use this function to set a bunch of defaut render
    cmds.setAttr("rmanGlobals.ri_maxDiffuseDepth", 2)
    cmds.setAttr("rmanGlobals.ocioConfig", -1)
    cmds.setAttr("PxrPathTracer.maxIndirectBounces", 3)
    cmds.setAttr("rmanGlobals.motionBlur", 2)


    minSamples = None
    maxSamples = None
    variance = None
    if not data:
        return
    if precision is not None:
        data = data.get(precision.lower(), {})
        minSamples = data.get("minSamples")
        maxSamples = data.get("maxSamples")
        variance = data.get("variance")

    if minSamples is not None:
        cmds.setAttr("rmanGlobals.hider_minSamples", minSamples)
        print(f"MinSample set to : {minSamples}")

    if maxSamples is not None:
        cmds.setAttr("rmanGlobals.hider_maxSamples", maxSamples)
        print(f"MaxSample set to : {maxSamples}")
    if variance is not None:
        cmds.setAttr("rmanGlobals.ri_pixelVariance", variance)
        print(f"variance set to : {variance}")

def setup_aovs(aovs, lpe, lpeBool, pxrTee):
    reset_aovs()
    add_pxrtee_aovs(pxrTee, aovs)
    if lpeBool:
        add_lpe_avos(aovs, lpe)
    for aov in aovs:
        display = get_or_create_display(aov["display"])

        name = aov["name"]
        source = aov["source"]

        if cmds.objExists(name):
            node = name
        else:
            node = cmds.createNode("rmanDisplayChannel", name=name)
            cmds.setAttr(f"{node}.channelType", "color", type="string")
            cmds.setAttr(f"{node}.channelSource", source, type="string")
            if aov.get("lpe"):
                cmds.setAttr(f"{node}.lpeLightGroup", aov["lpe"], type="string")
            if aov.get("type"):
                cmds.setAttr(f"{node}.channelType", aov["type"], type="string")

        link_channel_to_display(node, display)
    
def add_pxrtee_aovs(display, datAov):
    #find every pxrtee node in the scene, get their name and create custom aovs for them and add them
    PxrTee = cmds.ls(type="PxrTee")
    newAovs = datAov
    #create lpe dict
    pxrteeList = []
    for t in PxrTee:
        source = cmds.getAttr(t+".aov")
        pxrTeeict = {"name": source,
                    "source": source,
                    "display": display,
                }
        pxrteeList.append(pxrTeeict)
            
    newAovs += pxrteeList

    return newAovs

def setup_cryptomatte(data):
    reset_crypto()
    if not data:
        return

    for item in data:
        cmds.evalDeferred("mel.eval('rman_update_globals()')", lp=True)
        mel.eval("refreshAE;")

        rfm2.ui.globals.update()
        mel.eval("currentRenderLayerLabel();")

        wgt.update_page_visibility('PxrPathTracer')

        add_cryptomatte(item)
    
def add_cryptomatte(data):
    if not data:
        return

    # Find the first free slot in sampleFilters
    next_index = 0

    while True:
        # Check if this slot is occupied
        existing = cmds.listConnections(f"rmanGlobals.sampleFilters[{next_index}]", plugs=True)
        if not existing:
            break  # free slot found
        next_index += 1

    # Ensure the array element exists
    if not cmds.objExists(f"rmanGlobals.sampleFilters[{next_index}]"):
        cmds.setAttr(f"rmanGlobals.sampleFilters[{next_index}]", lock=False)
        
    crypto = cmds.createNode('PxrCryptomatte', n=data['name'])
    mel.eval(f"connectAttrToAttrOverride({data['name']}.message, rmanGlobals.sampleFilters[{next_index}]);")
    cmds.setAttr(f"{crypto}.filename", data["fileName"], type="string")
    cmds.setAttr(f"{crypto}.layer", data["layer"], type="string")


    # Connect the cryptomatte
    cmds.connectAttr(f"{crypto}.message", f"rmanGlobals.sampleFilters[{next_index}]", force=True)

def get_or_create_display(name):
    display=name
    
    if display == "rmanDefaultDisplay":
        cmds.setAttr(f"{display}.denoise", 1)
        cmds.setAttr(f"{display}.frameMode", 1)
        cmds.setAttr(f"{display}.opticalFlow", 1)

    if not cmds.objExists(display) :
        cmds.createNode("rmanDisplay", name=display)
        print(f"Created display: {display}")

    #create the driver manually
    driver=None
    if not display=="rmanDefaultDisplay":
        driver = cmds.createNode("d_openexr", name=f"dOpenexr_{name}")
        cmds.connectAttr(driver+".message", display+".displayType", f=True)
    if driver:
        if name == "integrator":
            cmds.setAttr(f"{driver}.asrgba", 0)

    #link it to rmanGlobals
    indices = cmds.getAttr("rmanGlobals.displays", multiIndices=True)
    next_index = indices[-1] + 1 if indices else 0
    #check if it's not already connected
    connections = cmds.listConnections("rmanGlobals.displays", s=True)
    for c in connections:
        if display == c:
            return display
    cmds.connectAttr(f"{display}.message", f"rmanGlobals.displays[{next_index}]")

    return display

def link_channel_to_display(channel_node, display):
    # Check existing connections
    connections = cmds.listConnections(f"{channel_node}.message", d=True, type="rmanDisplay")

    if connections and display in connections:
        return  # already linked

    indices = cmds.getAttr(f"{display}.displayChannels", multiIndices=True)
    next_index = indices[-1] + 1 if indices else 0

    try:
        cmds.connectAttr(
            f"{channel_node}.message",
            f"{display}.displayChannels[{next_index}]",
            force=True
        )
        print(f"Linked {channel_node} → {display}")
    except Exception as e:
        cmds.warning(f"Failed to link {channel_node}: {e}")

#region Render Layers

def setup_Layer(data, chars):
    reset_layer_setup()
    rs = renderSetup.instance()  
    layers = data

    for layer in layers:
        #check if the layer should be created based on the char list
        good=1
        for char in chars:
            if char in layer["name"]:
                good=0
                break

        if not good:
            continue

        # Create and append the render layer
        r = rs.createRenderLayer(layer["name"])

        for col in layer["collections"]:
            #check if the collection should be created based on the char list (is in the original name of the collection and check)
            good=1
            for char in chars:
                if char in col["name"]:
                    good=0
                    break

            if not good:
                continue

            #create the collection under it's parent if it has one
            if col.get("parent"):
                parent_collection = find_collection_by_name(r, col["parent"])
                c = parent_collection.createCollection(col["name"])
            else:
                # Create and append collection
                c = r.createCollection(col["name"])

            # define pattern
            c.getSelector().setPattern(col["pattern"])

            #define Include if specify
            if col.get("type"):
                sel = c.getSelector()
                # Set node type filter
                sel.setFilterType(selector.Filters.kCustom)               

                # Set the actual type
                sel.setCustomFilterValue(col["type"])
            

            for override in col["overrides"]:
                try:
                    if override["type"] == "":
                        continue
                    
                    if override["type"] != "absoluteOverride":
                        ovr = c.createOverride(override["name"], override["type"])
                        ovr.setMaterial(override["value"])
                        continue
                    
                    ovr = c.createAbsoluteOverride(
                        override["name"],
                        override["attribute"]
                    )

                    ovr.setAttrValue(override["value"])

                except Exception as e:
                    print("couldn't create the override :", e)

def find_collection_by_name(layer, name):
    # Check top-level collections
    for col in layer.getCollections():
        if col.name() == name:
            return col

#region reset

def reset_layer_setup():
    rs = renderSetup.instance()

    rs.switchToLayer(rs.getDefaultRenderLayer())

    for layer in rs.getRenderLayers():

        # delete collections + overrides
        collections = layer.getCollections()
        if collections:
            for coll in collections:
                
                # delete overrides first
                overrides = coll.getOverrides()
                if overrides:
                    for ov in overrides:
                        override.delete(ov)

                # delete collection
                collection.delete(coll)

        # delete layer
        renderLayer.delete(layer)
    print("Layer fully reset")

def reset_render_setup():
    prefs.setDefaultPreset()

def reset_aovs():
    # Get connected displays
    displays = cmds.listConnections("rmanGlobals.displays", type="rmanDisplay") or []

    for display in displays:
        hardClean = True
        #default exception:
        if display == "rmanDefaultDisplay":
            cmds.setAttr("rmanDefaultDisplay.denoise", 0)
            cmds.setAttr("rmanDefaultDisplay.frameMode", 0)
            hardClean = False
        # Get channels
        channels = cmds.listConnections(f"{display}.displayChannels", type="rmanDisplayChannel") or []
        
        # Get driver
        driver = cmds.listConnections(f"{display}.displayType") or []

        # Delete everything cleanly
        for ch in channels:
            if cmds.objExists(ch):
                cmds.delete(ch)
            

        for d in driver:
            if hardClean:
                if cmds.objExists(d):
                    cmds.delete(d)
            else:
                pass

        if cmds.objExists(display) and hardClean:
            cmds.delete(display)

    print("RenderMan displays fully reset")

def reset_crypto():
    # Get connected sample filters
    cryptos = cmds.listConnections("rmanGlobals.sampleFilters", type="PxrCryptomatte") or []


    for crypto in cryptos:
        try:
            cmds.delete(crypto)
        except:
            print("couldn't delete the crypto : ", crypto)

    print("RenderMan crypto fully reset")

def reset_all():
    reset_layer_setup()
    reset_render_setup()
    reset_aovs()
    reset_crypto()

#region Ligths

def create_lpe(data):
    #get all the lights in the scene
    light_types = [
        'PxrRectLight', 'PxrDiskLight', 'PxrCylinderLight', 
        'PxrSphereLight', 'PxrDistantLight', 'PxrDomeLight', 
        'PxrEnvDayLight', 'PxrPortalLight', 'PxrMeshLight'
    ]
    lights = cmds.ls(type=light_types)

    lpeGroups = data["groups"]

    for l in lights:
        for g in lpeGroups:
            if g in l:
                cmds.setAttr(l+".lightGroup", "LPE_"+g, type="string")
    print("ligth group has been set ! :)")

def add_lpe_avos(datAov, dataLpe):
    newAovs = datAov
    print("data lpe found:", dataLpe)
    #create lpe dict
    lpeList = []
    for group in dataLpe["groups"]:
        for aov in dataLpe["aovs"]:
            #to get the rigth display find the aov in the aov data and get the associate display
            display = get_display_lpe(datAov, aov)
            source = get_source_lpe(datAov, aov)

            lpedict = {"name": aov+"_LPE_"+group,
                        "source": source.replace("O", ""),
                        "display": display,
                        "lpe": "LPE_"+group
                    }
            lpeList.append(lpedict)
            
    newAovs += lpeList

    return newAovs

def get_display_lpe(aovs, name):
    return next((d["display"] for d in aovs if d["name"] == name), None)

def get_source_lpe(aovs, name):
    return next((d["source"] for d in aovs if d["name"] == name), None)

#region Path

def getCurrentFileName():
    return cmds.file(q=True, sceneName=True).split("/")[-1]

def getPathFromFileName(fileName):
    sqsh = fileName[:11]
    sh = sqsh.split("-")[-1]
    sq = sqsh.split("-")[0]

    networkPath = f"<ws>/imagesShots/{sqsh}"
    LocalPath = f"D:/imageShotLocal/{sqsh}"


    networkLightingPath = f"<ws>/02_Shots/{sq}/{sh}/Renders/3dRender/Lighting"
    project = cmds.workspace(q=True, rootDirectory=True)
    computeLightingPath = networkLightingPath.replace("<ws>", project)

    # if the directory exists list all the subfolder in it and set the new version to the last one +1, if not create the directory and set the version to v001
    if not os.path.exists(computeLightingPath):
        version = "v0001"
    else:
        # List all subfolders and find the last version
        subfolders = os.listdir(computeLightingPath)
        print("subfolders found:", subfolders)
        if subfolders:
            version = f"v{len(subfolders)+1:04d}"
        else:
            version = "v0001"
    networkLightingPath = f"<ws>/02_Shots/{sq}/{sh}/Renders/3dRender/Lighting/{version}"
    #if the scene isn't a correct scene (check if the sq and sh are correct) return empty path
    if not sh.startswith("sh") or not sq.startswith("sq"):
        networkLightingPath = LocalPath


    return [sqsh, networkPath, LocalPath, networkLightingPath]

def setOutputPath(path):
    #create the idrectory if it doesnt' exist
    project = cmds.workspace(q=True, rootDirectory=True)
    computepath = path.replace("<ws>", project)
    if not os.path.exists(computepath):
        os.makedirs(computepath)

    cmds.setAttr(
    "rmanGlobals.imageOutputDir",
    path,
    type="string"
    )
    cmds.setAttr(
    "rmanGlobals.imageFileFormat",
    "<layer>_<aov>.<f4>.<ext>",
    type="string"
    )

def computePath(pathType):
    path = getPathFromFileName(getCurrentFileName())
    if pathType == "Network":
        outpath = path[1]
    elif pathType == "Local":
        outpath = path[2]
    elif pathType == "Lighting":
        outpath = path[3]

    return outpath