"""
Created on 17/06/2013

@author: Owner
"""
import pymel.core as pm
import maya.cmds as cmds


#     from libs import libUtilities
#     from libs import libFile
#     from libs import libXml
# except:
from PKD_tools import libUtilities
from PKD_tools import libFile
from PKD_tools import libXml

for module in libFile, libUtilities, libXml:
    reload(module)

from pymel.internal.plogging import pymelLogger

# global colorMap
# colorMap = ["color",
# "transparency",
# "reflectionColor",
# "reflectionExitColor",
# "refractionColor",
# "refractionExitColor",
# "fogColor",
# "bumpMap",
# "translucencyColor"
# ]


DEBUG = True


def list_missing_path():
    nodes = []
    fileList = []
    for node in pm.ls(type="file"):
        path = node.fileTextureName.get()
        if not libFile.exists(path):
            fileList.append(path)
            nodes.append(node)
            print("Node: %s" % node)
            print("Path: %s" % path)


def remap_missing_path(search, replace):
    """Remap Missing Texture"""
    for node in pm.ls(type="file"):
        path = node.fileTextureName.get()
        if not libFile.exists(path):
            node.fileTextureName.set(path.replace(search, replace))


class ShaderAPI(object):
    def __init__(self):
        """
        The Shader API constructor.
        """
        self.textureFolder = None
        self._data_folder_ = ""
        self.__init_internal__()
        self._preset_path_ = "//file04/Repository/maya/2016/plugins/mds/scripts/PKD_tools"
        self._namespace_ = ''

    def __init_internal__(self):
        """Setup the internal variables which can be refreshed at a later state"""
        self._used_shaders_ = None
        self._sub_shaders_ = None
        self._all_shaders_ = None
        self._error_shaders_ = []

    def create_shader(self, shader_name='my_shader'):
        """"Creates lambert shader and the relevant shaderGroup"""
        if not pm.objExists(shader_name):
            shader = pm.shadingNode('lambert', asShader=True, name=shader_name)
            shading_group = pm.sets(
                renderable=True,
                noSurfaceShader=True,
                empty=True,
                name=shader + 'SG'
            )
            shader.outColor.connect(shading_group.surfaceShader)
            return [shader, shading_group]
        else:
            return [shader_name, shader_name + 'SG']

    def assign_shader(self, shading_group, node, shapePrefix=""):
        """Assign shader to a shading_group for given a node or list of nodes"""
        if isinstance(node, list):
            self.safe_select_meshList(node, shapePrefix)
        else:
            self.safe_select_meshList([node], shapePrefix)
        if pm.ls(sl=1):
            try:
                pm.sets(shading_group, e=1, forceElement=1)
                pm.select(cl=1)
            except:
                "Error assigning shaders to objects"
        else:
            print(
                "No Geo or Dags Was Selected. Nothing Assigned to " + shading_group)
            # sets(shading_group, e=True, forceElement=node)

    def delete_unused_shaders_in_scene(self):
        """Removes all unused shaders"""
        removedShaders = []
        # Get list of shaderEngines
        for sg in self.all_shaders_py:
            # Check to see if the current shader engine is not a used_shader or
            # sub_shader
            if sg not in self.used_shaders_py + self.sub_shaders_py:
                # Check to see that current shader engine is not a subset of
                # used engine
                removedShaders.append(str(sg))
                self.safe_delete_shading_network(sg)

        if removedShaders:
            return removedShaders

    def delete_shaders_in_scene(self):
        """Remove all shaders from Scene"""
        for engine in self.all_shaders_py:
            self.safe_delete_shading_network(engine)

    def clean_shaders_in_scene(self):
        """Export Scene essentially removes it and removes any junk shaders"""
        self.extract_all_shaders_from_scene()
        self.import_all_shading_and_connection_info()

    def extract_all_shaders_from_scene(self):
        """Extract Shaders from Network and leave behind the relevent shape/dag nodes"""
        for shadingEngine in self.all_shaders_py:
            # Try to attempt to extract shader with meshList
            if "initial" not in shadingEngine:
                self.extract_shader_from_scene(shadingEngine)

        # Attempt to delete the rest of the shadering network
        for shadingEngine in self.all_shaders_py:
            self.safe_delete_shading_network(shadingEngine)

    def extract_shader_from_scene(self, shadingEngine):
        """Extract Individual Shader from Scene and leave behind any relevent"""
        self.export_shading_and_connection_info(shadingEngine, rebuild=0)
        self.safe_delete_shading_network(shadingEngine)

    # def _determine_final_outputFile_(self,imagePath,newPath,suffix):
    # """ Internal process used by the converts"""
    # Collect all relevant read write file information
    # fileName,savePath,ext=_process_file_info_(imagePath,newPath)
    #     if suffix:
    #         outputFile=fileName+"_"+suffix+".jpg"
    #     else:
    #         outputFile=fileName+".jpg"
    #     return (savePath+outputFile)

    # def _process_file_info_(self,imagePath,newFilePath=None):
    #     """Process File Info. Internal process used by the converts"""
    #     fileName,savePath,ext=libFile.get_file_folder_extension(imagePath)
    # Determine if it is relative path or absolute path
    #     if newFilePath:
    #         if libFile.exists(newFilePath):
    #             savePath=libFile.safePath(newFilePath)
    #         else:
    #             savePath=libFile.join(savePath,newFilePath)
    #     return fileName,savePath,ext

    def rename_all_shading_network(self):
        """Rename Shading Network"""
        sub_shaders = self.sub_shaders_py
        for sg in self.all_shaders_py:
            sg = str(sg)
            if ":" not in sg and sg not in sub_shaders:
                global DEBUG
                if DEBUG:
                    print("_" * 10)
                    print("RENAMING NETWORK:" + sg)
                self.rename_shader_network(sg)

    def rename_shader_network(self, shadingEngine):
        """Rename Shading Network based on convention. THIS WOULD CHANGE IN THE FUTURE"""

        # Rename the shading engine
        shadingEngine = pm.PyNode(shadingEngine)
        self.rename_shading_node(shadingEngine, shadingEngine)


        # Rename the subShaders
        # if DEBUG:
        #     print "_"*10
        #     print self.detailed_sub_shaders.has_key(str(shadingOldEngineName))
        #     print "_"*10
        self._rename_subshaders_(shadingEngine)

        primaryShaderNodes = []

        # Iterate through all the materials connected to the shading engine
        for node in self.get_network_nodes(shadingEngine, 1, 0):
            primaryShaderNodes.append(node)
            self.rename_shading_node(node, shadingEngine)


        # Iterate through all shaders
        # materials(Vray) = shaders(mentalRay)
        for primaryShader in primaryShaderNodes:
            for shaderNode in self.prune_dag_shape(pm.listHistory(primaryShader, ac=1)[1:]):
                self.rename_shading_node(shaderNode, shadingEngine, primaryShader)

        # Do we rename duplicates in name
        self._rename_duplicate_nodes_in_sg_(shadingEngine)

    def _rename_subshaders_(self, shadingEngine):
        """Rename all subshaders"""
        if self.detailed_sub_shaders_py.has_key(shadingEngine):
            subShaderList = self.detailed_sub_shaders_py[shadingEngine]
            component = str(shadingEngine).split("_")[0]
            for subShader, iteration in zip(subShaderList, range(len(subShaderList))):
                pm.rename(subShader, "%s_%i_SubSG" %
                          (component, iteration + 1))

    def _rename_duplicate_nodes_in_sg_(self, shadingEngine):
        """Rename duplicates Nodes in Shading Group"""
        networkNodes = self.get_network_nodes(shadingEngine, returnEngine=False)
        self._rename_duplicate_nodes_(networkNodes)

    def _rename_duplicate_nodes_(self, networkNodes):
        """Rename duplicates Nodes with 1,2,3 etc at the end"""
        # Construct Duplicate Item Dictionary
        dupItemDict = []
        for checkItem in networkNodes:
            # Check if last letter has a digit
            if checkItem.name()[-1].isdigit():
                createPureNode = True
                # Check if a new pureName needs to be constructed
                for checkDup in dupItemDict:
                    # Check to see if this if there are part of duplicated
                    # nodes
                    if checkItem in checkDup['Duplicates']:
                        createPureNode = False
                        break
                # Construct pure node and duplicate dictuonary item
                if createPureNode:
                    # Prune numbers from end of the node
                    noDigNum = 0
                    checkItem = str(checkItem)
                    for i in range(len(checkItem) - 1, -1, -1):
                        if not checkItem[i].isdigit():
                            noDigNum = i + 1
                            break
                    pureNode = checkItem[0:noDigNum]
                    # Get all duplicate names with wild card
                    dupItemDict.append(
                        {'PureNode': pureNode,
                         'Duplicates': pm.ls(pureNode + "*")}
                    )
        # Go through dictionary and remove the duplicate name
        for dupItem in dupItemDict:
            # Rename duplicates to a templname
            dupNodes = dupItem['Duplicates']
            for dupNode in dupNodes:
                dupNode.rename("PKD_TempName_Alpha1")
            # Split the pureName
            splitPure = dupItem['PureNode'].split("_")
            # Iterate through duplicate again
            for i in range(len(dupNodes)):
                newName = ""
                # Construct new name with relevant integer
                for k in range(len(splitPure)):
                    if k == 1:
                        newName = newName + str(i)
                    else:
                        newName = newName + splitPure[k]
                    if k < (len(splitPure) - 1):
                        newName = newName + "_"

                dupNodes[i].rename(newName)

    def rename_shading_node(self, node, shadingEngine, shader=None):
        """

        Default Naming Convention

        ShadingObject_Iteration_(attribute in which the last Node to the Material)_Nodetype

        For example,     color file node which is conneted to the connected to the primary color of the shader would be named
        "Skin_0_Color_File"

        Shadering Engine and Primary Material connected to the shading engine would be renamed as

        ShadadingObject_0_Nodetype

        eg "Skin_0_CM","Hair_0_Lambert"

        """
        global DEBUG

        node = pm.PyNode(node)
        baseName = self.get_base_name(shadingEngine, node)
        nodeName = self.get_node_name(node)

        if shader is not None:
            postFix = self.get_final_connection_postfix(node, shader)
            targetName = "%s_0_%s_%s" % (str(baseName), postFix, nodeName)
            # Check to see if the node can be renamed
        else:
            targetName = "%s_0_%s" % (str(baseName), nodeName)

        try:
            node.rename(targetName)
        except:
            print("Unable to Rename Read Only Node:" + node)

    def get_base_name(self, shadingEngine, *args):
        """Defines where do we get the base name for this shading engine. By default we look to the shading engine"""
        # Split Strip the interger

        baseName = self._format_name_(shadingEngine)
        print ("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print "basename = {}".format(basename)
        print ("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return libUtilities.strip_integer_in_string()

    def _format_name_(self, node):
        """Split the name and remove any trailing numbers"""
        text = libUtilities.strip_integer_in_string(node.name().split("_")[0])
        # Preserve camelcasing

        try:

            text = libUtilities.capitalize(text)
        except:
            libUtilities.pyLog.error("Error capitialising on: $s" % node)

        return text

    def check_shading_engine_name(self):
        name_error = []
        for shader in self.used_shaders_py:
            if not str(shader).endswith("_SG"):
                name_error.append(str(shader))
        if name_error:
            name_error.insert(0, "The Following Shader Are Not Named Properly")
            print("Incorrect Named Shaders ")
            for name in name_error:
                print(name)
            return [False, name_error]
        else:
            return [True]

    def list_shaders_missing_color_file(self):
        "Print out list of shaders with missing color file"
        withFileShaders = []
        for shader in pm.ls(type="shadingEngine"):
            if self.get_connected_shapes(shader):
                for node in self.get_network_nodes(shader):
                    if node.nodeType() == "file":
                        withFileShaders.append(shader)
                        break
        missingColorFile = []
        for shader in withFileShaders:
            if not pm.objExists(shader.name()[0:-2] + "C_File"):
                missingColorFile.append(shader)

        if missingColorFile:
            colorError = ["The Following Shader Do Not Have a Color Map"]
            print("Missing Color Maps")
            for shader in withFileShaders:
                colorError.append(shader.name())
                print(shader)
            return [False, colorError]
        else:
            return [True]

    def get_material(self, shadingEngine):
        """Get the main material connected to the shading engine"""
        connections = pm.PyNode(shadingEngine).surfaceShader.listConnections()
        if connections:
            return connections[0]

    def get_shadingEngine(self, node):
        """
         Get Shading Engine For a given node
        @code
        libShader.get_shadingEngine('pCube4')
        @endcode
        """
        shadingEngines = None
        history = None
        try:
            history = pm.listHistory(node, f=1, ac=1)
        except:
            print("No Shader Defined For:" + node)
        if history:
            for item in history:
                # Make sure that the shading engine is not a subShader
                if item.type() == "shadingEngine" and item.name() not in self.sub_shaders and item.name() != "initialShadingGroup":
                    return item

    # def get_all_shaderEngines(self):
    #     shadingEngines=[]
    #     for engineName in cmds.ls(type="shadingEngine"):
    #         if engineName not in ["initialShadingGroup","initialParticleSE","lambert1","particleCloud1"]:
    #             shadingEngines.append(engineName)
    #     return shadingEngines

    def get_node_name(self, node):
        """Retrieve Node Type name"""
        nodeName = node.type()

        # ___Dictionary would be expanded as needs__
        # nodeDirectory=[
        #  {'node': "shadingEngine", 'shortform': "SG"},
        #  {'node': "place2dTexture", 'shortform': "Place2D"},
        #  {'node': "place3dTexture", 'shortform': "Place3d"},
        #  {'node': "mentalrayTexture", 'shortform': "File"}
        # ]

        nodeDirectory = self.load_alias_info("node")

        # Get name from directory, otherwise capitlise
        shortName = ""
        for entry in nodeDirectory:
            if entry['node'] == nodeName:
                shortName = entry['shortform']
        if shortName:
            nodeName = shortName
        else:
            nodeName = libUtilities.capitalize(nodeName)
        return nodeName

    def _list_history_(self, node, *args, **kwargs):
        # List history without any of the dag objects

        # Pymel was erroring on 'swatchShadingGroup' which seems to randomly come up
        # quering the file node

        historyNodes = []
        for historyNode in cmds.listHistory(node.name(), *args, **kwargs):
            if pm.objExists(historyNode):
                historyNodes.append(pm.PyNode(historyNode))
            else:
                pymelLogger.info("Virtual Node:" % historyNode)
        result = self.prune_dag_shape(list(set(historyNodes)))
        if node in result:
            result.remove(node)
        return result

    def get_final_connection_postfix(self, node, shader):
        """Get postfix Based on connection plugged into the material"""
        postFix = ""
        pymelLogger.info("Analysing: %s" % node)
        # List all the main nodes connected to the shaders
        mainNodes = self._list_history_(shader, levels=1, allConnections=True)
        # Is the current node one of those main nodes
        if node in mainNodes:
            #  get me the get_postfix_attr()
            pymelLogger.info("This is a node that directly connected to the primary shader" % node)
            postFix = self.get_postfix_attr(node, shader)
        else:
            # List the future history of node
            allFutureNodes = self._list_history_(node, allFuture=True, future=True)
            pymelLogger.info("Analysing Future Nodes")
            # Count how many times the main nodes occur in the history
            mainNodeList = []
            for mainNode in mainNodes:
                if mainNode in allFutureNodes:
                    mainNodeList.append(mainNode)

            # Are there more than one main node in the history
            if len(mainNodeList) == 1:
                # Get me the postfix node node based on one main node
                postFix = self.get_postfix_attr(mainNodeList[0], shader)
            else:
                # Then this is Multi node connections
                pymelLogger.info("This node has a affect on more than one node that is connected to the primary shader")
                # pymelLogger.info(allFutureNodes)
                # pymelLogger.info(mainNodeList)
                postFix = "Multi"

        pymelLogger.info("Result: %s" % postFix)
        pymelLogger.info("Analysis Complete on: %s" % node)
        pymelLogger.info("#" * 10)
        return postFix

    #     con = self.valid_connections(node)
    #     if len(con) == 1:
    #         lastNode = self.get_last_connected_node(node, shader)
    #         if lastNode:
    #             postFix = self.get_postfix_attr(lastNode, shader)
    #         else:
    #             postFix = "Multi"
    #     else:
    #         postFix = "Multi"
    #     return postFix
    #
    # def get_last_connected_node(self, node, shader):
    #     """Last node Connected to shader"""
    #     lastCon = None
    #     con = self.valid_connections(node)
    #     if len(con) == 1:
    #         #Are we looking at the material at the
    #         if con[0] == shader:
    #             lastCon = node
    #         else:
    #             lastCon = self.get_last_connected_node(con[0], shader)
    #     return lastCon



    def get_postfix_attr(self, lastNode, shader):
        """Get post fix based on the attribute the lastnode is connected to the shader"""
        pymelLogger.info("Analysing connections to the primary material")
        postFix = ""
        # Attribute Shader Directory. A shortcut

        attrDirectory = self.load_alias_info("attr")
        # Find the attribute connected to the shader

        cons = self.valid_connections(lastNode, 1, 1)
        shaderConnections = []
        for con in cons:
            if str(shader) in con:
                shaderConnections.append(con)
                # shaderCon = con

        attr = ""

        if len(shaderConnections) > 1:
            # Since there are multiple attribute connected to the same node the postfix should be Multi
            pymelLogger.info("There are more than one attributes connected to the primary shader")
            return "Multi"
        else:

            attr = shaderConnections[0].split(str(shader) + ".")[-1]
            pymelLogger.info("Direct Connection on: %s" % attr)

        # Find in the shortform dictionary
        for entry in attrDirectory:
            if entry['attribute'] == attr:
                pymelLogger.info("Found an attribute in the overide data")
                postFix = entry['shortform']
        # If not in list then make one
        # ____For safety we really should be adding in the dictonary___
        if not postFix:
            if "_" in attr:
                splitName = attr.split("_")
                postFix = (splitName[0][0].capitalize()
                           + splitName[1][0].capitalize())
            else:
                capChars = filter(self.__isCap__, attr)
                if capChars:
                    postFix = attr[0].capitalize() + capChars[0]
                else:
                    postFix = attr.capitalize()
        return postFix

    def get_connected_shapes(self, shadingEngine):
        """Return all shapes connected to a particular shape or dag"""
        pm.select(cl=1)
        connectedObjects = []

        if cmds.about(batch=True):
            try:
                connectedObjects = pm.sets("Body_0_SG", q=1)
            except:
                print("NO SHADERS")
        else:
            # pm.hyperShade(objects=shadingEngine)
            connectedObjects = pm.sets(shadingEngine, q=1)
        if connectedObjects is None:
            connectedObjects = []
        return connectedObjects

    def get_network_nodes(self, shadingEngine, level=0, returnEngine=True, allConnections=False):
        """Get the shading network information without any transform or shape information"""
        shadingNetworkNodes = self.prune_dag_shape(
            pm.listHistory(shadingEngine, lv=level, ac=allConnections))
        # In case select the network only. If you select the shadingEngine,
        # maya automatically selects the dags/in the set
        if not returnEngine:
            if shadingEngine in shadingNetworkNodes:
                shadingNetworkNodes.remove(shadingEngine)
        return shadingNetworkNodes

    def get_rendering_info(self, shapeList):

        pureShapeList = []
        dags = []
        for stuff in shapeList:
            # thisNodeType=libNode.identify(stuff)
            thisNodeType = stuff.type()
            if thisNodeType == "transform":
                dags.append(stuff)
            elif thisNodeType in ['mesh']:
                pureShapeList.append(pm.PyNode(stuff.split(".")[0]))

        pureShapeList = list(set(pureShapeList))

        shapeAttributeList = self.load_attr_info("shape")

        shapeDictionaryList = []
        for shape in pureShapeList:
            dags.append(shape.getParent())
            shapeAttributeDictionary = []
            for attr in shapeAttributeList:
                self._build_attr_info_(shape, attr, shapeAttributeDictionary)
            shapeDictionaryList.append(
                {"shape": str(shape), "renderingInfo": shapeAttributeDictionary})

        dags = list(set(dags))

        dagAttributeList = self.load_attr_info("dag")

        dagDictionaryList = []

        for dag in dags:
            attributeDictionary = []
            for attr in dagAttributeList:
                if dag.hasAttr(attr):
                    attributeDictionary.append(
                        {'attribute': attr, 'value': float(pm.getAttr(dag + "." + attr))})
            dagDictionaryList.append(
                {"dag": str(dag), "renderingInfo": attributeDictionary})

        return {"dagsInfo": dagDictionaryList, "shapesInfo": shapeDictionaryList}

    def _build_attr_info_(self, target, attribute, listDictionary):
        if target.hasAttr(attribute):
            attribute = target + "." + attribute
            attrType = pm.getAttr(attribute, typ=1)
            if attrType not in ["message", "TdataCompound"]:
                if attrType == "string":
                    listDictionary.append(
                        {'attribute': attribute, 'value': pm.getAttr(attribute), 'type': 'string'})
                else:
                    try:
                        float(pm.getAttr(attribute))
                    except:
                        print(attribute)
                        print(attrType)
                    listDictionary.append(
                        {'attribute': attribute, 'value': float(pm.getAttr(attribute)), 'type': 'float'})

    def __isCap__(self, x):
        """Quick internal function to check capitial letter on a character"""
        return x.isupper()

    def valid_connections(self, node, strType=0, plugs=0):
        """Return Connections without junk info"""

        validConnections = []
        connections = []
        # Pymel was erroring on 'swatchShadingGroup.surfaceShader' which seems to randomly come up
        # quering th file node
        for connection in cmds.listConnections(node.name(), s=0, p=plugs):
            if pm.objExists(connection):
                connections.append(pm.PyNode(connection))
        connections = list(connections)
        for connection in connections:
            appendCon = True
            # Also ignore any sub_shaders
            nonValidStrings = [
                "mentalrayGlobals", "materialInfo", "default", "hyper"]
            nonValidStrings += self.sub_shaders
            for nonValidString in nonValidStrings:
                if nonValidString in str(connection) or connection.type() == nonValidString:
                    appendCon = False
                    break
            if appendCon:
                if strType:
                    validConnections.append(str(connection))
                else:
                    validConnections.append(connection)
        return validConnections

    def safe_delete_shading_network(self, shadingEngine):
        """Delete Shader Network without deleting any dags or shapes. Also assign default lambert to a shader"""
        shadingEngineName = str(shadingEngine)
        if shadingEngineName not in ["initialShadingGroup", "initialParticleSE", "lambert1", "particleCloud1"]:

            if DEBUG:
                print("_" * 10)
            if DEBUG:
                print("Attempting to remove the shading network attached to: " + shadingEngine)
            meshList = self.get_connected_shapes(shadingEngine)
            if meshList:
                self.assign_shader("initialShadingGroup", meshList)
            self.disconnect_mesh_from_network(shadingEngine)
            for node in self.get_network_nodes(shadingEngine):
                # Attempt to delete node. Catch error if maya deletes a unused
                # node when deleting a connected node
                try:
                    pm.delete(node)
                except:
                    if not pm.objExists(node):
                        if DEBUG:
                            print node + "does not exists"
                    else:
                        if DEBUG:
                            print node + "is deletable"

            if DEBUG:
                if not pm.objExists(shadingEngineName):
                    print("Status: Success")
                else:
                    print("Status: Failed")
                print("_" * 10)

        # Refresh the scene api
        self.refresh()

    def __sort_XML_MA_Files__(self, shaderFolder):
        """Return XMl and Ma File"""
        shaderFolder = libFile.safePath(shaderFolder)
        shaderXmlInfoPath = None
        shaderMAFilePath = None
        # Sort out the file
        for shaderFile in libFile.listfiles(shaderFolder):
            if shaderFile.endswith(".xml"):
                shaderXmlInfoPath = shaderFolder + shaderFile
            elif shaderFile.endswith(".ma"):
                shaderMAFilePath = shaderFolder + shaderFile
        return shaderXmlInfoPath, shaderMAFilePath

    def import_all_shading_and_connection_info(self, shaderOnly=0, shapePrefix="", *args, **kwargs):
        global DEBUG
        """Import Shading Group for a given directory"""
        # Read All Subfolders in data directory
        for shaderFolder in libFile.listfolders(self.dataFolder):
            if not (shaderFolder == "Textures"):
                pm.select(cl=1)
                self.import_shading_and_connection_info(
                    libFile.join(self.dataFolder, shaderFolder),
                    shaderOnly, shapePrefix
                )
                if DEBUG:
                    print("Shader Processed:" + shaderFolder)

        pm.select(cl=1)

    def import_shading_and_connection_info(self, shaderFolder, shaderOnly=False, shapePrefix=""):
        global DEBUG
        """Import Shading Group from individual folder"""
        shaderFolder = libFile.safePath(shaderFolder)
        shaderXmlInfo, shaderMAFile = self.__sort_XML_MA_Files__(shaderFolder)
        # Import the shaders
        self.import_shading_network(shaderMAFile)
        # Rebuild the connections
        self.import_connection_info(
            shaderXmlInfo, connectShapes=(not shaderOnly), shapePrefix=shapePrefix)
        if DEBUG:
            print("Shader Info was loaded from " + shaderFolder)
            # Dekete any sets created by the above step
        try:
            pm.delete(pm.ls("set*", type="objectSet"))
        except:
            pass

    def import_connection_info(self, shaderXmlInfo, connectShapes=1, shapePrefix="", setRenderInfo=True):
        """Import shape and connection info"""
        # Reading the Shader Connection Info
        shaderInfo = libXml.ConvertXmlToDict(shaderXmlInfo)['shapeShaderConnections']
        if pm.objExists(shaderInfo['shadingEngine']):
            # Connect the shapes to shading group
            if connectShapes:
                self.assign_shader(shaderInfo['shadingEngine'], shaderInfo["mesh"], shapePrefix)
            # Rebuild the network connections
            if shaderInfo.has_key('shadingReconnection'):
                self.__process_xml_dict_info__(
                    shaderInfo['shadingReconnection'], shapePrefix)

                #            shaderReconInfo=shaderInfo['shadingReconnection']
                #            if isinstance(shaderReconInfo, dict):
                #                rebuild_connection(shaderReconInfo,shapePrefix)
                #            elif isinstance(shaderReconInfo, list):
                #                for reconnection in shaderReconInfo:
                #                    rebuild_connection(reconnection,shapePrefix)
            # Set the Render Info for the mesh
            if setRenderInfo:
                if shaderInfo.has_key('renderingInfo'):
                    self.__set_rendering_info__(
                        shaderInfo['renderingInfo'], shapePrefix)
        else:
            print(shaderInfo['shadingEngine'] + " does not exists in scene. No connection info was imported")

    def import_shading_network(self, shaderMAFile):
        """Import Individual Shading Network from a maya file"""
        if not shaderMAFile.endswith(".ma"):
            print("not a valid Maya File with a .ma extension")
            return
        if not libFile.exists(shaderMAFile):
            print("File Does not exists")
            return
        # mel.eval('file -import -type "mayaAscii" -ra true -rpr "importedShader" -options "v=0"  -pr -loadReferenceDepth "all" "%s";'%shaderMAFile)
        libFile.importFile(shaderMAFile)
        # for node in pm.ls("importedShader*"):
        #     node.rename(str(node).replace("importedShader_",""))

    def __process_xml_dict_info__(self, func, info, *arg):
        """pass a dictionary argument to method based on the fact if 'info' item a dictionary item or a list.
         If it is a list then iterate the through the list
         and then pass each individual item individually throught the method"""
        if isinstance(info, dict):
            func(info, *arg)
        elif isinstance(info, list):
            for item in info:
                func(item, *arg)

    def __set_rendering_info__(self, renderingInfo, shapePrefix=""):
        self.__process_xml_dict_info__(
            self.__set_dag_stats__, renderingInfo['dagsInfo'], shapePrefix)
        self.__process_xml_dict_info__(
            self.__set_shape_stats__, renderingInfo['shapesInfo'], shapePrefix)

    def __set_dag_stats__(self, dagInfo, shapePrefix, swapDagDict={}):
        """

        :param dagInfo:
        :param shapePrefix:
        :param swapDagDict:
        """
        thisDag = dagInfo['dag']
        if swapDagDict.has_key(thisDag):
            thisDag = swapDagDict[thisDag]
        if pm.objExists(shapePrefix + thisDag):
            thisDag = pm.PyNode(shapePrefix + thisDag)
            if dagInfo.has_key('renderingInfo'):
                for attr in dagInfo['renderingInfo']:
                    if pm.attributeQuery(attr['attribute'], node=thisDag, ex=1):
                        try:
                            attribute = pm.PyNode(
                                thisDag + "." + attr['attribute'])
                            if attribute.isSettable():
                                attribute.set(float(attr['value']))
                            else:
                                if DEBUG:
                                    print(attribute + " is unsettable. Unable to import settings")
                        except:
                            # Do not error if the attrubyre dies dies exist
                            pass
        else:
            print(thisDag + ":Does Not Exists In This Scene")

    def __set_shape_stats__(self, shapeInfo, shapePrefix, swapShapeDict={}):
        thisShape = shapeInfo['shape']
        if swapShapeDict.has_key(thisShape):
            thisShape = swapShapeDict[thisShape]

        targetShape = shapePrefix + thisShape

        targetShape = self._check_target_shape_existence_(targetShape)

        if targetShape:
            thisShape = pm.PyNode(targetShape)
            if shapeInfo.has_key('renderingInfo'):
                for attr in shapeInfo['renderingInfo']:
                    try:
                        if thisShape.hasAttr(attr['attribute']):
                            attribute = pm.PyNode(
                                thisShape + "." + attr['attribute'])
                            if attribute.isSettable():
                                if attr['type'] == 'string':
                                    if attr['value'] != 'None':
                                        attribute.set(attr['value'])
                                else:
                                    attribute.set(float(attr['value']))
                            else:
                                if DEBUG:
                                    print(attribute + " is unsettable. Unable to import settings")
                    except:
                        print "This attribute %s does not exists on this shape: %s" % (attr['attribute'], thisShape)

    def rebuild_connection(self, conDict, shapePrefix=""):
        """Rebuild Individual Connections"""
        # Check to see attributes exists or not.
        targetAttr = None
        sourceAttr = None
        try:
            sourceAttr = pm.PyNode(shapePrefix + conDict['sourceNode'])
            targetAttr = pm.PyNode(conDict['targetNode'])
        except:
            print("One of the following connection attributes are missing")
            print(conDict['sourceNode'])
            print(conDict['targetNode'])

        if targetAttr and sourceAttr:
            sourceAttr >> targetAttr

    def _check_target_shape_existence_(self, targetShape):
        origName = targetShape
        # Maya 2015 bug. When you create a skinCluster it makes a topEyes_meshShapeDeformed and applies the changes
        # to that. It should be applying to the topEyes_meshShape. We need to capture this in our script
        if not pm.objExists(targetShape):
            # Check to make sure shape deformed version exists
            deformedShape = targetShape + "Deformed"
            # Check to see a 'Deformed shape version exists'
            if not pm.objExists(deformedShape):
                # Set to none
                targetShape = None
            else:
                pymelLogger.info("Remapping %s to %s" % (origName, deformedShape))
                # Set the deformed shape to target shape
                targetShape = deformedShape

        if targetShape is None:
            pymelLogger.warn(
                "%s:Does Not Exists In This Scene. Even the 'ShapeDeformed' version does not exist either" % origName)

        # Return status
        return targetShape

    def check_nameSpace_in_shadingEngine(self, shadingEngine):
        """Prevent Export of nameSpaced shaders"""
        if ":" in str(shadingEngine):
            print(shadingEngine + ":Contains a nameSpace. Skipping")
            return False
        return True

    def export_all_shading_and_connection_info(self, shaderOnly=False, *args, **kwargs):
        """Export All Shaders in scene"""
        # _____Can extend the functionality of the script make the script export
        for shadingEngine in self.all_shaders_py:
            if "initial" not in str(shadingEngine) and shadingEngine not in self.sub_shaders_py:
                if shaderOnly:
                    self.export_shading_network(shadingEngine)
                else:
                    self.export_shading_and_connection_info(shadingEngine)

    def export_shading_and_connection_info(self, shadingEngine, rebuild=1):
        """
        Allows you to export individual shading Group.\nYou can also force export to individual shader but avoid putting it back on the original geometry, allowing you to remap shaders to different geometry
        @code
        sceneShaders=shaderManage(myPath)
        sceneShaders.export_shading_and_connection_info(shaderOnly=1)
        @endcode
        """

        if self.check_nameSpace_in_shadingEngine(shadingEngine):
            meshList = self.get_connected_shapes(shadingEngine)
            # Only Export if mesh are connected
            if not meshList:
                print(shadingEngine + ":Have no mesh attached to them. Skipping Shader Export")
                return
            # Export the shape shading Network info
            self.export_connections_info(shadingEngine)
            # Export the shading Network
            self.export_shading_network(shadingEngine, rebuild)
            if not meshList:
                print(shadingEngine + ":Exported. Contains Empty Mesh Info")
            else:
                print(shadingEngine + ":Exported")
            # Dekete any sets created by the above step
            try:
                pm.delete(pm.ls("set*", type="objectSet"))
            except:
                pass

    def export_shading_network(self, shadingEngine, rebuild=1, exportTextures=True, *args, **kwargs):
        """Export the individual Shading Group without the dags or shapes"""
        global DEBUG
        if self.check_nameSpace_in_shadingEngine(shadingEngine):
            # Constuct Directory if missing
            shaderDir = self._build_shader_folder_(shadingEngine)
            # Disconnect the mesh from the shading group set
            meshList = self.get_connected_shapes(shadingEngine)
            if meshList:
                self.remove_shape_from_shadingGroup(meshList)
            # Disconnect any dag from network
            shadingReConList = self.disconnect_mesh_from_network(shadingEngine)
            textureRevertInfo = None
            # Export Textures
            if exportTextures:
                textureRevertInfo = self.export_textures(
                    shadingEngine, shaderDir)

            # Export the shading network
            mayaExportFile = "%s%s.ma" % (shaderDir, self._build_export_file_name_(shadingEngine))
            pm.select(cl=1)
            pm.select(shadingEngine, ne=1, r=1)
            libFile.ma_export(mayaExportFile)
            if rebuild:
                # Rebuild the connection and reapply the shading to the shapes
                for reconnection in shadingReConList:
                    pm.PyNode(reconnection["sourceNode"]) >> pm.PyNode(
                        reconnection["targetNode"])
                # Reassign Mesh to the original Shader
                if meshList:
                    self.assign_shader(shadingEngine, meshList)
                if textureRevertInfo:
                    for revert in textureRevertInfo:
                        revert['fileNode'].fileTextureName.set(
                            revert['oldPath'])
            if DEBUG:
                print("Shader Maya File Written To - " + mayaExportFile)

    def _build_shader_folder_(self, shadingEngine):
        return libFile.folder_check(libFile.join(self.dataFolder, shadingEngine))

    def _build_export_file_name_(self, shadingEngine):
        """
        Export the file name based on the shading engine
        @param shadingEngine PyNode or String
        @return  material PyNode
        """
        return shadingEngine

    def export_textures(self, shadingEngine, shaderFolder):
        global DEBUG
        fileTextureSwap = []

        dataPath = None

        if self.textureFolder:
            dataPath = self.textureFolder
        else:
            dataPath = str(shaderFolder)
        for node in self.get_network_nodes(shadingEngine, returnEngine=0):
            # Iterate through all the textures
            if node.nodeType() in ['file', 'mentalrayTexture']:
                rebuildInfo = self._export_texture_and_change_path_name_(node, dataPath)
                if len(rebuildInfo):
                    fileTextureSwap.append(rebuildInfo)
                    # Get the path
                    # currentImageFile = node.fileTextureName.get()
                    # if currentImageFile:
                    #     # Get file folder information
                    #     imageName, dummy, ext = libFile.get_file_folder_extension(
                    #         currentImageFile)
                    #     # global GRID_TEXTURES
                    #     imageFileName = imageName + "." + ext
                    #     # if imageFileName not in GRID_TEXTURES:
                    #     # New image location
                    #     newImagePath = libFile.folder_check(
                    #         dataPath) + imageFileName
                    #     # make sure the file does not exists
                    #     if not libFile.exists(newImagePath):
                    #         libFile.copyfile(currentImageFile, newImagePath)
                    #     # Set the new path information
                    #     node.fileTextureName.set(newImagePath)
                    #     fileTextureSwap.append(
                    #         {'fileNode': node, 'oldPath': currentImageFile})
                    # else:
                    #     if DEBUG:
                    #         print(node + " Has No File Path")
        return fileTextureSwap

    def _export_texture_and_change_path_name_(self, textureNode, targetFolder):

        rebuildInfo = {}
        try:
            currentImageFile = textureNode.fileTextureName.get()
            if currentImageFile:
                imageName, sourceFolder, ext = libFile.get_file_folder_extension(
                    currentImageFile)
                # Rebuild the file name
                imageFileName = "%s.%s" % (imageName, ext)

                # New image location
                newImagePath = "%s%s" % (
                    libFile.folder_check(targetFolder),
                    imageFileName)

                # Are we exporting UDIMs
                if "<UDIM>" in imageName:
                    searchPattern = imageFileName.replace("<UDIM>", "****")
                    # Convert for relative path to absolute path for the source images folder
                    if sourceFolder.lower().startswith("sourceimages"):
                        sourceFolder = libFile.join(cmds.workspace(q=True, rd=True), sourceFolder)

                    udimFiles = libFile.search_pattern_in_folder(searchPattern, sourceFolder)
                    # New Udim files
                    for udimFile in udimFiles:
                        currentUdimPath = libFile.join(sourceFolder, udimFile)
                        newUdimPath = "%s%s" % (
                            libFile.folder_check(targetFolder),
                            udimFile)
                        if not libFile.exists(newUdimPath):
                            libFile.copyfile(currentUdimPath, newUdimPath)
                else:
                    # make sure the file does not exists
                    if not libFile.exists(newImagePath):
                        libFile.copyfile(currentImageFile, newImagePath)
                # Set the new path information
                textureNode.fileTextureName.set(newImagePath)
                rebuildInfo = {'fileNode': textureNode, 'oldPath': currentImageFile}
            else:
                pymelLogger.warning("%s has not file path" % textureNode)
        except:
            raise Exception("Problem with exporting data from %s" % textureNode)
        return rebuildInfo

    def copy_all_texture_files(self, newPath):
        """Copy the textures path from the existing location to the target location
        newPath = string
        """
        newPath = str(newPath)
        for shader in self.used_shaders:
            self.export_textures(shader, newPath)

    def export_connections_info(self, shadingEngine):
        global DEBUG
        """Export shape shader connection"""
        if self.check_nameSpace_in_shadingEngine(shadingEngine):
            # Get Connected Mesh Info
            meshList = self.get_connected_shapes(shadingEngine)
            # Get Rendering Info
            renderingInfo = self.get_rendering_info(meshList)
            # Dsconnect Mesh from shading engine
            if meshList:
                self.remove_shape_from_shadingGroup(meshList)
            # path for Directory
            shaderDir = self._build_shader_folder_(shadingEngine)
            infoFile = "%s%s.xml" % (shaderDir, self._build_export_file_name_(shadingEngine))
            # Get Shading Network Info
            shadingReConList = self.disconnect_mesh_from_network(
                shadingEngine, False)
            shaderInfo = {'shapeShaderConnections': {'mesh': meshList, 'shadingEngine': shadingEngine,
                                                     'shadingReconnection': shadingReConList,
                                                     'renderingInfo': renderingInfo}}
            libXml.write_xml(infoFile, shaderInfo)
            # Reapply shading group
            if meshList:
                self.assign_shader(shadingEngine, meshList)
            if DEBUG:
                print("Shape Shader Connection Info Xml File Written To - " + infoFile)
            return infoFile

    def disconnect_mesh_from_network(self, shadingEngine, breakConnection=True):
        """Disconnect any Shape or Dag from a shading network so that geo/dags are not imported. Breakconnection=0 would put it in a query mode"""
        shadingNetworkNodes = self.get_network_nodes(shadingEngine)
        # Disconnect any DAG or mesh from the shading network and collect that
        # information for rebuilding purposes
        shadingReConList = []
        for node in shadingNetworkNodes:
            # list all attributes in node
            for attr in pm.listAttr(node, c=1, m=1):
                nodeAttr = node.name() + "." + attr
                for connection in pm.listConnections(nodeAttr, d=0):
                    if connection.type() in ["mesh", "transform", "nurbsSurface"]:
                        # Build the mel command to reconnect the connections
                        for disconnectTarget in cmds.listConnections(nodeAttr, d=0, p=1):
                            if connection.name() in disconnectTarget:
                                shadingReConList.append(
                                    {'sourceNode': disconnectTarget, 'targetNode': nodeAttr})
                                if breakConnection:
                                    pm.disconnectAttr(disconnectTarget, nodeAttr)
        return shadingReConList

    def remove_shape_from_shadingGroup(self, meshList):
        """Disconnect geometery from shading group and the network"""
        if meshList:
            self.assign_shader("initialShadingGroup", meshList)
            pm.refresh()

    def prune_dag_shape(self, nodeList):
        """Remove Dag or shape info. Will also remove duplicates"""
        possibleNodes = []
        disQualifiedNodes = []
        for node in nodeList:
            if node.type() not in ["polyNormal", "mentalrayGlobals", "mesh", "transform", "nurbsSurface", 'mesh',
                                   'time', 'expression', 'cluster', 'groupParts', 'groupId', 'clusterHandle', 'lattice',
                                   'baseLattice', 'tweak', 'resolution']:
                possibleNodes.append(node)
            else:
                # Remove Any Intereconnected node still in the valid nodes such
                # deformer history
                try:
                    disQualifiedNodes = disQualifiedNodes + pm.listHistory(node)[1:]
                except:
                    # Node does not have history
                    pass
        validNodes = []
        for validNode in possibleNodes:
            if validNode not in disQualifiedNodes:
                validNodes.append(validNode)
        return list(set(validNodes))

    def safe_select_meshList(self, meshList, shapePrefix=""):
        """Select mesh from meshList. Check to see if a mesh exists, if not print warning message, instead of  erroring out"""
        pm.select(cl=1)
        for mesh in meshList:
            targetMesh = shapePrefix + str(mesh)
            targetMesh = self._check_target_shape_existence_(targetMesh)
            if targetMesh:
                pm.select(targetMesh, add=1)

    def has_shader(self, dag):
        """Return List of Shader Assigned to the Dag"""
        pass

    def refresh(self):
        """Reload the shader API to take into account any changes in the scene"""
        self.__init_internal__()

    def load_alias_info(self, aliasType):
        """

        :rtype : return a dict from the xmlPath
        """
        aliasType = "%sAliases" % aliasType
        return self._load_info_(eval("self.%sPath" % aliasType))[aliasType]

    def load_attr_info(self, attrType):
        attrType = "%sAttr" % attrType
        return self._load_info_(eval("self.%sPath" % attrType))[attrType]

    def _load_info_(self, path):
        if not libFile.exists(path):
            raise Exception("Path does not exist:%s" % path)
        return libXml.ConvertXmlToDict(path)["Data"]

    def _get_data_folder_(self):
        if not self._data_folder_:
            self._data_folder_ = "H:/TEMP/"
        return self._data_folder_

    def _set_data_folder_(self, folder):
        # Get the root folder from the user
        self._data_folder_ = libFile.folder_check(folder)

    def _get_namespace_(self):
        return self._namespace_

    def _set_namespace_(self, namespace):
        if not namespace.endswith(":"):
            cmds.error('Namespace must ends with ":"')
        self._namespace_ = namespace

    dataFolder = property(_get_data_folder_, _set_data_folder_)

    namespace = property(_get_namespace_, _set_namespace_)

    @property
    def all_shaders_py(self):
        """
        Return a list of shaders that are used in the scene
        """
        if self._all_shaders_ is None:
            self._all_shaders_ = []
            # Save a pymel list for dynamic update
            for engine in pm.ls(type="shadingEngine"):
                if engine.name() not in ["initialShadingGroup", "initialParticleSE", "lambert1", "particleCloud1"]:
                    self._all_shaders_.append(engine)

        return self._all_shaders_

    @property
    def all_shaders(self):
        return libUtilities.stringList(self.all_shaders_py)

    @property
    def used_shaders_py(self):
        """
        Return the pymel version of used shaders
        """
        if self._used_shaders_ is None:
            self._used_shaders_ = []
            # Make sure all shader information is loaded
            # if self._all_shaders_ is None:
            #     self.all_shaders
            # Save a pymel list for dynamic update
            for shader in self.all_shaders_py:
                try:
                    if self.get_connected_shapes(shader):
                        self._used_shaders_.append(shader)
                except:
                    pymelLogger.warning("Unable to Process: %s" % shader)
                    self._error_shaders_.append(shader)
        return self._used_shaders_

    @property
    def used_shaders(self):
        """
        Return a list of used shaders that are used in the scene
        """
        return libUtilities.stringList(self.used_shaders_py)

    @property
    def sub_shaders_py(self):
        """
        Return the pymel version of used shaders
        """
        sub_shaders = []
        for key in self.detailed_sub_shaders_py.keys():
            sub_shaders += self.detailed_sub_shaders_py[key]
        return sub_shaders

    @property
    def sub_shaders(self):
        """
        Return a list of sub shaders that are used in the scene
        """
        return libUtilities.stringList(self.sub_shaders_py)

    @property
    def detailed_sub_shaders_py(self):
        """
        Return the pymel version of detailes shaders
        """
        # Build the sub shader info
        if self._sub_shaders_ is None:
            self._sub_shaders_ = {}
            # Iterate through all  shaders
            for shader in self.all_shaders_py:
                # Remove all used shadering engine
                if shader not in self.used_shaders_py:
                    # Get the main material connected to this shading engine
                    mainMaterial = self.get_material(shader)
                    if mainMaterial:
                        # Iterate through all future connected nodes for the material
                        for connection in pm.listHistory(mainMaterial, allConnections=True, future=True):
                            # Append the shader engine to list
                            if connection in self.used_shaders_py:
                                if self._sub_shaders_.has_key(connection):
                                    self._sub_shaders_[connection].append(shader)
                                else:
                                    self._sub_shaders_[connection] = [shader]

        return self._sub_shaders_

    @property
    def detailed_sub_shaders(self):
        """
        These shaders have no geometery associated but are still connected to another shading network.
        """
        # Return a string based sub shaders

        return libUtilities.stringDict(self.detailed_sub_shaders_py)

    @property
    def error_shaders_py(self):
        """
        These shaders have issues. They may been assigned to faces rather than to
        """

        self.used_shaders
        return self._error_shaders_

    @property
    def error_shaders(self):
        return libUtilities.stringList(self.error_shaders_py)

    @property
    def attrAliasesPath(self):
        return libFile.join(self._preset_path_, "attrAliases.xml")

    @property
    def nodeAliasesPath(self):
        return libFile.join(self._preset_path_, "nodeAliases.xml")

    @property
    def shapeAttrPath(self):
        return libFile.join(self._preset_path_, "shapeAttr.xml")

    @property
    def dagAttrPath(self):
        return libFile.join(self._preset_path_, "dagAttr.xml")


# noinspection PyPep8Naming
class MDSshaderAPI(ShaderAPI):
    def __init__(self):
        super(MDSshaderAPI, self).__init__()
        #self._preset_path_ = r"\\file04\Repository\maya\2015\mds\scripts\PKD_tools"
        self._preset_path_ = r"\\productions\boad\Pipeline\tools\maya\shaderManager"
        # Track nodes where which the first primary node has been renamed
        self._artist_named_shader_node_dict_ = {}
        self.assetNameSpace = ""

    def update_all_shader(self):
        for shaderFolder in libFile.listfolders(self.dataFolder):
            self.update_shader(shaderFolder)

    def update_shader(self, shaderFolder):
        if not pm.objExists(shaderFolder):
            pm.warning("This material does not exists in this scene anymore")
        else:
            # Get the shading engine
            shadingEngine = self.get_shadingEngine(shaderFolder)
            # Delete the existing shader
            self.safe_delete_shading_network(shadingEngine)
            # Delete the existing vrag dags
            self.delete_vray_dag_info()
            # import the data
            self.import_shading_and_connection_info(shaderFolder, shapePrefix=self.namespace)
            self._import_vray_dag_info_()

    def delete_vrag_dag_info(self):
        vrayDagTypes = self._get_vrag_dag_types_()
        vrayDags = pm.ls(type=vrayDagTypes)
        if vrayDags:
            pm.delete(vrayDags)

    def import_all_shading_and_connection_info(self, *args, **kwargs):
        """Import the vray nodes in the file also"""
        super(MDSshaderAPI, self).import_all_shading_and_connection_info(shapePrefix=self.namespace, *args, **kwargs)
        self._import_vray_dag_info_()

    def reapply_all_shaders(self):
        """Reapply shader to another names space object"""
        for material in libFile.listfolders(self.dataFolder):
            if not (material == 'Textures'):
                materialFolder = libFile.join(self.dataFolder, material)
                shaderXmlInfo = self.__sort_XML_MA_Files__(materialFolder)[0]
                self.import_connection_info(shaderXmlInfo, shapePrefix=self.namespace)
                libUtilities.pyLog.info("Reapplied %s to %s" % (material, self.namespace))

    def add_shader_nameSpace(self):
        "Put the shaders under name space"
        for material in libFile.listfolders(self.dataFolder):
            if not (material == 'Textures'):
                shader = self.get_shadingEngine(pm.PyNode(material))
                connectNodes = self.get_network_nodes(shader)
                libUtilities.add_nodes_to_namespace(self.assetNameSpace, connectNodes)
                libUtilities.pyLog.info("Adding namespace %s to %s" % (self.assetNameSpace, material))

    def get_model_info(self):
        return self._load_info_(self.modelInfoPath)

    def _import_vray_dag_info_(self):
        if libFile.exists(self.vrayDagMAPath):
            # Import the maya vray dag file
            libFile.importFile(self.vrayDagMAPath)
            # Read the vray xml relationship
            vrayRebuildInfo = libXml.ConvertXmlToDict(self.vrayDagInfoPath)["Data"]
            self._rebuild_vrag_dag_data_(vrayRebuildInfo)

    def export_all_shading_and_connection_info(self, *args, **kwargs):
        """Export the vray nodes in the file also"""
        # Export the vray nodes to be exported
        try:
            self._export_used_model_info_()
        except:
            libUtilities.pyLog.warning("No Published Model found in this scene")
        super(MDSshaderAPI, self).export_all_shading_and_connection_info(*args, **kwargs)
        self._export_vray_dag_info_()

    def _export_used_model_info_(self):
        dataDict = {"Data": str(pm.listReferences()[0].path)}
        libXml.write_xml(self.modelInfoPath, dataDict)

    def _get_vrag_dag_types_(self):
        return libXml.list_persist(self._load_info_(self.vrayDagPaths)["vrayDags"])

    def _export_vray_dag_info_(self):
        """Export the vray dag data such as displacement"""
        vrayDagTypes = self._get_vrag_dag_types_()
        # Go through all the dags type
        if vrayDagTypes:
            vrayDagRebuildInfo = {}
            for vrayDayType in vrayDagTypes:
                # List the dag types
                vrayDags = pm.ls(type=vrayDayType)
                if vrayDags:
                    for dag in vrayDags:
                        # Details
                        # Get the objects list
                        objects = cmds.sets(str(dag), q=1)
                        # Get the name of dag
                        vrayDagRebuildInfo[dag.name()] = objects
                        # Unlink the info
                        dag.removeMembers(objects)
            # Select all the vray dags
            pm.select(cl=1)
            for vragDag in vrayDagRebuildInfo.keys():
                pm.select(vragDag, add=1, ne=1)
            # Export the vray data
            if pm.selected():
                libFile.ma_export(self.vrayDagMAPath)
                dataDict = {"Data": vrayDagRebuildInfo}
                libXml.write_xml(self.vrayDagInfoPath, dataDict)
                global DEBUG
                if DEBUG:
                    print("Vray Dag Info Written to: %s" % self.vrayDagInfoPath)
                    print("Vray Dag Ma Written to: %s" % self.vrayDagMAPath)
            # Rebuild the data
            self._rebuild_vrag_dag_data_(vrayDagRebuildInfo)

    def _rebuild_vrag_dag_data_(self, vrayDagDict):
        for vragDag in vrayDagDict.keys():
            # check if the dag exits
            objects = libXml.list_persist(vrayDagDict[vragDag])
            vragDag = pm.PyNode(vragDag)
            for item in objects:
                item = self.namespace + item
                if pm.objExists(item):
                    vragDag.addMembers([item])
                else:
                    print("%s could not be added to %s as it does exists in this scene" % (item, vragDag))

    def _build_shader_folder_(self, shadingEngine):
        return libFile.folder_check(libFile.join(self.dataFolder, self.get_material(shadingEngine)))

    def _build_export_file_name_(self, shadingEngine):
        """
        Export the file name based on the primary material
        @param shadingEngine PyNode or String
        @return  material PyNode
        """
        return self.get_material(shadingEngine)

    def _rename_duplicate_nodes_in_sg_(self, shadingEngine):
        """Rename duplicates Nodes in Shading Group"""
        networkNodes = self.get_network_nodes(shadingEngine, returnEngine=True)
        self._rename_duplicate_nodes_(networkNodes)

    def _return_materials_(self, shader_list):
        """Internal method to return a list of py materials from py shader list"""
        materials = []
        for sg in shader_list:
            material = self.get_material(sg)
            if material is not None:
                materials.append(material)
        return materials

    def get_base_name(self, shadingEngine, *args):
        """@brief We have three ways of deteriming a base name
        @detailed We first see if the artist has renamed the node. It not we try to see if the artist has
        named the first connected material. Otherwise we get the name from the primary material
        """
        # set the base name to none

        baseName = ""

        # Set the node name
        node = args[0]

        mainMaterial = self.get_material(shadingEngine)

        # Check to see it is not the main ShadingEngine
        if node != shadingEngine:
            # Check to see if the artist has named the node
            if self._is_node_has_default_name_(node):
                # Use that as base name
                baseName = self._format_name_((node))
            else:
                if self.detailed_sub_materials_py.has_key(mainMaterial):
                    subMaterials = self.detailed_sub_materials_py[mainMaterial]
                    allFutureHistory = pm.listHistory(node, f=1, ac=1)
                    # Is subshader in the future connections
                    if any(x in allFutureHistory for x in subMaterials):
                        # Put in a try to break nested loop
                        try:
                            # List all future connections
                            for connection in allFutureHistory:
                                # Try to find the first future subMaterial connection
                                if connection in subMaterials:
                                    # Which subMaterial is it?
                                    for subMaterial in subMaterials:
                                        # subMaterial found
                                        if subMaterial == connection:
                                            # Check to see if subMaterial has been renamed
                                            if self._is_node_has_default_name_(subMaterial):
                                                # Set the base name based on subMaterial
                                                baseName = self._format_name_(subMaterial)
                                                # Break from loop
                                                raise StopIteration()
                        except StopIteration:
                            pass

        # Has the base name been found?

        if not baseName:
            # Get the base name from the base material
            baseName = self._format_name_(mainMaterial)
        return baseName

    def _is_node_has_default_name_(self, node):
        """Check to see if the artist has bother to rename the node. Otherwise we will write for them"""
        return node.type() not in node.name()

    def set_datafolder_from_publish_path(self, path):
        """Build and set the data folder in the publish data"""
        # Decontruct the path
        fileName, folder, ext = libFile.get_file_folder_extension(path)
        # Set the shader path
        shaderPath = libFile.join(folder, "Shaders")
        # Get the shader part
        shaderVersionPath = libFile.join(shaderPath, fileName)
        # Set the shader version
        self.dataFolder = libFile.folder_check(shaderVersionPath)

    def check_nameSpace_in_shadingEngine(self, shadingEngine):
        """Prevent Export of nameSpaced material"""
        material = self.get_material(shadingEngine)
        if ":" in str(material):
            print(material + ":Contains a nameSpace. Skipping")
            return False
        return True

    @property
    def all_materials_py(self):
        """Print out a list of py all materials"""
        all_materials = self._return_materials_(self.all_shaders_py)
        return all_materials

    @property
    def all_materials(self):
        """Print out a list of all materials"""
        return libUtilities.stringList(self.all_materials_py)

    @property
    def used_materials_py(self):
        """Print out a list of py used materials"""
        used_materials = self._return_materials_(self.used_shaders_py)
        return used_materials

    @property
    def used_materials(self):
        """Print out a list of used materials"""
        return libUtilities.stringList(self.used_materials_py)

    @property
    def sub_materials_py(self):
        """Print out a list of py sub materials"""
        sub_materials = self._return_materials_(self.sub_shaders_py)
        return sub_materials

    @property
    def detailed_sub_materials_py(self):
        """Return a detailed dictonary of materials"""
        shaderDict = {}

        for subShaderKey in self.detailed_sub_shaders_py.keys():
            shaderDict[self.get_material(subShaderKey)] = []
            for subShader in self.detailed_sub_shaders_py[subShaderKey]:
                shaderDict[self.get_material(subShaderKey)].append(self.get_material(subShader))

        return shaderDict

    @property
    def detailed_sub_materials(self):
        """String version of the detailed_sub_material property"""
        return libUtilities.stringDict(self.detailed_sub_materials_py)

    @property
    def sub_materials(self):
        """Print out a list of py sub materials"""
        return libUtilities.stringList(self.sub_materials_py)

    @property
    def error_materials_py(self):
        """Return a list of pymel error materials"""
        error_materials = self._return_materials_(self.error_shaders_py)
        return error_materials

    @property
    def error_materials(self):
        """Return a list of pymel error"""
        return libUtilities.stringList(self.error_materials_py)

    @property
    def vrayDagPaths(self):
        """the vray dags that need to be exported"""
        return libFile.join(self._preset_path_, "vrayDags.xml")

    @property
    def vrayDagInfoPath(self):
        """Vray Output file"""
        return libFile.join(self.dataFolder, "vrayDagInfo.xml")

    @property
    def vrayDagMAPath(self):
        """Vray Output file"""
        return libFile.join(self.dataFolder, "vrayDags.ma")

    @property
    def modelInfoPath(self):
        """Save out the model file that is used to build the object"""
        return libFile.join(self.dataFolder, "modelInfo.xml")


class MDSFurShaderAPI(MDSshaderAPI):
    def copy_all_texture_files(self):
        """Copy the textures path from the existing location to the target location
        # newPath = string
        # """
        rebuild_info = []
        for texture in pm.ls(type="file"):
            rebuildData = self._export_texture_and_change_path_name_(texture, self.dataFolder)
            if len(rebuildData):
                rebuild_info.append(rebuildData)
        return rebuild_info


if __name__ == '__main__':
    a = MDSFurShaderAPI()
    print a.error_materials
