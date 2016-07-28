from functools import partial

from pymel.internal.plogging import pymelLogger as pyLog

__author__ = 'pritish.dogra'

from PKD_tools import libUtilities, libGUI, libPySide, libFile, libGeo
from maya import cmds
import pymel.core as pm

import json

for mod in [libUtilities, libGUI, libPySide, libFile, libGeo]:
    reload(mod)

import MDS
import tank
import mdsYetiTools

from mdsAltusTools import *
import mdsAltusTools
reload (mdsAltusTools)


import MayaMuster
reload (MayaMuster)

reload(MDS)
import Red9


def populateName():
    #### Get version ID
    fileName = cmds.file(q=True, sn=True)[cmds.file(q=True, sn=True).rfind('/')+1:cmds.file(q=True, sn=True).rfind('.')]
    version = fileName.split("_v")[1]
    sceneName = fileName.split("_v")[0]

    #### Populate Render globals
    cmds.setAttr("vraySettings.fileNamePrefix", 'v<Version>/<Layer>/'+ sceneName + '_<Layer>_v<Version>', type="string")
    cmds.setAttr("defaultRenderGlobals.renderVersion", version, type="string")

    cmds.setAttr ("vraySettings.imgOpt_exr_autoDataWindow", 1)
    cmds.setAttr ("vraySettings.imgOpt_exr_multiPart", 1)

    print sceneName

def comingSoon():
    print "coming Soon"

def muster8GUI():
    MayaMuster.submitToMuster()

def fix_shaders():
    selection = libUtilities.get_selected()
    if selection:
        libUtilities.fix_shaders()
    else:
        libGUI.nothing_selected_box()


def _get_shotgun_fields_from_file_name_():
    import sgtk
    libUtilities.pyLog.info('Getting info from Shotgun')
    path = pm.sceneName()
    tk = sgtk.sgtk_from_path(path)
    template_obj = tk.template_from_path(path)
    fields = template_obj.get_fields(path)
    return template_obj, fields, tk


def collect_alembic_data():
    # Build the alembic dictionary
    alembicDict = {}
    for item in pm.ls(type="transform"):
        if item.hasAttr("Alembic"):
            type = item.Alembic.get()
            # Check this type of alembic top node is unique
            if item.Alembic.get() == "Camera":
                info = {"Namespace": "AnimCam"}
            elif item.namespace():
                info = {"Namespace": item.namespace()[:-1]}
            else:
                info = {"Namespace": "Alembic"}

            if item.isReferenced():
                info["FileName"] = item.referenceFile().path

            if not alembicDict.has_key(type):
                alembicDict[item.Alembic.get()] = {}

            alembicDict[item.Alembic.get()][item] = info

    return alembicDict

def add_alembic_tag():
    selection = libUtilities.get_selected()
    if selection:
        for node in selection:
            # Add the alembic Tag
            scene_name = cmds.file(query=True, sn=True)
            tk = tank.tank_from_path(scene_name)
            templ = tk.template_from_path(scene_name)
            fields = templ.get_fields(scene_name)

            asset_name = "assetNameOrShotStep"

            if "Asset" in fields:
                asset_name = fields["Asset"]

            elif "Shot" in fields:
                asset_name = fields["Step"]
         
            libUtilities.addStrAttr(node, 'Alembic')
            node.Alembic.set(asset_name)
            # Add the frame rate tag
            libUtilities.addAttr(node, "Step", 100, 0.0001, df=1)
            node.Step.setKeyable(False)
            node.Step.showInChannelBox(False)
            # Frame Relative Sample
            libUtilities.addBoolAttr(node, "RelativeFrameSample")
            node.RelativeFrameSample.setKeyable(False)
            node.RelativeFrameSample.showInChannelBox(False)
            libUtilities.addAttr(node, "RelativeLow", 100, -100, df=-.2)
            node.RelativeLow.setKeyable(False)
            node.RelativeLow.showInChannelBox(False)
            libUtilities.addAttr(node, "RelativeHigh", 100, -100, df=.2)
            node.RelativeHigh.setKeyable(False)
            node.RelativeHigh.showInChannelBox(False)
            libUtilities.addStrAttr(node, "WARNING")
            node.WARNING.set("DO NOT EDIT ANYTHING BELOW THIS ATTRIBUTE")
            node.WARNING.lock()
            libUtilities.addStrAttr(node, "ModelUsed")
            libUtilities.addStrAttr(node, "Namespace")
    else:
        libGUI.nothing_selected_box()


def remove_alembic_tag():
    selection = libUtilities.get_selected()
    if selection:
        for node in selection:
            for attribute in ["Alembic", "Step", "RelativeFrameSample", "RelativeHigh", "RelativeLow", "WARNING",
                              "ModelUsed", "Namespace"]:
                if node.hasAttr(attribute):
                    node.attr(attribute).unlock()
                    node.deleteAttr(attribute)


def publish_alembics():
    # Get all the alembic data
    alembicData = collect_alembic_data()
    # Do QC
    if not check_inconsistent_alembic(alembicData):
        # Export the alembic
        export_alembic(alembicData)


def check_inconsistent_alembic(alembicDict):
    problemDict = {}
    # Iterate through all groups
    for alembic in alembicDict:
        # Iteratate through all the custom attribute
        for attribute in ["Step", "RelativeFrameSample", "RelativeLow", "RelativeHigh"]:
            # Make the empty list
            values = []
            # Iterate through all the transforms
            for transform in alembicDict[alembic]:
                # Get all the values
                values.append(transform.attr(attribute).get())
            # Make unique list
            values = set(values)
            # Check lenght more than 1
            if len(values) > 1:
                # If so then add the dictanary items to the problem dict and break
                problemDict[alembic] = alembicDict[alembic]
                break
        else:
            # continue to the next alembic group
            continue

    # Return the problem dictionary

    return problemDict


def export_alembic(alembicDict):
    # Load the alembic plugin
    cmds.loadPlugin("AbcExport.mll", quiet=True)

    # Export the alembics
    if not alembicDict:
        noAlembic = libPySide.QCriticalBox()
        noAlembic.setText("No exportable data founds")
        msg = "No exportable data was found in your scene. Please contact your supervisor to help resolve this issue"
        noAlembic.setDetailedText(msg)
        noAlembic.exec_()
    else:
        # Try to import the sgtk or goto the toolkit
        try:
            template_obj, fields, tk = _get_shotgun_fields_from_file_name_()
        except:
            fileName = 'H:/Temp/test.abc'
            pm.AbcExport(
                j="-frameRange 1 24 -worldSpace -root %s -file %s" % (alembicDict["Character"], fileName))
            return

        libUtilities.pyLog.info('Getting the root folder')

        # Get the master alembic tempalate

        masterAlembicTemplate = tk.templates["master_alembic_cache"]
        for alembic in alembicDict:

            fields["name"] = alembic
            libUtilities.pyLog.info("Preparing Alembic for: " + alembic)
            # Set up alembic filepath
            alembicPath = masterAlembicTemplate.apply_fields(fields)

            # Check that the folder exists
            libFile.folder_check(libFile.get_parent_folder(alembicPath))

            libUtilities.pyLog.info("Alembic Path: " + alembicPath)

            # Select the topGrp
            roots = ""
            for grp in alembicDict[alembic]:
                roots += "-root %s " % grp.name()
                if alembicDict[alembic][grp].has_key("FileName"):
                    grp.ModelUsed.set(alembicDict[alembic][grp]["FileName"])
                grp.Namespace.set(alembicDict[alembic][grp]["Namespace"].replace("_RigBody_", "_"))
                step = grp.Step.get()

            relativeSample = ''
            if grp.RelativeFrameSample.get():
                relativeSample = '-frameRelativeSample %f -frameRelativeSample 0 -frameRelativeSample %f' % \
                                 (grp.RelativeLow.get(), grp.RelativeHigh.get())

            libUtilities.pyLog.info("Base Export Command")
            startFrame, endFrame = libUtilities.get_animation_time_range()

            command = "-attr ModelUsed -attr Namespace -attr scaleX -attr scaleY -attr scaleZ -attr visibility -frameRange %i %i -step %s -uvWrite -writeVisibility -worldSpace -eulerFilter -dataFormat hdf %s %s -file %s" % \
                      (startFrame,
                       endFrame,
                       step,
                       roots,
                       relativeSample,
                       alembicPath)

            libUtilities.pyLog.info('cmds.AbcExport(j="%s")' % command)

            cmds.AbcExport(j=command)

        libUtilities.pyLog.info('Export Complete')


def import_alembics():
    alembicInfo = _gather_exported_alembic_info_()
    for alembic in alembicInfo:
        pm.AbcImport(alembicInfo[alembic], mode='import')
    _reparent_imported_alembics_()


def _gather_exported_alembic_info_():
    cmds.loadPlugin("AbcImport.mll", quiet=True)

    template_obj, fields, tk = _get_shotgun_fields_from_file_name_()

    if not pm.objExists("animatedAlembicGroup"):
        pm.createNode("transform", name="animatedAlembicGroup")

    temp, fields, tk = _get_shotgun_fields_from_file_name_()
    masterAlembicTemplate = tk.templates["master_alembic_cache"]

    alembicFolder = libFile.get_parent_folder(masterAlembicTemplate.apply_fields(fields))

    # Get all the abc files

    exported_alemblic_info = {}
    if libFile.exists(alembicFolder):
        for alembicFile in libFile.listfiles(alembicFolder, "abc"):
            alembicFilePath = libFile.join(alembicFolder, alembicFile)

            # Edited by Chet 
            # Project Kitten Witch 25 May 2016
            # ========================================================
            # Old code that was causing the list of alembics to build
            # niceName =  alembicFile.split(".")[0].split("_")[]

            niceName =  alembicFile.split(".")[0]
            niceName = niceName.split("_")
            niceName = " ".join(niceName[1:])
            exported_alemblic_info[niceName] = alembicFilePath
    return exported_alemblic_info


def _reparent_imported_alembics_():
    # Put them under a unique namespace
    for node in pm.ls(assemblies=True):
        if node.hasAttr("Namespace"):
            namespace = node.Namespace.get()
            targetNodes = [node] + node.listRelatives(ad=1, type="transform")
            libUtilities.add_nodes_to_namespace(namespace, targetNodes)
            # Strip number from topGrp
            libUtilities.strip_integer(node)
            # parent under the proper group
            node.setParent("animatedAlembicGroup")


class AlembicImporter(libPySide.QDockableWindow):
    def __init__(self):
        super(AlembicImporter, self).__init__()
        # Set window name
        self.setWindowTitle("Alembic Importer")
        self.alembicInfo = _gather_exported_alembic_info_()
        self.checkBoxDict = {}
        self.setFixedWidth(162)

    def _setup_(self):
        super(AlembicImporter, self)._setup_()
        self.main_layout.setAlignment(libPySide.QtCore.Qt.AlignTop)

        if self.alembicInfo:
            # Create QGroupBox with title
            groupBox = libPySide.QGroupBox("Select Alembic To Import")

            # Iterate though the info and craete a checkbox
            for alembic in self.alembicInfo:
                print alembic
                self.checkBoxDict[alembic] = libPySide.QtGui.QCheckBox(alembic)
                groupBox.form.addRow("%s                  " % alembic, self.checkBoxDict[alembic])
            # Create the Import button
            self.import_button = libPySide.QtGui.QPushButton("Import")
            self.main_layout.addWidget(groupBox)
            self.main_layout.addWidget(self.import_button)

    def _connect_signals_(self):
        super(AlembicImporter, self)._connect_signals_()
        if self.alembicInfo:
            self.import_button.clicked.connect(self._import_alembic_)

    def _import_alembic_(self):
        for checkBox in self.checkBoxDict:
            if self.checkBoxDict[checkBox].isChecked():
                # Import the alembic if the box is checked
                print self.alembicInfo[checkBox]
                pm.AbcImport(self.alembicInfo[checkBox], mode='import')
                _reparent_imported_alembics_()

    def show(self, *args, **kwargs):
        super(AlembicImporter, self).show()
        if not self.alembicInfo:
            noAlembicError = libPySide.QCriticalBox()
            noAlembicError.setWindowTitle("Empty Folder")
            noAlembicError.setText("No Exported Alembic Data")
            noAlembicError.setDetailedText("""The alembic folder for this shot is empty""")
            noAlembicError.exec_()
            self.close()
            return

# Various Functions used in ABC

def mass_wrap():
    selection = libUtilities.get_selected()
    if selection:
        for geo in selection:
            noNameSpaceGeo = geo.split(":")[-1]
            wrap = libGeo.create_wrap(noNameSpaceGeo, geo)
            wrap.exclusiveBind.set(1)
    else:
        libGUI.nothing_selected_box()


def _process_yeti_(iterItem):
    # Return a dictanary with the namespace
    yeti_dict = {}
    for yeti_node in iterItem:
        # Get the namespace
        namespace = yeti_node.namespace()[:-1]
        # Check if the namespace exists in the master dictionary
        if not yeti_dict.has_key(namespace):
            # If not then create a new master
            yeti_dict[namespace] = []
        # Add the current shape to the reference group
        yeti_dict[namespace].append(yeti_node)

    return yeti_dict


def query_yeti_info():
    yetiFurDictionary = _process_yeti_(pm.ls(type='pgYetiMaya'))
    yetiGroomDictionary = _process_yeti_(pm.ls(type='pgYetiGroom'))
    return yetiFurDictionary, yetiGroomDictionary


def write_yeti_cache(yetiShapeDictionary, substep):
    project = cmds.workspace(q=1, rd=1)
    minRange, maxRange = libUtilities.get_animation_time_range()
    for character in yetiShapeDictionary:
        # Iterate through the yeti node per characte
        for yeti in yetiShapeDictionary[character]:
            cacheLocation = project
            for folder in ["cache", "fur", character, yeti.stripNamespace()]:
                cacheLocation = libFile.join(cacheLocation, folder)

            cacheLocation = libFile.folder_check(cacheLocation)

            # NEED TO CREATE CACHE LOCATION IF DOES NOT EXIST
            cacheName = libFile.linux_path(libFile.join(cacheLocation,
                                                        "%s_Cache_%s.fur" % (yeti.stripNamespace(), "%04d")))

            # Set cache name fields

            yeti.outputCacheFileName.set(cacheName)
            yeti.cacheFileName.set(cacheName)

            # Cache out using time sldier range and given sample count
            pm.select(yeti, r=1)

            # Set the grooms simulation
            # Turn off the all the sims

            for allGroom in pm.ls(type='pgYetiGroom'):
                allGroom.doSimulation.set(False)

            # Turn on the relavent
            if yetiShapeDictionary[character][yeti]:
                pyLog.info("Turning on simulation the following groom during the caching of %s" % (yeti))
            for groom in yetiShapeDictionary[character][yeti]:
                print groom
                groom.doSimulation.set(True)

            yeti.fileMode.set(0)
            cmd = 'pgYetiCommand -updateViewport false -writeCache "%s" -range %i %i -samples %i' \
                  % (cacheName, minRange, maxRange, substep)
            pyLog.info("Setting Fur Cache for: %s" % yeti.name())
            libUtilities.melEval(cmd, echo=True)
            yeti.fileMode.set(2)


class YetiCacheWriter(libPySide.QMainWindow):
    def __init__(self):
        super(YetiCacheWriter, self).__init__()
        self.setWindowTitle("Yeti Cache Writer")
        self.checkboxes = {}
        self.setMaximumHeight(1122)

    def _setup_(self):
        yetiNodeInfoDict, yetiGroomDict = query_yeti_info()
        super(YetiCacheWriter, self)._setup_()
        myBox = libPySide.QGroupBox()
        # Yeti Tab Widget
        tabWidget = libPySide.QtGui.QTabWidget()
        tabWidget.setTabBar(libPySide.VerticalTabBar(width=150, height=25))
        tabWidget.setTabPosition(libPySide.QtGui.QTabWidget.West)

        # Make a multi array checkbox dictonary
        for key in yetiNodeInfoDict:
            self.checkboxes[key] = {}

        for character in yetiNodeInfoDict:
            # Build a tab only if there is some information
            if yetiNodeInfoDict[character]:
                frame = libPySide.QtGui.QFrame()
                tabWidget.addTab(frame, character)
                tabLayout = libPySide.QtGui.QVBoxLayout()
                frame.setLayout(tabLayout)
                frame.setFrameStyle(libPySide.QtGui.QFrame.StyledPanel | libPySide.QtGui.QFrame.Plain)
                for yetiNode in yetiNodeInfoDict[character]:
                    mainGroomBox = libPySide.QGroupBox(yetiNode.stripNamespace())
                    tabLayout.addWidget(mainGroomBox)
                    checkBox = libPySide.QtGui.QCheckBox()
                    mainGroomBox.form.addRow("Write Cache", checkBox)

                    # Create yetiNode Dict
                    self.checkboxes[character][yetiNode] = {}
                    self.checkboxes[character][yetiNode]['node'] = checkBox
                    # Groom Dict
                    self.checkboxes[character][yetiNode]['grooms'] = {}

                    # New Widget
                    groomWidget = libPySide.QGroupBox("Groom Simulation")
                    groomForm = groomWidget.form
                    groomWidget.setLayout(groomForm)
                    groomWidget.isCollapsable = True
                    groomWidget.toggleCollapse.connect(self.resize_window)
                    groomWidget.collapse()

                    # Create groom
                    for groomNode in yetiGroomDict[character]:
                        groomCheckBox = libPySide.QtGui.QCheckBox()
                        groomForm.addRow(groomNode.stripNamespace(), groomCheckBox)
                        self.checkboxes[character][yetiNode]['grooms'][groomNode] = groomCheckBox
                        # groomCheckBox.setCheckState(libPySide.libPySide.QtCore.Qt.Checked)
                        groomCheckBox.toggled.connect(partial(self.toggle_groom_sim, yetiNode, groomNode))

                    # Add the widget to the main
                    mainGroomBox.form.addRow(groomWidget)
                    checkBox.toggled.connect(partial(self.toggle_groom, groomWidget))
                    # checkBox.toggled.connect(groomWidget.setVisible)
                    groomWidget.setVisible(False)


            else:
                print "Pymel: No %s information was found" % character


        # Add sub steo button
        self.sampleEdit = libPySide.QLineEdit()
        self.sampleEdit.setInputMask("99")
        self.sampleEdit.setText("3")
        # Add Button
        self.writeButton = libPySide.QtGui.QPushButton("Write Cache")
        # Add all the widgets

        myBox.form.addRow(tabWidget)
        myBox.form.addRow(libPySide.horizontal_divider())
        myBox.form.addRow("Samples", self.sampleEdit)
        myBox.form.addRow(libPySide.horizontal_divider())
        myBox.form.addRow(self.writeButton)

        self.main_layout.addWidget(myBox)


def _set_vray_():
    cmds.loadPlugin("vrayformaya", quiet=True)
    # Set the default renderer
    renderer = pm.PyNode("defaultRenderGlobals")
    renderer.currentRenderer.set("vray")


def rendersettings():
    _set_vray_()
    pm.mel.eval("unifiedRenderGlobalsWindow")


def set_publish_info():
    try:
        import sgtk
    except:
        shotgunErrorBox = libPySide.QCriticalBox()
        shotgunErrorBox.setText("Shotgun toolkit not loaded")
        shotgunErrorBox.setWindowTitle("Shotgun Module")
        shotgunErrorBox.exec_()
        return
    # # Evaluate the path
    path = pm.sceneName()
    #
    # # Get the toolkit
    tk = sgtk.sgtk_from_path(path)

    # # Get the nuke published area
    nukePublishFolderTemplate = tk.templates['shot_publish_area_nuke']
    #
    # Deconstruct the maya scene
    mayaTemplate = tk.template_from_path(path)
    fields = mayaTemplate.get_fields(path)
    nukePublishFolder = nukePublishFolderTemplate.apply_fields(fields)
    #
    publishNukeFile = [fileName for fileName in libFile.listfiles(nukePublishFolder) if fileName.endswith(".nk")]
    currentPublishedNuke = libFile.search_pattern_in_folder(".nk", nukePublishFolder)
    #
    # increments the version
    fields["version"] = len(publishNukeFile) + 1

    # Get the maya scene file
    mayaPublishFolderTemplate = tk.templates['maya_shot_render_folder']
    mayaPublishVersion = "v%s" % str(fields["version"]).zfill(3)
    mayaPublishVersionFolder = mayaPublishFolderTemplate.apply_fields(fields)
    mayaShotTemplate = tk.templates['shot_publish_area_maya']
    mayaProjectFolder = mayaShotTemplate.apply_fields(fields)
    mayaFileName = "%s_%s" % (fields['Shot'], mayaPublishVersion)

    renderer = pm.PyNode("defaultRenderGlobals")
    renderer.currentRenderer.set("vray")

    # Setup Vray
    _set_vray_()
    vraySettings = pm.PyNode("vraySettings")
    vraySettings.fileNamePrefix.set(mayaFileName)

    info = {"jobName": mayaFileName,
            "imagesFolder": mayaPublishVersionFolder,
            "projectFolder": mayaProjectFolder

            }
    # Set the meta data
    set_render_meta_data(vraySettings, tk)
    return info


def prep_for_publish():

    #Now using this file for management of passes and render presets. Simply update this file to drive required setup
    cmds.file('//productions/boad/Pipeline/tools/maya/rendering/presets/passTemplate_v002.ma',type='mayaAscii',i=True, reference=False, mergeNamespacesOnClash=True, namespace=':')

    # _set_vray_()
    # vraySettings = pm.PyNode("vraySettings")
    # vraySettings.cam_mbOn.set(1)
    # vraySettings.cam_mbDuration.set(0.50)
    # vraySettings.cam_mbIntervalCenter.set(0)
    # vraySettings.cam_mbShutterEfficiency.set(0.5)
    # vraySettings.cam_mbPrepassSamples.set(1)
    # vraySettings.cam_mbGeomSamples.set(2)
    # vraySettings.cam_mbCameraMotionBlur.set(1)
    # vraySettings.cmap_adaptationOnly.set(1)
    # # Add the Render Elements
    # renderElements = ["diffuseChannel",
    #                   "lightingChannel",
    #                   "reflectChannel",
    #                   "shadowChannel",
    #                   "specularChannel",
    #                   "giChannel",
    #                   "refractChannel",
    #                   "FastSSS2Channel",

    #                   ]
    # for re in renderElements:
    #     pm.mel.eval('vrayAddRenderElement %s' % re)

    # depthPass = pm.mel.eval('vrayAddRenderElement zdepthChannel')

    # # setting appropriate settings for zdepth pass
    # cmds.setAttr('%s.vray_filtering_zdepth' % (depthPass), 0)
    # cmds.setAttr('%s.vray_depthClamp' % (depthPass), 0)


def set_render_meta_data(vraySettings, tank):
    vraySettings.imageFormatStr.set("exr (multichannel)")
    # Setup the meta data dependency
    dependencies = []
    try:
        for ref in pm.listReferences():
            validatedPublish = tank.template_from_path(ref.path)
            if validatedPublish:
                if "work" in ref.path and ref.isLoaded():
                    raise TypeError
                elif "work" not in ref.path:
                    dependencies.append(ref.path)

    except TypeError:
        workFiles = libPySide.QCriticalBox()
        workFiles.setText("Unable to publish with WIP assets")
        msg = "Your scene contains Work in progress(WIP) references. Please switch to a published asset or unload it. \n\n Example: \n%s" % ref.path
        workFiles.setDetailedText(msg)
        workFiles.setWindowTitle("WIP Assets")
        workFiles.exec_()

    shotgunInfo = {"SourceMayaFile": pm.sceneName(), "Dependencies": dependencies}
    shotgunJson = libFile.json.dumps(shotgunInfo)
    vraySettings.imgOpt_exr_attributes.set('ShotgunInfo = "%s";' % shotgunJson)


class MusterGUI(MDS.MusterGUI):

    def _set_publish_setup_(self):
        # Disable the folder
        self.imageFolderEdit.setEnabled(False)
        self.projectFolderEdit.setEnabled(False)
        self.jobnameEdit.setEnabled(False)
        #
        self.priorityEdit.setText("5")
        jobInfo = set_publish_info()

        self.imageFolderEdit.setText(jobInfo["imagesFolder"])
        self.projectFolderEdit.setText(jobInfo["projectFolder"])
        self.jobnameEdit.setText(jobInfo["jobName"])

    def _setup_pools_(self):
        # Get the pool list

        pools = self.musterApi.get_pools()

        for pool in pools:
            if "BOAD" in pool and "Nuke" not in pool:
                self.poolsCombo.addItem(pool)

    def _set_state_(self):
        # Disable the Publish Checkbox
        self.outRadioButtonGrp.buttons()[1].setEnabled(("Light" in pm.sceneName()))
        self.outRadioButtonGrp.buttons()[0].setChecked(True)
        self._set_render_folders_()


class AlembicExporter(libPySide.QDockableWindow):
    def __init__(self):
        super(AlembicExporter, self).__init__()
        # Set window name
        self.setWindowTitle("Alembic Exporter")
        self.err_labels = {}
        self.alembicDict = collect_alembic_data()

    def _setup_(self):
        super(AlembicExporter, self)._setup_()

        self.exportList = []

        self.col_box = libPySide.QtGui.QGroupBox()
        self.col_layout = libPySide.QtGui.QGridLayout()
        self.exp_button = libPySide.QtGui.QPushButton("Export")
        self.exp_button.released.connect(self._export_)

        self.layoutErr = libPySide.QtGui.QGridLayout()
        self.err_box = libPySide.QtGui.QGroupBox("Error Log:")
        self.err_box.setLayout(self.layoutErr)

        self.tabs = libPySide.CheckableTabWidget()
        self.tabs.setTabBar(libPySide.QtGui.QTabBar())
        # Creating tabs
        for alembic in self.alembicDict:
            typeBox = libPySide.QtGui.QGroupBox()
            layout = libPySide.QtGui.QGridLayout()
            layout.setAlignment(libPySide.QtCore.Qt.AlignTop)
            # Adding buttons with object name and signal to each tab
            for transform in self.alembicDict[alembic]:
                slButton = libPySide.QtGui.QPushButton("%s" % transform.name())
                slButton.clicked.connect(transform.select)
                layout.addWidget(slButton)
                typeBox.setLayout(layout)
            self.tabs.addTab(typeBox, alembic)

        self.main_layout.addWidget(self.tabs)
        self.tabs.stateChanged.connect(self.checkErrors)
        self.main_layout.addWidget(self.err_box)
        self.main_layout.addWidget(self.exp_button)

    def checkErrors(self, index, checkState, title):
        probDict = check_inconsistent_alembic(self.alembicDict)
        checkKeys = probDict.keys()
        if bool(checkState) == 1:
            self.exportList.append(title)
            if not self.err_labels.has_key(title):
                self.err_labels[title] = libPySide.QtGui.QLabel()
                self.layoutErr.addWidget(self.err_labels[title], index, 0)
            if title in checkKeys:
                self.err_labels[title].setText(
                    "\n<font color='red'>Inconsistency found in the %s alembic nodes.</font>" % title)
            else:
                self.err_labels[title].setText(
                    "\n<font color='green'>No errors found in %s, please proceed.</font>" % title)
        elif bool(checkState) == 0:
            if self.err_labels.has_key(title):
                self.err_labels[title].clear()
                self.layoutErr.removeWidget(self.err_labels[title])
                del self.err_labels[title]
            self.exportList.remove(title)

    def _export_(self):
        # Build the export dictionary
        exportDict = {}
        for target in self.exportList:
            exportDict[target] = self.alembicDict[target]
        export_alembic(exportDict)


def get_cam_list():
    renderCams = []
    for camera in pm.ls(type="camera"):
        if camera.name() not in [u'frontShape', u'perspShape', u'sideShape', u'topShape']:
            renderCams.append(camera.getParent())
        else:
            # Disable the preset camera for rendering
            camera.renderable.set(0)

    return renderCams


class publishPrepGUI(libPySide.QDockableWindow):
    def __init__(self):
        super(publishPrepGUI, self).__init__()
        self.setWindowTitle("Set Passes")
        # Load the presets
        _set_vray_()
        self.customCameraStatus = True

    def _setup_(self):
        super(publishPrepGUI, self)._setup_()
        self.main_layout.setAlignment(libPySide.QtCore.Qt.AlignTop)

        # Add The text
        camLabel = libPySide.QtGui.QLabel()
        camLabel.setText("<b>Set Render Camera</b>")
        self.main_layout.addWidget(camLabel)

        self.cameraBox = libPySide.QtGui.QComboBox()
        cameras = get_cam_list()

        if not cameras:
            self.customCameraStatus = False
            self.cameraBox.addItem("No Custom Camera")
        else:
            self.cameraBox.addItems(libUtilities.stringList(cameras))

        self.main_layout.addWidget(self.cameraBox)

        # Setup Render publish
        divider = libPySide.horizontal_divider()
        self.main_layout.addWidget(divider)

        # add publish button
        self.publishButton = libPySide.QtGui.QPushButton("Set Passes")
        self.main_layout.addWidget(self.publishButton)

    def _connect_signals_(self):
        super(publishPrepGUI, self)._connect_signals_()
        if self.customCameraStatus:
            self.cameraBox.currentIndexChanged.connect(self._set_cam_)
        # Set the current cam
        self._set_cam_()
        self.publishButton.clicked.connect(prep_for_publish)

    def _set_cam_(self):
        cam_text = self.cameraBox.currentText()
        if cam_text != "No Custom Camera":
            camera = pm.PyNode(self.cameraBox.currentText())
            camera.renderable.set(1)
            for otherCamera in get_cam_list():
                if camera != otherCamera:
                    otherCamera.renderable.set(0)
            pyLog.warning("Current Render Camera: %s" % camera)

    def _get_selected_preset_(self):
        selectButton = self.radioButtonGrp.checkedButton()
        return selectButton.renderPreset


class MDSShotgunTools(MDS.MDSTools):
    def __init__(self):
        super(MDSShotgunTools, self).__init__()
        self.setWindowTitle("MDS Shotgun Tools")

    def _muster_console_(self):
        reload (MayaMuster)
        MayaMuster.submitToMuster()

    def _alembic_exporter_(self):
        win = AlembicExporter()
        win.show()

    def setTabInfo(self):
        super(MDSShotgunTools, self).setTabInfo()

        animTools = {
            "Import Alembics": {"Func": libGUI.partial(self._launch_window_, AlembicImporter),"Tooltip": "Use to import alembic camera for this shot"},
            "Tangent Swapper": {"Func": self._tangent_swapper_,"Tooltip": "Quickly change your tangents for your animation scene"},
            "Fix Shaders": {"Func": fix_shaders,"Tooltip": "Fix the shaders for referenced in rigs."},
            "Red9 Pack": {"Func": libGUI.partial(Red9.start),"Tooltip": "Red9 animation tools."},

            "Order": ["Import Alembics","Fix Shaders","Tangent Swapper","Red9 Pack"]
        }

        Rendering = {
            "Import Alembics": {"Func": libGUI.partial(self._launch_window_, AlembicImporter),"Tooltip": "Import all alembics for this shot"},
            "Set Render Path": {"Func": populateName,"Tooltip": "Sets the correct naming for your render"},
            "Open Render Settings": {"Func": rendersettings,"Tooltip": "Bring up the Maya render settings"},
            "Set Passes": {"Func": libGUI.partial(self._launch_window_, publishPrepGUI),"Tooltip": "Bring up the preset renders GUI"},
            "Altus Setup": {"Func": ALTUSwinUI,"Tooltip": "Launch MDS Altus Tool"},
            "Muster Console": {"Func": muster8GUI,"Tooltip": "Send the your existing maya scene to Muster"},
            "Mass Wrap": {"Func": mass_wrap,"Tooltip": "Wrap the selected referenced geometry to it's alembic counterpart"},

            "Order": ["Import Alembics","Mass Wrap","Open Render Settings","Set Passes","Set Render Path","Altus Setup","Muster Console"]

        }

        # Converting General Tab to Group based one
        defaultGeneralTab = self.tabInfo["&General"]
        defaultGeneralTools = defaultGeneralTab["Order"]

        defaultGeneralTab["Add Alembic Tag"] = {"Func": add_alembic_tag,"Tooltip": "Add the Alembic Tag"}
        defaultGeneralTab["Remove Alembic Tag"] = {"Func": remove_alembic_tag,"Tooltip": "Remove the Alembic Tag"}
        defaultGeneralTab["Alembic Exporter"] = {"Func": libGUI.partial(self._launch_window_, AlembicExporter),"Tooltip": "Manually export alembics for your shot without publishing"}

        defaultGeneralTab["Groups"] = [{"Alembic Tagging": ["Add Alembic Tag", "Remove Alembic Tag", "Alembic Exporter"]},{"Misc": defaultGeneralTools}]

        del defaultGeneralTab["Order"]

        # Adding "Yeti Cache Writer"
        fxTools = self.tabInfo["&FX"]
        fxTools["Yeti Cache Writer"] = {"Func": libGUI.partial(self._launch_window_, YetiCacheWriter),"Tooltip": "Write the Yeti Cache for the shot"}
        fxTools["Publish Yeti Cache"] = {"Func": mdsYetiTools.mdsPrePublishYetiCache,"Tooltip": "Create's a proxy cache node suitable for publishing"}
        fxTools["Yeti Scene Setup"] = {"Func": mdsYetiTools.mdsYetiSetupCall,"Tooltip": "Join Yeti required basemesh to the Anim Alembic"}
        fxTools["Groom Collision"] = {"Func": mdsYetiTools.mdsYetiGroomCollideWith, "Tooltip": "Set Collision for the Yeti Grooms"}

        #fxTools["Groups"][1]["MDS"].append("Yeti Cache Writer")
        fxTools["Groups"][1]["MDS Yeti Tools"].append("Yeti Scene Setup")
        fxTools["Groups"][1]["MDS Yeti Tools"].append("Groom Collision")
        fxTools["Groups"][1]["MDS Yeti Tools"].append("Publish Yeti Cache")



        #
        self.tabInfo["&General"] = defaultGeneralTab
        self.tabInfo["&Modelling"] = defaultGeneralTab
        self.tabInfo["&Animation"] = animTools
        self.tabInfo["&Lighting"] = Rendering
        self.tabInfo["Order"] = ["&Modelling","&Rigging","&Animation","&Surfacing","&FX","&Lighting"]


if __name__ == '__main__':
    # export_alembic()
    # ABCTools().show()
    win = AlembicImporter()
    win.show()


    # export_alembic(_collect_alembic_data_())

    # import_alembics()
    # clean_geo()
