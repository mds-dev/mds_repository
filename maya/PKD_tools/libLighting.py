__author__ = 'pritish.dogra'
import pymel.core as pm
import PySide.QtGui as QtGui
from maya import mel
from functools import partial
try:
    import libPySide, libGUI, libShader,libUtilities
    for module in libPySide,libGUI, libShader,libUtilities:
        reload(module)
except:
    from libs import libPySide, libGUI, libShader,libUtilities
    for module in libPySide,libGUI, libShader,libUtilities:
        reload(module)
import re


def _build_query_stats_():
    Global_Options_Advanced = [
        "globopt_ray_maxIntens_on",
        "globopt_ray_maxIntens"
    ]

    Image_Sampler = [
        "samplerType",
        "minShadeRate",
        "aaFilterOn",
        "aaFilterType",
        "aaFilterSize",
        "subdivMinRate",
        "subdivMaxRate",
        "subdivJitter",
        "subdivThreshold",
        "subdivEdges",
        "subdivNormals"]

    Dmc_Sampler = [
        "dmcs_adaptiveAmount",
        "dmcs_adaptiveThreshold",
        "dmcs_adaptiveMinSamples",
        "dmcs_subdivsMult"]

    Color_Mapping = [
        "cmap_type",
        "cmap_darkMult",
        "cmap_brightMult",
        "cmap_gamma",
        "cmap_affectBackground",
        "cmap_adaptationOnly",
        "cmap_clampOutput"
    ]

    Color_Mapping_Advanced = [
        "cmap_subpixelMapping",
        "cmap_linearworkflow",
        "cmap_affectSwatches"
    ]

    Camera = ["cam_type",
              "cam_overrideFov",
              "cam_fov",
              "cam_dofOn",
              "cam_dofAperture",
              "cam_dofCenterBias",
              "cam_dofGetFromCamera",
              "cam_dofSides",
              "cam_dofRotation",
              "cam_dofAnisotropy",
              "cam_mbOn",
              "cam_mbCameraMotionBlur",
              "cam_mbDuration",
              "cam_mbIntervalCenter",
              "cam_mbBias",
              "cam_mbShutterEfficiency"
              ]

    GI = [
        "giOn",
        "reflectiveCaustics",
        "refractiveCaustics",
        "primaryEngine",
        "primaryMultiplier",
        "secondaryEngine",
        "secondaryMultiplier"
    ]

    GI_Advanced = [
        "saturation",
        "contrast",
        "contrastBase",
        "aoOn",
        "aoAmount",
        "aoRadius",
        "aoSubdivs",
        "giRayDistOn",
        "giRayDist"
    ]

    Irradiance_Map = [
        "imap_currentPreset",
        "imap_minRate",
        "imap_maxRate",
        "imap_subdivs",
        "imap_interpSamples",
        "imap_interpFrames",
        "imap_colorThreshold",
        "imap_normalThreshold",
        "imap_distanceThreshold",
        "imap_useCameraPath",
        "imap_mode"]

    Irradiance_Map_Advanced = [
        "imap_detailEnhancement",
        "imap_detailScale",
        "imap_detailRadius",
        "imap_detailSubdivsMult",
        "imap_showSamples",
        "imap_showCalcPhase",
        "imap_interpolationMode",
        "imap_lookupMode",
        "imap_checkSampleVisibility",
        "imap_multipass",
        "imap_randomizeSamples",
        "imap_calcInterpSamples"
    ]

    Brute_Force = [
        "dmc_subdivs",
        "dmc_depth"]

    Light_Cache = [
        "subdivs",
        "sampleSize",
        "showCalcPhase",
        "storeDirectLight",
        "worldScale",
        "useForGlossy",
        "useCameraPath",
        "mode",
        "filterType",
        "prefilter",
        "prefilterSamples",
        "depth",
        "filterSamples",
        "filterSize",
        "useRetraceThreshold",
        "retraceThreshold",
        "adaptiveSampling"
    ]

    Caustics = [
        "causticsOn",
        "causticsMultiplier",
        "causticsSearchDistance",
        "causticsMaxPhotons",
        "causticsMaxDensity",
        "causticsMode",
        "causticsDontDelete"]

    LighthInfo = ["subdivs",
                  "cutoffThreshold"]

    MaterialInfo = ["reflectionGlossiness",
                    "reflectionSubdivs",
                    "refractionGlossiness",
                    "refractionSubdivs",
                    "scatterSubdivs",
                    "sssSubdivs",
                    "subdivs"
                    ]

    renderStatsQuery = {"Global_Options_Advanced": Global_Options_Advanced,
                        "Image_Sampler": Image_Sampler,
                        "Dmc_Sampler": Dmc_Sampler,
                        "Color_Mapping": Color_Mapping,
                        "Color_Mapping_Advanced": Color_Mapping_Advanced,
                        "Camera": Camera,
                        "GI":GI,
                        "GI_Advanced": GI_Advanced,
                        "Irradiance_Map": Irradiance_Map,
                        "Irradiance_Map_Advanced": Irradiance_Map_Advanced,
                        "Brute_Force": Brute_Force,
                        "Light_Cache": Light_Cache,
                        "Caustics": Caustics,
                        "Light Info": LighthInfo,
                        "Material Info": MaterialInfo,
                        "Order": ["Global_Options_Advanced",
                                  "Image_Sampler",
                                  "Dmc_Sampler",
                                  "Color_Mapping",
                                  "Color_Mapping_Advanced",
                                  "Camera",
                                  "GI",
                                  "GI_Advanced",
                                  "Irradiance_Map",
                                  "Irradiance_Map_Advanced",
                                  "Brute_Force",
                                  "Light_Cache",
                                  "Caustics",
                                  "Light Info",
                                  "Material Info"
                                  ]
                        }

    return renderStatsQuery


def _vray_settings_aliases_():
    samplerType = {0: "Fixed Rate", 1: "Adaptive", 2: "Adaptive Subdivision", 3: "Progressive"}

    renderMaskMode = {0: "Disabled", 1: "Texture", 2: "Object Set", 3: "ObjectIDs"}

    aaFilterType = {0: "Box", 1: "Area", 2: "Triangle", 3: "Lanczos", 4: "Sinc", 5: "CatmullRom", 6: "Gaussian",
                    7: "Cook Variable"}

    cmap_type = {0: "Linear Multiply", 1: "Exponential", 2: "HSV Exponential", 3: "Intensity Exponential",
                 4: "Gamma Correction", 5: "intensity Gamma", 6: "Reinhard"}

    cmap_adaptationOnly = {0: "Color Mapping And Gamma", 1: "Don't affect Colors,Only Adaptation",
                           2: "Color Mapping Only,No Gamma"}

    cam_type = {0: "Standard", 1: "Spherical", 2: "Cylindrical(point)", 3: "Cylindrical(ortho)", 4: "Box",
                5: "Fish Eye", 6: "Warped Spherical(old_tyle)", 7: "Orthogonal", 8: "Pinhole"}

    primaryEngine = {0: "Irradiance Map", 1: "Photon Map", 2: "Brute Force", 3: "Light Cache", 4: "Spherical Harmonics"}

    secondaryEngine = {0: "none", 1: "Photon Map", 2: "Brute force", 3: "Light Cache"}

    imap_currentPreset = {0: "Custom", 1: "Very Low", 2: "Low", 3: "Medium", 4: "Mudium Animation", 5: "High",
                          6: "High Animation", 7: "Very High"}

    imap_mode = {0: "Single Frame", 1: "Multiframe Incremental", 2: "From File", 3: "Add To Current Map",
                 4: "Incremental Add TO Current Map", 5: "Bucket Mode", 6: "Animation(Prepass)",
                 7: "Animation(Rendering)"}

    imap_detailScale = {0: "Screen", 1: "World"}

    imap_interpolationMode = {0: "Weighted Average (Good/Robust)", 1: "Least Squares Fit(Good/Smooth)",
                              2: "Delone Trangulation(Good/Exact)", 3: "Least Squares W/Voronoi Weights"}

    imap_lookupMode = {0: "Nearest(Draft)", 1: "Quad-balanced(Good)", 2: "Overlapping(Very Good/Fast)",
                       3: "Density Based(Best)"}

    pmap_mode = {0: "New Map", 1: "From Map"}

    aliasDict = {
        "samplerType": samplerType,
        "renderMaskMode": renderMaskMode,
        "aaFilterType": aaFilterType,
        "cmap_type": cmap_type,
        "cmap_adaptationOnly": cmap_adaptationOnly,
        "cam_type": cam_type,
        "primaryEngine": primaryEngine,
        "secondaryEngine": secondaryEngine,
        "imap_currentPreset": imap_currentPreset,
        "imap_mode": imap_mode,
        "imap_detailScale": imap_detailScale,
        "imap_interpolationMode": imap_interpolationMode,
        "imap_lookupMode": imap_lookupMode,
        "pmap_mode": pmap_mode
    }
    return aliasDict


def gather_scene_information():
    renderer = pm.PyNode("defaultRenderGlobals")
    if renderer.currentRenderer.get() != 'vray':
        noVrayMessage = libPySide.QCriticalBox()
        noVrayMessage.setWindowTitle("Incorrect Rendererer")
        noVrayMessage.setText("Vray is not the current renderer for this scene")
        noVrayMessage.exec_()
        raise Exception("Vray is not the current renderer for this scene")

    renderStatsQuery = _build_query_stats_()


    pm.loadPlugin("vrayformaya")
    # Set the default renderer
    renderer = pm.PyNode("defaultRenderGlobals")
    renderer.currentRenderer.set("vray")

    vraySettings = pm.PyNode("vraySettings")
    renderStats = {"Order": renderStatsQuery["Order"]}
    vrayAliases = _vray_settings_aliases_()
    # Ignore the LightInfo and Material info for now
    boolAlias = {True: "On", False: "Off"}
    for info in renderStatsQuery["Order"][:-2]:
        renderStats[info] = {}
        for attr in renderStatsQuery[info]:
            value = vraySettings.attr(attr).get()

            if vrayAliases.has_key(attr):
                value = vrayAliases[attr][value]


            # Bool alieas
            if vraySettings.attr(attr).type() == "bool":
                value = boolAlias[value]
            elif isinstance(value, (long, float, complex)):
                value = round(value, 4)

            renderStats[info][attr] = str(value)

            # attrPy = pm.PyNode(attr)
            # pyLog.info("Attribute: " + attr)
            # pyLog.info("Attribute: %s" % attrPy.get())
    # Gatger tge Shader Inforamtion
    shaderApi = libShader.MDSshaderAPI()

    materialInfo = {}

    for attr in renderStatsQuery["Material Info"]:
        for material in shaderApi.used_materials_py:
            materialInfo[material.name()] = {}
            # Check material is part of group
            if material.hasAttr(attr):
                # create a dictionary
                if not materialInfo.has_key(material.name()):
                    materialInfo[material.name()] = {}
                value = material.attr(attr).get()
                if isinstance(value, (long, float, complex)):
                    value = round(value, 4)
            materialInfo[material.name()][attr] = str(value)

    renderStats["Material Info"] = materialInfo

    # Gather any materials with shaders issues
    if shaderApi.error_shaders_py:
        renderStats["Materials With Error"] = shaderApi.error_shaders_py

    # Gather light information
    vrayLights = [u'VRayLightSphereShape',
                  u'VRayLightDomeShape',
                  u'VRayLightRectShape',
                  u'VRayLightIESShape',
                  "VRaySunShape"]
    lightInfo = {}

    for light in pm.ls(type=vrayLights):
        info = {}
        for attr in renderStatsQuery["Light Info"]:
            if light.hasAttr(attr):
                value = light.attr(attr).get()
                if isinstance(value, (long, float, complex)):
                    value = round(value, 4)
                info[attr] = str(value)

        lightInfo[light.name()] = info

    renderStats["Light Info"] = lightInfo

    return renderStats

class SceneInspect(libPySide.QMainWindow):
    def __init__(self):
        super(SceneInspect, self).__init__()
        self.setWindowTitle("Scene Inspector")

    def _capitilise_and_add_space_(self,text):
        #Captilise while keeping camelcasing
        text = libUtilities.capitalize(text.replace("_", " "))
        #Split capitilised words and add space
        text = re.sub(r"(?<=\w)([A-Z])", r" \1", text).title()
        return libUtilities.title(text)

    def _setup_(self):
        super(SceneInspect, self)._setup_()
        tabWidget = QtGui.QTabWidget()
        tabWidget.setTabBar(libPySide.VerticalTabBar(width=150, height=25))
        tabWidget.setTabPosition(QtGui.QTabWidget.West)
        renderStats = gather_scene_information()

        for key in renderStats["Order"]:
            # Build a tab only if there is some information
            if renderStats[key]:
                frame = QtGui.QFrame()
                tabWidget.addTab(frame, key.replace("_"," "))
                # Make the advanced widget for lights
                if key in ["Light Info","Material Info"]:
                    detailedInfo = renderStats[key]
                    tabLayout = QtGui.QVBoxLayout()
                    frame.setLayout(tabLayout)
                    # Iterate though the lights
                    for item in detailedInfo:
                        groupBox = libPySide.QGroupBox(item)

                        # Add a right click menu to select the node
                        groupBox.setContextMenuPolicy(libPySide.QtCore.Qt.ActionsContextMenu)
                        selectAction = QtGui.QAction(groupBox)
                        selectAction.setText("Select Node")
                        selectAction.triggered.connect(partial(pm.select,item))
                        groupBox.addAction(selectAction)

                        # Iterate through all the attributes
                        tabLayout.addWidget(groupBox)
                        for attr in detailedInfo[item]:
                            # get the value
                            label = QtGui.QLabel(detailedInfo[item][attr])
                            # Add tha label
                            groupBox.form.addRow("%s:"% self._capitilise_and_add_space_(attr), label)
                            groupBox.form.setHorizontalSpacing(30)
                # Make for the other stats
                else:
                    tabLayout = QtGui.QFormLayout()
                    frame.setLayout(tabLayout)

                    frame.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
                    tabLayout.setHorizontalSpacing(30)
                    # Iterate through all the attribute
                    for attr in renderStats[key]:
                        label = QtGui.QLabel(renderStats[key][attr])
                        tabLayout.addRow("%s:"%self._capitilise_and_add_space_(attr), label)

                     # Select the Vray settings node
                    frame.setContextMenuPolicy(libPySide.QtCore.Qt.ActionsContextMenu)

                    # Render Settings window
                    renderAction = QtGui.QAction(frame)
                    renderAction.setText("Render Settings Window")
                    renderAction.triggered.connect(partial(mel.eval,"unifiedRenderGlobalsWindow"))

                    # Select the Vray node
                    selectAction = QtGui.QAction(frame)
                    selectAction.setText("Select Vray Node")
                    selectAction.triggered.connect(partial(pm.select,"vraySettings"))

                    frame.addAction(selectAction)
            else:
                print "Pymel: No %s information was found"%key

        if renderStats.has_key("Materials With Error"):
            pass


        self.main_layout.addWidget(tabWidget)



if __name__ == '__main__':
    # export_alembic()
    # ABCTools().show()
    # win = ABCTools()
    # win.show()
    # copy_presets()
    # win =presetrendersGUI()
    # win.show()

    win = SceneInspect()
    win.show()
