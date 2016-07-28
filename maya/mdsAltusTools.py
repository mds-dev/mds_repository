import maya.cmds as cmds
import random
import os
import os.path
import maya.mel as mel

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
#                                                  Define Functions
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
#                                                Setup AOV Layers Func
# ---------------------------------------------------------------------------------------------------------------------


# define AOV setup button
global setupAltusAOV
def setupAltusAOV(cauEnabled,albEnabled,visEnabled,posEnabled,norEnabled,envNames):
    # Check if VRay is loaded & load it if not

    vray_flag = cmds.pluginInfo( 'vrayformaya.mll', query=True,loaded=True )
    if (vray_flag):
        print "VRay is loaded"
    else:
        print "Attempting to load VRay"
        cmds.loadPlugin('Mvrayformaya.mll')

    # Check that VRay is set as the renderer

    cur_renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    if (cur_renderer != 'vray'):
        cmds.confirmDialog( title='AOV Setup Error', message='Current renderer is not VRay, Please set it to VRay and try aagain', button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
        exit()

    cmds.confirmDialog( 
    title='Altus Elements v1.1', 
    icon="information", 
    message='Will now create renderElements. \nThis will not create duplicates if elements already exists.\nThis will set current renderlayer to master', 
    button=['OK'] )


    # Make sure we are using master layer
    cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")	

    if envNames == 'MDS names':
        names = ["baseDiffuse", "utilityWorldPos", "utilityCameraNorm", "baseMatteShadow", "baseCaustics"]
    else:
        names = ["vrayRE_Diffuse", "vrayRE_Extra_Tex_WorldPos", "vrayRE_Extra_Tex_CameraNorm", "vrayRE_Matte_shadow", "vrayRE_Caustics"]
    # -----------------------------------------------------------------------
    # Feedback if already run

    if cmds.objExists(names[0]):
        print("vrayRE_Diffuse Render element already exists")
        
    if cmds.objExists(names[1]):
        print("vrayRE_Extra_Tex_WorldPos Render element already exists")
        
    if cmds.objExists(names[2]):
        print("vrayRE_Extra_Tex_CameraNorm Render element already exists")

    if cmds.objExists(names[3]):
        print("vrayRE_Matte_shadow Render element already exists")
        
    if cmds.objExists(names[4]):
        print("vrayRE_Caustics Render element already exists")
        
    
    # ------------------------------------------------------------------------- 
    # Setup for AOVs
    # Create V-ray render elements

    
    types = ["diffuseChannel", "ExtraTexElement", "ExtraTexElement", "matteShadowChannel", "causticsChannel"] 
    toggle = [albEnabled, posEnabled, norEnabled, visEnabled, cauEnabled]

    # CreateAOV
    for i in range(len(names)): 
        if cmds.objExists( names[i]) == False:
            var = mel.eval("vrayAddRenderElement "+types[i])
            
            if envNames == 'default names':
                if names[i] == names[1]:
                    cmds.rename(var, names[i])
                    cmds.setAttr(names[1]+'.vray_name_extratex','worldPos',type="string")
                elif names[i] == names[2]:
                    cmds.rename(var, names[i])
                    cmds.setAttr(names[2]+'.vray_name_extratex','cameraNorm',type="string")
            elif envNames == 'MDS names':
                cmds.rename(var, names[i])
                if names[i] == names[1]:
                    cmds.setAttr(names[1]+'.vray_name_extratex','worldPos',type="string")
                elif names[i] == names[2]:
                    cmds.setAttr(names[2]+'.vray_name_extratex','cameraNorm',type="string")

                
            cmds.setAttr ( names[i] + '.enabled', toggle[i]);
            

    # Setup worldPos render element
    if cmds.objExists("AltusWPP") != 1: 
        cmds.shadingNode('samplerInfo', asShader=True, n='AltusWPP')
        cmds.connectAttr('AltusWPP.pointWorldX',names[1]+'.vray_texture_extratex.vray_texture_extratexR')
        cmds.connectAttr('AltusWPP.pointWorldY',names[1]+'.vray_texture_extratex.vray_texture_extratexG')
        cmds.connectAttr('AltusWPP.pointWorldZ',names[1]+'.vray_texture_extratex.vray_texture_extratexB')
        
    # Setup cameraSpace surface normals render element 
    if cmds.objExists("AltusNorms") != 1:  
        cmds.shadingNode('samplerInfo', asShader=True, n='AltusNorms')
        cmds.connectAttr('AltusNorms.normalCameraX',names[2]+'.vray_texture_extratex.vray_texture_extratexG')
        cmds.connectAttr('AltusNorms.normalCameraY',names[2]+'.vray_texture_extratex.vray_texture_extratexR')
        cmds.connectAttr('AltusNorms.normalCameraZ',names[2]+'.vray_texture_extratex.vray_texture_extratexB')

#------------------------------------------------------------------------
# Setup Altus layers
#------------------------------------------------------------------------
global  setupAltusLayers
def setupAltusLayers(qALTUSsetseedTOGL,qALTUSstaticTOGL,qALTUSpadTOGL,qALTUSseedb1):

    # List renderLayers
    renderLayers = cmds.ls(exactType="renderLayer")
    userLayers = []
    renamedLayers = []
    
    # Create a list of only user created layers
    print "DEBUG - Processing layers"
    
    for layer in renderLayers: 
        if layer != "defaultRenderLayer" and not 'utility' in layer and not 'NOSEED' in layer:
            userLayers.append(layer)
        elif 'NOSEED' in layer:
            cmds.rename(layer, layer.replace('NOSEED',''))
    
    # Rename user layers and add to new list
    for layer in userLayers:
        cmds.select(layer)	
        cmds.rename(layer + "_b0")
        renamedLayers.append(layer + "_b0")			
    		
    # Duplicate renderlayer
    for dlayer in renamedLayers:
        cmds.select(dlayer)
        cmds.duplicate(ic=True) 
    
    # Create layer overrides for b1 layer
    renderLayers = cmds.ls(type="renderLayer")
    altusLayers = filter(lambda x: "_b1" in x, renderLayers)
    	
    	
    # for layer in altusLayers:
    #     seed = 1
    #     cmds.editRenderLayerGlobals(currentRenderLayer = layer)
    #     cmds.editRenderLayerAdjustment("vraySettings.dmcs_randomSeed")
    #     cmds.setAttr("vraySettings.dmcs_randomSeed", seed)
    #     cmds.setAttr("vraySettings.dmcstd", 0)
        
    if qALTUSseedb1 != 'rand':
        seed = int(qALTUSseedb1)
    elif qALTUSseedb1 == 'rand':
        seed = random.randint(1000,9999)
    else:
        seed = 1000

    for layer in altusLayers:
        if qALTUSsetseedTOGL:
            cmds.editRenderLayerGlobals(currentRenderLayer = layer)
            cmds.editRenderLayerAdjustment("vraySettings.dmcs_randomSeed")
            cmds.setAttr("vraySettings.dmcs_randomSeed", seed)
            
    if qALTUSstaticTOGL:
        cmds.setAttr("vraySettings.dmcstd", 0)

    if qALTUSpadTOGL:
        cmds.setAttr("vraySettings.fileNamePadding", 4)


        userLayers = filter(lambda x: "_b0" in x, renderLayers)
    
    # Remove b0 from name
            
    renderLayers = cmds.ls(type="renderLayer")
    userLayers = filter(lambda x: "_b0" in x, renderLayers)

    for layer in userLayers:
        cmds.select(layer)          
        originalLayer = layer.split("_b0")
        cmds.rename(originalLayer[0])   

#------------------------------------------------------------------------
# remove Altus layers
#------------------------------------------------------------------------
global removeAltusLayers
def removeAltusLayers():
    
    #reapture some variables 
    renderLayers = cmds.ls(type="renderLayer")
    altusLayers = filter(lambda x: "_b1" in x, renderLayers)
    userLayers = filter(lambda x: "_b0" in x, renderLayers)
    
    # Check to see if there are indeed any Altus layers
    for layer in altusLayers:
        cmds.select(layer)
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")	
        cmds.delete(layer)
    		
    for layer in userLayers:
        cmds.select(layer)		    
        originalLayer = layer.split("_b0")
        cmds.rename(originalLayer[0])    	
 
 
#------------------------------------------------------------------------
#           Conditionally execute the appropriate action
#------------------------------------------------------------------------
global AltusLayersButton
def AltusLayersButton(qALTUSsetseedTOGL,qALTUSstaticTOGL,qALTUSpadTOGL,qALTUSseedb1):
    renderLayers = cmds.ls(type="renderLayer")
    altusLayers = filter(lambda x: "_b1" in x, renderLayers)

    if cmds.objExists('vraySetting'):
      print "Yes"
    else:
      print("Warning: no surface exists.")
     
    if altusLayers:
        cmds.confirmDialog( 
        title='Altus Layers v1.0', 
        icon="information", 
        message='Altus Layer configuration will now be removed', 
        button=['OK'] )
           
        removeAltusLayers()
        
    elif cmds.objExists('vraySettings'):
        cmds.confirmDialog( 
        title='Altus Layers v1.0', 
        icon="information", 
        message='Altus Layer configuration will now be applied', 
        button=['OK'] )
        qALTUSsetseedTOGLpass = qALTUSsetseedTOGL
        setupAltusLayers(qALTUSsetseedTOGLpass,qALTUSstaticTOGL,qALTUSpadTOGL,qALTUSseedb1)   
           
              
    else:
        cmds.confirmDialog( 
        title='Altus Layers v1.0', 
        icon="critical", 
        message='VRAY NOT FOUND!\nPlease ensure Vray is loaded and has been accessed via the Maya Render Globals', 
        button=['OK'] )
        

# ---------------------------------------------------------------------------------------------------------------------
#                                            Start Altus Command Func
# ---------------------------------------------------------------------------------------------------------------------
global altusStart
def altusStart( Pathb0, Pathb1, AltusOutput, chosenRender, chosenMethod, animationToggle, frameRadius, frameStart, frameEnd, filterRadius, kc1, kc2, kc3, TogglesVal, runToggleVal, printToggleVal, pauseToggleVal):
   
    outputFile = os.path.basename(AltusOutput)
    outputDir = os.path.split(AltusOutput)[0]
    
    output_noEXT = os.path.splitext(outputFile)[0]
    extension = os.path.splitext(outputFile)[1]

    if not os.path.exists(outputDir+'/'):
        os.makedirs(outputDir+'/')

    file = open(outputDir+'/'+output_noEXT+".cfg", "w")
    file.write("################################################################################################\n")
    file.write("#                                     ALTUS CONFIG FILE \n")
    file.write("# "+AltusOutput+'\n')
    file.write("#                           Output from Maya Altus Tools Interface\n")
    file.write("################################################################################################\n\n\n")

    # Chosen Renderer
    if chosenRender == 'VRay':
        rendererFlag = 'Renderer=vray'
    elif chosenRender == 'Arnold':
        rendererFlag = 'Renderer=arnold'
    else:
        rendererFlag = 'Renderer='+chosenRender
    file.write(rendererFlag+'\n')
        
    # Chosen Method
    if chosenMethod == 'CPU':
        ALTUSlocation = os.environ["altus_PATH"] + 'altus.exe'
        ALTUSlocation = ALTUSlocation.replace('\\','/')
        gpuFlag = ''
        
    elif chosenMethod == 'OpenCL':
        ALTUSlocation = os.environ["altus_PATH"] + 'altus.exe'
        ALTUSlocation = ALTUSlocation.replace('\\','/')
        gpuFlag = 'gpu=\n'
        
    elif chosenMethod == 'CPU (cuda.exe)':
        ALTUSlocation = os.environ["altus_CUDA_PATH"] + 'cuda.exe'
        ALTUSlocation = ALTUSlocation.replace('\\','/')
        gpuFlag = ''
        
    elif chosenMethod == 'CUDA':
        ALTUSlocation = os.environ["altus_CUDA_PATH"] + 'cuda.exe'
        ALTUSlocation = ALTUSlocation.replace('\\','/')
        gpuFlag = 'gpu=\n'
        
    file.write(gpuFlag+'\n')

    # Filter Settings
    # Filter Radius
    filterRadius = 'radius='+str(filterRadius)+'\n\n'
    file.write(filterRadius)
    # KC flags
    kc1Flag = 'kc_1=' + str(kc1)+'\n'
    kc2Flag = 'kc_2=' + str(kc2)+'\n'
    kc3Flag = 'kc_3=' + str(kc3)+'\n\n'
    file.write(kc1Flag)
    file.write(kc2Flag)
    file.write(kc3Flag)
    
    # Animation Toggle
    if animationToggle:
        #Frame Settings
        frameRadiusFlag = 'Frame_Radius=' + str(frameRadius)
        frameStartFlag = 'StartFrame=' + frameStart
        frameEndFlag = 'EndFrame=' + frameEnd
        
        file.write(frameRadiusFlag+'\n')
        file.write(frameStartFlag+'\n')
        file.write(frameEndFlag+'\n\n')
        
        
        # i = 0
        # for path in Pathb0:
        #     Pathb0[i] = path[:-9]+'.exr'
        #     print Pathb0[i]
        #     i = i+1
           
        # i = 0 
        # for path in Pathb1:
        #     Pathb1[i] = path[:-9]+'.exr'
        #     print Pathb1[i]
        #     i = i+1
    
    file.write('img='+output_noEXT+'\n')
    file.write('out='+outputDir+'\n\n\n')

    
    
    
    elementFlags=['rgb=','alb=','pos=','nrm=','vis=','cau=',]
    
    i = 0
    while i < 6:
 
        if TogglesVal[i] and os.path.exists(Pathb0[i]) and os.path.exists(Pathb1[i]):
            file.write(elementFlags[i]+Pathb0[i]+'\n')
            file.write(elementFlags[i]+Pathb1[i]+'\n')
            if TogglesVal[i] and not os.path.exists(Pathb0[i]):
                print 'Could not find ' + elementFlags[i] + Pathb0[i]
            if TogglesVal[i] and not os.path.exists(Pathb1[i]):
                print 'Could not find ' + elementFlags[i] + Pathb1[i]
        i = i+1


    file.write('\n\n')
    file.write('''################################################################################################
#               Use the # symbol to comment out any setting you do not want
#                              The default Renderer is vray 
#        The renderer flag is not critical currently as it is only for shadow consideration
################################################################################################
''')
    file.close()

    # Setup Command
    cmdFilePart = ALTUSlocation + ' --config ' + outputDir + '/' + output_noEXT+".cfg"
    if pauseToggleVal:
        CommandString = cmdFilePart
    else:
        CommandString = 'start ' + cmdFilePart
    # Settings Flags

    # Final command combine
    if printToggleVal:
        print 'Output Command: ' + CommandString.replace('start ','') + ' & pause'

    # Start Altus
    if runToggleVal:
        if pauseToggleVal:
            os.system(CommandString+' & pause');
        else:
            os.system(CommandString);
    
    
    
########################################################################################################################
########################################################################################################################
#                                                       File Finders
########################################################################################################################
########################################################################################################################

global RGBB0_setRadio
def RGBB0_setRadio(RGBB0_radioCollection):
    selectedRadio = cmds.radioCollection(RGBB0_radioCollection, query=True, select=True)
    selectedRadioLabel = cmds.radioButton(selectedRadio, query=True, l=True )
    selectedRadioLabel = selectedRadioLabel.replace('{CURRENT} ','')
    if selectedRadioLabel != '{EMPTY}':
        cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], edit = True, tx=selectedRadioLabel)
    cmds.deleteUI(ALTUS_rgbb0_SEARCH_UIID)
    Altus_findFiles_check()
    
global RGBB1_setRadio
def RGBB1_setRadio(RGBB1_radioCollection):
    selectedRadio = cmds.radioCollection(RGBB1_radioCollection, query=True, select=True)
    selectedRadioLabel = cmds.radioButton(selectedRadio, query=True, l=True )
    selectedRadioLabel = selectedRadioLabel.replace('{CURRENT} ','')
    if selectedRadioLabel != '{EMPTY}':
        cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], edit = True, tx=selectedRadioLabel)
    cmds.deleteUI(ALTUS_rgbb1_SEARCH_UIID)
    Altus_findFiles_check()
    
##############################################################
#                      RGB B0 Finder
##############################################################
global altus_rgbb0Finder
def altus_rgbb0Finder(rgbPathb0,rgbPathb1,useVersions):
    
    global ALTUS_rgbb0_SEARCH_UIID
    ALTUS_rgbb0_SEARCH_UIID = 'ALTUS_FILE_SEARCH_UIID_2'
    if cmds.window(ALTUS_rgbb0_SEARCH_UIID, exists=True):
        cmds.deleteUI(ALTUS_rgbb0_SEARCH_UIID)
    # ------------------------------------------------------
    # Make window
    cmds.window(ALTUS_rgbb0_SEARCH_UIID, width=1000, title = 'RGB B0 File Finder')
    cmds.columnLayout( adjustableColumn=True )


    cmds.separator(h = 10, style = "double")
    cmds.text( label='RGB B0 not defined or doesn\'t exist, searching...' )



    # Searching for RGB b0
    global RGBB0_radioCollection
    RGBB0_radioCollection = cmds.radioCollection(gl=True)
    

    if rgbPathb0 == '':
        rb_rgbPathb0_default = cmds.radioButton( l='{EMPTY}' )
    else:
        rb_rgbPathb0_default = cmds.radioButton( l='{CURRENT} '+rgbPathb0 )
        
    cmds.radioCollection(RGBB0_radioCollection, edit=True, select=rb_rgbPathb0_default )

    if rgbPathb1 != "":
        rgbPathb1_split = os.path.split(rgbPathb1)
        Pathb1_fold_index = rgbPathb1_split[0].rfind('/')
        Pathb1_fold = rgbPathb1_split[0][Pathb1_fold_index:]
        possible_b0folder = rgbPathb1_split[0][:Pathb1_fold_index]+Pathb1_fold.replace('b1','b0')
        
        
        
        # If split into /<prefix><b0_or_b1><suffix>/ folders
        # With b0/b1 name difference only
        if 'b1' in (rgbPathb1_split[1]):
            possible_b0rgb = possible_b0folder+'/'+rgbPathb1_split[1].replace('b1','b0')

            if (os.path.exists(possible_b0rgb)) and (possible_b0rgb != rgbPathb1):
                rb_rgbPathb0_renderLayerFileFolderb1name = cmds.radioButton( l=possible_b0rgb )
                cmds.radioCollection(RGBB0_radioCollection, edit=True, select=rb_rgbPathb0_renderLayerFileFolderb1name )
                
        # If split into /<prefix><b0_or_b1><suffix>/ folders
        # With same same as b1
        possible_b0rgb = possible_b0folder + '/' + rgbPathb1_split[1]
        if os.path.exists(possible_b0rgb) and (possible_b0rgb != rgbPathb1):
            rb_rgbPathb0_renderLayerFolderb1name = cmds.radioButton( l=possible_b0rgb )
            cmds.radioCollection(RGBB0_radioCollection, edit=True, select=rb_rgbPathb0_renderLayerFolderb1name )
    
    
        # Same folder as b1, b0 name difference
        possible_b0rgb = rgbPathb1_split[0]+'/'+rgbPathb1_split[1].replace('b1','b0')
        if (os.path.exists(possible_b0rgb)) and (possible_b0rgb != rgbPathb1):
            rb_rgbPathb0_renderLayerFileb1name = cmds.radioButton( l=possible_b0rgb )
            cmds.radioCollection(RGBB0_radioCollection, edit=True, select=rb_rgbPathb0_renderLayerFileb1name )

    ### MDS Shotgun Search ###
    if useVersions:
        i = 1
        iMax = 100
        alphabetList = list(map(chr, range(97, 123)))
        alphabetList.append('')
        while i < iMax:
            
            img_currentVer = '%03d' % i
            layersDir = cmds.workspace(q=True, fn=True) + '/images/v'+img_currentVer+'/'
            
            if os.path.exists(layersDir):
                shot = cmds.workspace(q=True, fn=True)
                shotInd = shot.rfind('kittenSequence')
                shot = shot[shotInd+15:]
                shotInd = shot.rfind('/Light')
                shot = shot[:shotInd]

                layers = next(os.walk(layersDir))[1]
                for layer in layers:
                    if not 'utility' in layer and 'b0' in layer:
                        possible_b0rgb = layersDir+layer+'/'+shot+'_Light_'+layer+'_v'+img_currentVer+'.0991'+'.exr'
                        if os.path.exists(possible_b0rgb):
                            lastRadioButton = cmds.radioButton( l=possible_b0rgb )
                            if not os.path.exists(rgbPathb0):
                                cmds.radioCollection(RGBB0_radioCollection, edit=True, select=lastRadioButton )
                                
                        possible_b0rgb = layersDir+layer+'/rgba/'+shot+'_Light_'+layer+'_v'+img_currentVer+'.0991'+'.exr'
                        if os.path.exists(possible_b0rgb):
                            lastRadioButton = cmds.radioButton( l=possible_b0rgb )
                            if not os.path.exists(rgbPathb0):
                                cmds.radioCollection(RGBB0_radioCollection, edit=True, select=lastRadioButton )
                                
                        
                        possible_b0rgb = layersDir+layer+'/rgba/'+shot+'_Light_'+layer+'_v'+img_currentVer+'.rgba.0991'+'.exr'
                        if os.path.exists(possible_b0rgb):
                            lastRadioButton = cmds.radioButton( l=possible_b0rgb )
                            if not os.path.exists(rgbPathb0):
                                cmds.radioCollection(RGBB0_radioCollection, edit=True, select=lastRadioButton )
                        
                i=i+1
            else:
                i=iMax
    
                
        
    
    
    cmds.button(label='Set Selected',bgc = [.4,.5,.5], command='RGBB0_setRadio(RGBB0_radioCollection)')
    cmds.button(label='Manually Find and set the path',bgc = [.4,.5,.5], command='''cmds.textField( altusCMDUIID_dict["rgbPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))
if (cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True) != ''):
    cmds.deleteUI(ALTUS_rgbb0_SEARCH_UIID)
    Altus_findFiles_check()
''')
    cmds.showWindow()
##############################################################
#                      RGB B1 Finder
##############################################################
global altus_rgbb1Finder
def altus_rgbb1Finder(rgbPathb0,rgbPathb1):
    
    global ALTUS_rgbb1_SEARCH_UIID
    ALTUS_rgbb1_SEARCH_UIID = 'ALTUS_b1_FILE_SEARCH_UIID_1'
    if cmds.window(ALTUS_rgbb1_SEARCH_UIID, exists=True):
        cmds.deleteUI(ALTUS_rgbb1_SEARCH_UIID)
    # ------------------------------------------------------
    # Make window
    cmds.window(ALTUS_rgbb1_SEARCH_UIID, width=1000, title = 'RGB B1 File Finder')
    cmds.columnLayout( adjustableColumn=True )


    cmds.separator(h = 10, style = "double")
    cmds.text( label='RGB B1 not defined or doesn\'t exist searching...' )



    # Searching for RGB b1
    global RGBB1_radioCollection
    RGBB1_radioCollection = cmds.radioCollection(gl=True)
    

    if rgbPathb1 == '':
        rb_rgbPathb1_default = cmds.radioButton( l='{EMPTY}' )
    else:
        rb_rgbPathb1_default = cmds.radioButton( l=('{CURRENT} '+rgbPathb1) )
        
    cmds.radioCollection(RGBB1_radioCollection, edit=True, select=rb_rgbPathb1_default )



    if rgbPathb0 != "":
        
        rgbPathb0_split = os.path.split(rgbPathb0)
        Pathb0_fold_index = rgbPathb0_split[0].rfind('/')
        Pathb0_fold = rgbPathb0_split[0][Pathb0_fold_index:]
        possible_b1folder = rgbPathb0_split[0][:Pathb0_fold_index]+Pathb0_fold.replace('b0','b1')
        
        # If split into /<prefix><b0_or_b1><suffix>/ folders
        # With b0/b1 name difference only
        if 'b0' in (rgbPathb0_split[1]):
            possible_b1rgb = possible_b1folder+'/'+rgbPathb0_split[1].replace('b0','b1')
            if (os.path.exists(possible_b1rgb)) and (possible_b1rgb != rgbPathb0):
                rb_rgbPathb1_renderLayerFileFolderb1name = cmds.radioButton( l=possible_b1rgb )
                cmds.radioCollection(RGBB1_radioCollection, edit=True, select=rb_rgbPathb1_renderLayerFileFolderb1name )
        
        
        # If split into /<prefix><b0_or_b1><suffix>/ folders
        # With same same as b1
        possible_b1rgb = possible_b1folder + '/' + rgbPathb0_split[1]
        if os.path.exists(possible_b1rgb) and (possible_b1rgb != rgbPathb0):
            rb_rgbPathb1_renderLayerFolderb1name = cmds.radioButton( l=possible_b1rgb )
            cmds.radioCollection(RGBB1_radioCollection, edit=True, select=rb_rgbPathb1_renderLayerFolderb1name )
    
        # Same folder as b1, b0 name difference
        possible_b1rgb = rgbPathb0_split[0]+'/'+rgbPathb0_split[1].replace('b0','b1')
        if (os.path.exists(possible_b1rgb)) and (possible_b1rgb != rgbPathb0):
            rb_rgbPathb1_renderLayerFileb1name = cmds.radioButton( l=rgbPathb0_split[0]+'/'+rgbPathb0_split[1].replace('b0','b1') )
            cmds.radioCollection(RGBB1_radioCollection, edit=True, select=rb_rgbPathb1_renderLayerFileb1name )
            
        ### If using folder split with RGBA split ###
        layersRoot = os.path.split(os.path.dirname(os.path.dirname(rgbPathb0)))
        b0folder = layersRoot[0]+'/'+layersRoot[1]
        possible_b1folder = layersRoot[0]+'/'+(layersRoot[1]).replace('b0','b1')
        if (os.path.exists(possible_b1folder)) and possible_b1folder != b0folder:
           
            possible_b1rgb = possible_b1folder+'/rgba/'+os.path.split(rgbPathb0)[1]
            if os.path.exists(possible_b1rgb) and possible_b1rgb != rgbPathb0:
                lastRadioButton = cmds.radioButton( l=possible_b1rgb )
                if not os.path.exists(rgbPathb1):
                    cmds.radioCollection(RGBB1_radioCollection, edit=True, select=lastRadioButton )

            possible_b1rgb = possible_b1folder+'/rgba/'+(os.path.split(rgbPathb0)[1]).replace('b0','b1')
            if os.path.exists(possible_b1rgb) and possible_b1rgb != rgbPathb0:
                lastRadioButton = cmds.radioButton( l=possible_b1rgb )
                if not os.path.exists(rgbPathb1):
                    cmds.radioCollection(RGBB1_radioCollection, edit=True, select=lastRadioButton )





    cmds.button(label='Set Selected',bgc = [.4,.5,.5], command='RGBB1_setRadio(RGBB1_radioCollection)')
    cmds.button(label='Manually Find and set the path',bgc = [.4,.5,.5], command='''cmds.textField( altusCMDUIID_dict["rgbPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))
if (cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True) != ''):
    cmds.deleteUI(ALTUS_rgbb1_SEARCH_UIID)
    Altus_findFiles_check()
''')
    cmds.showWindow()

##############################################################
#                      Element Finder
##############################################################

global B_setField
def B_setField(radioCollection,textField):
    i = 0
    for collection in radioCollection:
        selectedRadio = cmds.radioCollection(collection, query=True, select=True)
        selectedRadioLabel = cmds.radioButton(selectedRadio, query=True, l=True )
        selectedRadioLabel = selectedRadioLabel.replace('{CURRENT} ','')
        selectedRadioLabel = selectedRadioLabel.replace('{CURRENT (Not Found)} ','')
        if (selectedRadioLabel != '{EMPTY}') and (selectedRadioLabel != 'Input:   '):
            cmds.textField( textField[i], edit = True, tx=selectedRadioLabel)
        elif (selectedRadioLabel == 'Input:   '):
            selectedRadioLabel = cmds.textField( manualElements_txtField[i], q = True, tx = True)
            cmds.textField( textField[i], edit = True, tx=selectedRadioLabel)

        i = i+1
    cmds.deleteUI(ALTUS_FileFinder_UIID)

#################################################################
global altus_fileFinder
def altus_fileFinder(rgbPathb0,rgbPathb1,albPathb0,albPathb1,posPathb0,posPathb1,norPathb0,norPathb1,visPathb0,visPathb1,cauPathb0,cauPathb1,elementTXTfields):
    global elementTXTfield
    elementTXTfield = elementTXTfields
    global ALTUS_FileFinder_UIID
    ALTUS_FileFinder_UIID = 'ALTUS_FileFinder_UIID7'
    if cmds.window(ALTUS_FileFinder_UIID, exists=True):
        cmds.deleteUI(ALTUS_FileFinder_UIID)
    # ------------------------------------------------------
    # Make window
    cmds.window(ALTUS_FileFinder_UIID, width=900, title = 'Altus EXR File Finder')
    masterLayout = cmds.columnLayout( adjustableColumn=True, width=(900), columnAlign=('center') )
    
    ##### RGB INPUTS #####
    cmds.separator(h = 10, style = "double")
    cmds.text( label='RGB', width = 800, fn='boldLabelFont', bgc =[.268,.268,.268] )
    cmds.columnLayout()
    

    #b0
    cmds.text( label='    B0: '+rgbPathb0, fn='boldLabelFont', rs=True )
    #b1
    cmds.text( label='    B1: '+rgbPathb1, fn='boldLabelFont', rs=True )

    
    cmds.setParent('..')
    
    cmds.separator(h = 10, style = "double")
    
    

    cmds.scrollLayout( horizontalScrollBarThickness=0, verticalScrollBarThickness=16, cr=True, h=640)
    cmds.columnLayout( adjustableColumn=True, width=(850), columnAlign=('center') )
    
    ##########################################################################################
    #####                               Search for elements                              #####
    ##########################################################################################
    
    elementList = ['diffuse','worldPos','cameraNorm','matteShadow','caustics']
    elementTitle = ['Diffuse','World Position','Camera Normals','Matte Shadow','Caustics']
    elementInput = [rgbPathb0,rgbPathb1,albPathb0,albPathb1,posPathb0,posPathb1,norPathb0,norPathb1,visPathb0,visPathb1,cauPathb0,cauPathb1]
    global radioCollections
    radioCollections = ['','','','','','','','','','']
    global radioInputButton
    radioInputButton = ['','','','','','','','','','']
    global manualElements_txtField
    manualElements_txtField = ['','','','','','','','','','']
    i = 0
    
    for element in elementList:
        
        # cmds.separator(h = 10, style = "double")
        cmds.text( label=elementTitle[i], fn='boldLabelFont', bgc =[.268,.268,.268])
         
        
        bVALUE = 0
        while bVALUE < 2:
            bSTRING = 'B'+str(bVALUE)
            currentElementB = elementInput[2+((i*2)+(bVALUE))]
            SETindex = i*2+bVALUE
            # Some common splicing for elements
            Pathb_split = os.path.split(elementInput[bVALUE])
            Pathb_folder_index = Pathb_split[0].rfind('/')
            Pathb_folder = Pathb_split[0][Pathb_folder_index:]
            
            b_extension = os.path.splitext(Pathb_split[1])[1]
            b_no_extension = os.path.splitext(Pathb_split[1])[0]

            b_padding_index = os.path.splitext(Pathb_split[1])[0].rfind('.')
            b_padding = b_no_extension[b_padding_index+1:]
            b_no_extension_no_padding = b_no_extension[:b_padding_index]
            
            cmds.columnLayout()
            cmds.text( label=(bSTRING) , fn='boldLabelFont', bgc =[.268,.268,.268])
            cmds.setParent('..')
            
            
            radioCollections[SETindex] = cmds.radioCollection(gl=True)

            
            # Checking the status of the current field text
            # if not os.path.exists(currentElementB) and currentElementB == '':   
            lastRadioButton = cmds.radioButton( l='{EMPTY}' )
            cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
            
            
            
            if not os.path.exists(currentElementB) and currentElementB != '':   
                lastRadioButton = cmds.radioButton( l='{CURRENT (Not Found)} '+currentElementB )
                cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
            if os.path.exists(currentElementB):
                lastRadioButton = cmds.radioButton( l='{CURRENT} '+currentElementB )
                cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
                
            # Auto Searches  
            # If all else fails use .b0 to .b0.diffuse replace method
            possible_replace = currentElementB.replace('.'+bSTRING,'.'+bSTRING+'.'+element)
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
                    
            # Auto Searches  
            # If all else fails use .b0 to .b0.diffuse replace method
            possible_replace = currentElementB.replace('.'+bSTRING,'.'+bSTRING+'.'+element)
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )

            #                                            .exr <--- Prefixing before that extension; .diffuse
            # Extension prefix method <anyPrefix>.diffuse.exr
            possible_replace = Pathb_split[0] + '/' + b_no_extension + '.' + element + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )

            # If you like to use folders (Replace Method)
            possible_replace = Pathb_split[0] + '/{}/'.format(element) + (b_no_extension+b_extension).replace('.'+bSTRING,'.'+bSTRING+'.'+element)
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
            # If you like to use folders (Extension Prefix method)
            possible_replace = Pathb_split[0] + '/{}/'.format(element) + b_no_extension + '.' + element + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
                    
            # If you like to use folders (Extension Prefix method) + RGBA folder
            possible_replace = os.path.dirname(Pathb_split[0]) +'/'+element+'/'+ b_no_extension + '.' + element + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )  
            
            # Frame Padding
            
            #                                   . <--- Looking for that . to split and prefix .diffuse
            # Padding Method <anyPrefix>.diffuse.<padding>.exr
            possible_replace = Pathb_split[0] + '/' + b_no_extension_no_padding + '.{}.'.format(element) + b_padding + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
                    
            # If you like to use folders (Padding Method)
            possible_replace = Pathb_split[0] + '/{}/'.format(element) + b_no_extension_no_padding + '.{}.'.format(element) + b_padding + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
             
            # In RGBA folder with .rgba element tag     
            # Looks for ../diffuse/<prefix>.rgba<suffix> to replace with <prefix>.diffuse<suffix> 
            possible_replace = os.path.dirname(Pathb_split[0]) +'/'+element+'/'+ Pathb_split[1].replace('.rgba',('.'+element))
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
            
            possible_replace = os.path.dirname(Pathb_split[0]) +'/'+element+'/'+b_no_extension_no_padding + '.{}.'.format(element) + b_padding + b_extension
            if (os.path.exists(possible_replace)) and (possible_replace != currentElementB):
                lastRadioButton = cmds.radioButton( l=possible_replace )
                if not os.path.exists(currentElementB):
                    cmds.radioCollection(radioCollections[SETindex], edit=True, select=lastRadioButton )
            
            
            
            cmds.columnLayout(adjustableColumn=True, width = 800, columnAlign=('center')) 
            cmds.rowLayout( numberOfColumns=3, adjustableColumn=2,columnWidth3=(50, 600, 30), columnAlign=(2, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)], h=20)
            radioInputButton[SETindex] = cmds.radioButton( l='Input:   ' )
            manualElements_txtField
            manualElements_txtField[SETindex] = cmds.textField(bgc = [.25,.25,.25])
            cmds.button(label='...', command='''
cmds.textField(manualElements_txtField['''+str(SETindex)+'''], edit = True, tx= altus_getFile (default_file_path))
if cmds.textField(manualElements_txtField['''+str(SETindex)+'''], query=True, tx=True) != '':
    cmds.radioCollection(radioCollections['''+str(SETindex)+'''], edit=True, select=radioInputButton['''+str(SETindex)+'''])
''')
            cmds.setParent('..')

            bVALUE = bVALUE + 1
        cmds.text( label='')
        i = i + 1
        
    cmds.setParent(masterLayout)
    ############## SET BUTTON ###################
    cmds.button(label='Set Selected', command='B_setField(radioCollections,elementTXTfield)', width = 200, height = 40, bgc = [.4,.5,.5])
    cmds.showWindow()

#End of searching
global Altus_findFiles_check
def Altus_findFiles_check():
    if (os.path.exists(cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True))) and (os.path.exists(cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True))):
        rgbPathb0 = cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True)
        rgbPathb1 = cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True)
        albPathb0 = cmds.textField( altusCMDUIID_dict['albPathFieldb0'], q = True, tx = True)
        albPathb1 = cmds.textField( altusCMDUIID_dict['albPathFieldb1'], q = True, tx = True)
        posPathb0 = cmds.textField( altusCMDUIID_dict['posPathFieldb0'], q = True, tx = True)
        posPathb1 = cmds.textField( altusCMDUIID_dict['posPathFieldb1'], q = True, tx = True)
        norPathb0 = cmds.textField( altusCMDUIID_dict['norPathFieldb0'], q = True, tx = True)
        norPathb1 = cmds.textField( altusCMDUIID_dict['norPathFieldb1'], q = True, tx = True)
        visPathb0 = cmds.textField( altusCMDUIID_dict['visPathFieldb0'], q = True, tx = True)
        visPathb1 = cmds.textField( altusCMDUIID_dict['visPathFieldb1'], q = True, tx = True)
        cauPathb0 = cmds.textField( altusCMDUIID_dict['cauPathFieldb0'], q = True, tx = True)
        cauPathb1 = cmds.textField( altusCMDUIID_dict['cauPathFieldb1'], q = True, tx = True)
        elementTXTfields = [altusCMDUIID_dict['albPathFieldb0'],altusCMDUIID_dict['albPathFieldb1'],altusCMDUIID_dict['posPathFieldb0'],altusCMDUIID_dict['posPathFieldb1'],altusCMDUIID_dict['norPathFieldb0'],altusCMDUIID_dict['norPathFieldb1'],altusCMDUIID_dict['visPathFieldb0'],altusCMDUIID_dict['visPathFieldb1'],altusCMDUIID_dict['cauPathFieldb0'],altusCMDUIID_dict['cauPathFieldb1']]
        altus_fileFinder(rgbPathb0,rgbPathb1,albPathb0,albPathb1,posPathb0,posPathb1,norPathb0,norPathb1,visPathb0,visPathb1,cauPathb0,cauPathb1,elementTXTfields)
        
    elif not os.path.exists(cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True)):
        altus_rgbb0Finder(cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True),True)
    
    elif not os.path.exists(cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True)):
        altus_rgbb1Finder(cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True))

#######################################################################################################################
#                                                         UI FUNC
#######################################################################################################################




# ------------------------------------------------------
#                Define UI Function
# ------------------------------------------------------
# fileDialogs
global altus_getFile
def altus_getFile (startDir):
    filters = "Beauty EXR (*.exr);;All Files (*.*)"
    pathUniCode = cmds.fileDialog2(fileFilter=filters, dialogStyle=2, fm = 1, okc = 'Ok', dir = startDir)
    return pathUniCode[0]

global altus_getOutput
def altus_getOutput (startDir):
    filters = "Output EXR (*.exr)"
    pathUniCode = cmds.fileDialog2(fileFilter=filters, dialogStyle=2, fm = 0, okc = 'Ok', dir = startDir)
    return pathUniCode[0]
    
    
    
    
# ------------------------------------------------------
#                     Help Funcs
# ------------------------------------------------------

#renderer
global ALTUSrenderHELP
def ALTUSrenderHELP():
    ALTUSrenderHELPUIID = 'ALTUSrenderHELPID1'

    if cmds.window(ALTUSrenderHELPUIID, exists=True):
        cmds.deleteUI(ALTUSrenderHELPUIID)
        
    cmds.window(ALTUSrenderHELPUIID, width=380, title = 'Altus Choose Render Help')
    cmds.columnLayout(adj = True, width = 380, columnAlign=('left'))
    cmds.text( label='''The chosen renderer is specific only to the shadow type from that renderer. 
A choice of V-Ray means that your shadows are inverted.
A choice of Arnold means that your shadows are not inverted.''' )
    cmds.showWindow()
    
#method
global ALTUSmethodHELP
def ALTUSmethodHELP():
    ALTUSmethodHELPUIID = 'ALTUSmethodHELPID2'

    if cmds.window(ALTUSmethodHELPUIID, exists=True):
        cmds.deleteUI(ALTUSmethodHELPUIID)
        
    cmds.window(ALTUSmethodHELPUIID, width=480, title = 'Altus Choose Method Help')
    cmds.columnLayout(adj = True, width = 480, columnAlign=('left'))
    cmds.text( label='''Use CPU or GPU with a choice of openCL or CUDA(beta)
CUDA beta version of altus needs to be installed and enviroment path set''' )
    cmds.showWindow()
    
#filter
global ALTUSfilterHELP
def ALTUSfilterHELP():
    ALTUSfilterHELPUIID = 'ALTUSfilterHELPID8'

    if cmds.window(ALTUSfilterHELPUIID, exists=True):
        cmds.deleteUI(ALTUSfilterHELPUIID)
        
    cmds.window(ALTUSfilterHELPUIID, width=280, title = 'Altus Filter Size Help')
    cmds.columnLayout(adj = True, width = 280, columnAlign=('left'))
    cmds.text( label='Filter radius. Default value is 10.\nGood to experiment with, especially with fine geo.' )
    cmds.showWindow()
    
#frame radius
global ALTUSradiusHELP
def ALTUSradiusHELP():
    ALTUSradiusHELPUIID = 'ALTUSradiusHELPID6'

    if cmds.window(ALTUSradiusHELPUIID, exists=True):
        cmds.deleteUI(ALTUSradiusHELPUIID)
        
    cmds.window(ALTUSradiusHELPUIID, width=380, title = 'Altus Filter Size Help')
    cmds.columnLayout(adj = True, width = 380, columnAlign=('left'))
    cmds.text( label='''Frame Radius - Default is 1
Uses surronding frames asneighbour compensation in temporal filtering.
Value 0: Current frame only
Value 1: Current, Current-1, Current+1
Value 2: Current, Current-2, current-1, Current+1, Current +2''' )
    cmds.showWindow()

#kc
global ALTUSkcHELP
def ALTUSkcHELP():
    ALTUSkcHELPUIID = 'ALTUSkcHELPID2'

    if cmds.window(ALTUSkcHELPUIID, exists=True):
        cmds.deleteUI(ALTUSkcHELPUIID)
        
    cmds.window(ALTUSkcHELPUIID, width=360, title = 'Altus KC Help')
    cmds.columnLayout(adj = True, width = 360, columnAlign=('left'))
    cmds.text( label='''The KC values control the sensitivity of the filter
kc_1 controls the sensitivity of the first pass. Default is 0.45
kc_2 controls the sensitivity of the second pass. Default is 0.45
kc_3 controls the sensitivity of the averaging pass. Default is 1e+010''' )
    cmds.showWindow()
    
#frame input range
global ALTUSrangeHELP
def ALTUSrangeHELP():
    ALTUSrangeHELPUIID = 'ALTUSrangeHELP3'

    if cmds.window(ALTUSrangeHELPUIID, exists=True):
        cmds.deleteUI(ALTUSrangeHELPUIID)
        
    cmds.window(ALTUSrangeHELPUIID, width=240, title = 'Altus KC Help')
    cmds.columnLayout(adj = True, width = 240, columnAlign=('left'))
    cmds.text( label='''Frame range; altus requires a padding of 4''' )
    cmds.showWindow()

global ALTUSinputHELP
def ALTUSinputHELP():
    ALTUSinputHELPUIID = 'ALTUSkcHELPID9'

    if cmds.window(ALTUSinputHELPUIID, exists=True):
        cmds.deleteUI(ALTUSinputHELPUIID)
        
    cmds.window(ALTUSinputHELPUIID, width=530, title = 'Altus File Input Help')
    cmds.columnLayout(adj = True, width = 530, columnAlign=('left'))
    cmds.text( label='''Use "Find Files" to quickly link your rendered files''' )
    cmds.showWindow()



#######################################################################################################################
#######################################################################################################################
#                                                         UI CODE
#######################################################################################################################
#######################################################################################################################

global ALTUSwinUI
def ALTUSwinUI():
    # Kill old window
    global altusCMDUIID
    altusCMDUIID = 'altusCMDUIID'

    if cmds.window(altusCMDUIID, exists=True):
        cmds.deleteUI(altusCMDUIID)
        print "deleted old window"
        
    # if cmds.dockControl(ALTUS_DOCK, exists=True):
    #     cmds.deleteUI(ALTUS_DOCK)
    # ------------------------------------------------------
    # Make window
    cmds.window(altusCMDUIID, width=300, title = 'Altus Tools Interface')
    global altusCMDUIID_dict
    altusCMDUIID_dict = {}
    
    # Master Layout
    cmds.scrollLayout( horizontalScrollBarThickness=0, verticalScrollBarThickness=16, cr=True, width = 320)
    cmds.columnLayout(adj = True, width = 300, columnAlign=('left'))
    

    # ------------------------------------------------------
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    # cmds.separator(h = 10, style = "double")
    # cmds.text( label='--- Altus Submitter ---', h = 40, fn = 'boldLabelFont', bgc = [0,0,0])
    #######################################################################################################################
    cmds.setParent('..')

    global altusStartUIbutton
    def altusStartUIbutton():
        b0rgb = cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True)
        b1rgb = cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True)
        AltusOutput = cmds.textField( altusCMDUIID_dict['ALTUSOutputPath'], q = True, tx = True)
        chosenRender = ALTUSchosenRender
        chosenMethod = chosenALTUSMethod
        animationToggle = cmds.checkBox( altusCMDUIID_dict['ALTUSanimationToggle'], q = True, v = True )
        frameRadius = cmds.intField( altusCMDUIID_dict['ALTUSframeRadius'], q = True, value = True )
        frameStart = cmds.textField(altusCMDUIID_dict['ALTUSframeStart'], q = True, tx = True)
        frameEnd = cmds.textField(altusCMDUIID_dict['ALTUSframeEnd'], q = True, tx = True)
        filterRadius = cmds.intField( altusCMDUIID_dict['ALTUSfilterRadius'], q = True, value=True )
        kc1 = cmds.floatField( altusCMDUIID_dict['ALTUSkc1'], q = True, value = True )
        kc2 = cmds.floatField( altusCMDUIID_dict['ALTUSkc2'], q = True, value = True )
        kc3 = cmds.floatField( altusCMDUIID_dict['ALTUSkc3'], q = True, value = True )
        TogglesVal = [cmds.checkBox( altusCMDUIID_dict['rgbToggle'], q = True, v = True ), cmds.checkBox( altusCMDUIID_dict['albToggle'], q = True, v = True ), cmds.checkBox( altusCMDUIID_dict['posToggle'], q = True, v = True ), cmds.checkBox( altusCMDUIID_dict['norToggle'], q = True, v = True ), cmds.checkBox( altusCMDUIID_dict['visToggle'], q = True, v = True ),cmds.checkBox( altusCMDUIID_dict['cauToggle'], q = True, v = True )]
        Pathb0 = [cmds.textField( altusCMDUIID_dict['rgbPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['albPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['posPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['norPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['visPathFieldb0'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['cauPathFieldb0'], q = True, tx = True)]
        Pathb1 = [cmds.textField( altusCMDUIID_dict['rgbPathFieldb1'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['albPathFieldb1'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['posPathFieldb1'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['norPathFieldb1'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['visPathFieldb1'], q = True, tx = True),cmds.textField( altusCMDUIID_dict['cauPathFieldb1'], q = True, tx = True)]
        runToggleVal = cmds.checkBox( altusCMDUIID_dict['ALTUSrunToggle'], q = True, v = True )
        printToggleVal = cmds.checkBox( altusCMDUIID_dict['ALTUSprintToggle'], q = True, v = True )
        pauseToggleVal = cmds.checkBox( altusCMDUIID_dict['ALTUSpauseToggle'], q = True, v = True )

        altusStart( Pathb0, Pathb1, AltusOutput, chosenRender, chosenMethod, animationToggle, frameRadius, frameStart, frameEnd, filterRadius, kc1, kc2, kc3, TogglesVal, runToggleVal, printToggleVal, pauseToggleVal)

    cmds.button(label='> Start Altus <', h= 50, bgc = [.4,.5,.5],  command='altusStartUIbutton()')

    cmds.button(label='Find Files', h= 25, bgc = [.4,.5,.5],  command='Altus_findFiles_check()')

    cmds.button(label='Import Definitions', h= 25, bgc = [.4,.5,.5],  command='from mdsAltusTools import *')

    # ------------------------------------------------------
    # Choose Renderer
    cmds.rowLayout( adj = True, numberOfColumns=3, adjustableColumn=1)
    
    global ALTUSchosenRender
    ALTUSchosenRender = 'VRay'
    global chosenRenderFunc
    def chosenRenderFunc(item):
        global ALTUSchosenRender
        ALTUSchosenRender = item

    cmds.optionMenu( label='Renderer', changeCommand=chosenRenderFunc, height = 26 )
    cmds.menuItem( label='VRay' )
    cmds.menuItem( label='Arnold' )
    cmds.menuItem( label='RedShift' )
    cmds.menuItem( label='Corona' )
    cmds.menuItem( label='3Delight' )
    cmds.menuItem( label='Maxwell' )
    cmds.menuItem( label='Other' )

    cmds.button(label='?', command='ALTUSrenderHELP()')

    cmds.setParent('..')


    # Choose method; CPU, openCL or CUDA
    global chosenALTUSMethod
    chosenALTUSMethod = 'CPU'
    global ALTUS_chosenMethodFunc
    def ALTUS_chosenMethodFunc(item):
        global chosenALTUSMethod
        chosenALTUSMethod = item
        
    cmds.rowLayout( adj = True, numberOfColumns=5, adjustableColumn=1)


    cmds.optionMenu( label='Method  ', changeCommand=ALTUS_chosenMethodFunc, height = 26 )
    cmds.menuItem( label='CPU' )
    cmds.menuItem( label='OpenCL' )
    # cmds.menuItem( label='CPU (cuda.exe)' )
    cmds.menuItem( label='CUDA' )
    cmds.button(label='?', command='ALTUSmethodHELP()')


    cmds.setParent('..')

    # debug
    cmds.rowLayout( numberOfColumns=5)
    # cmds.text( label='Run Altus:' )
    altusCMDUIID_dict['ALTUSrunToggle'] = cmds.checkBox( label='Run Altus', v = 1 )
    # cmds.text( label=' Print CMD:' )
    altusCMDUIID_dict['ALTUSprintToggle'] = cmds.checkBox( label='Print CMD', v = 1 )
    # cmds.text( label=' Hold & Pause:' )
    altusCMDUIID_dict['ALTUSpauseToggle'] = cmds.checkBox( label='Wait', v = 0 )
    # cmds.text( label=' Debug:' )
    # ALTUSdebugToggle = cmds.checkBox( label='Debug', v = 0 )
    cmds.text( label=' ' )

    cmds.setParent('..')

    #######################################################################################################
    #######################################################################################################

    # File Inputs
    cmds.separator(h = 10, style = "double")
    # Title RGBA Beauty EXR
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    cmds.rowLayout( adj = True, numberOfColumns=2, adjustableColumn=1, columnAlign=(2, 'right'))
    cmds.text( label='Input: RGBA Beauty EXR', fn = 'boldLabelFont', bgc = [.2,.2,.2] )
    cmds.button(label='?', command='ALTUSinputHELP()')

    cmds.setParent('..')

    cmds.setParent('..')

    #######################################################################################################
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    # RGB
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    global default_file_path
    default_file_path = cmds.workspace(q=True, fn=True) + '/images' 
    cmds.text( label='Beauty b0: ')
    altusCMDUIID_dict['rgbPathFieldb0'] = cmds.textField(tx='')
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["rgbPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['rgbPathFieldb1'] = cmds.textField(tx='')
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["rgbPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')


    # alb
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='Diffuse b0: ')
    altusCMDUIID_dict['albPathFieldb0'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["albPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['albPathFieldb1'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["albPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')

    # pos
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnWidth3=(80, 250, 20), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='WorldPos b0: ')
    altusCMDUIID_dict['posPathFieldb0'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["posPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['posPathFieldb1'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["posPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')

    # nor_b0
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnWidth3=(80, 250, 20), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='CamNorm b0: ')
    altusCMDUIID_dict['norPathFieldb0'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["norPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['norPathFieldb1'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["norPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')

    # vis_b0
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnWidth3=(80, 250, 20), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='MatShad b0: ')
    altusCMDUIID_dict['visPathFieldb0'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["visPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['visPathFieldb1'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["visPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')


    # cau_b0
    cmds.rowLayout( numberOfColumns=7, adjustableColumn=2, columnWidth3=(80, 250, 20), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='Caustics b0: ')
    altusCMDUIID_dict['cauPathFieldb0'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["cauPathFieldb0"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.text( label=' b1: ' )
    altusCMDUIID_dict['cauPathFieldb1'] = cmds.textField()
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["cauPathFieldb1"], edit = True, tx= altus_getFile (default_file_path))')
    cmds.setParent('..')

    # Output: Line
    cmds.rowLayout( numberOfColumns=3, adjustableColumn=2, columnWidth3=(80, 226, 20), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    
    
    save_file_path = cmds.workspace(q=True, fn=True) + '/altus'+'/output.exr' 
    global default_output_file_path
    default_output_file_path = cmds.workspace(q=True, fn=True) + '/altus'
    cmds.text( label='Output: ' )
    altusCMDUIID_dict['ALTUSOutputPath'] = cmds.textField(tx = save_file_path)
    cmds.button(label='...', command='cmds.textField( altusCMDUIID_dict["ALTUSOutputPath"], edit = True, tx= altus_getOutput (default_output_file_path))')

    cmds.setParent('..')

    

    ####################################################################################################

    cmds.setParent('..')

    # -------------------------------------------------------
    cmds.separator(h = 10, style = "double")
    # Animation
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    cmds.rowLayout( numberOfColumns=3, columnWidth3=(118, 55, 20), columnAlign=(1, 'center'), bgc = [.2,.2,.2])
    cmds.text( label='' )
    cmds.text( label='Animation', fn = 'boldLabelFont' )
    altusCMDUIID_dict['ALTUSanimationToggle'] = cmds.checkBox( label='', v = 0 )
    cmds.setParent('..')
    cmds.setParent('..')

    # Frame Range
    cmds.rowLayout( numberOfColumns=3, adjustableColumn=1, columnWidth=[2,50], columnAlign=(1, 'left') )

    cmds.text( label='Frame Radius:' )
    altusCMDUIID_dict['ALTUSframeRadius'] = cmds.intField( minValue=0, value=1 )
    cmds.button(label='?', command='ALTUSradiusHELP()')

    cmds.setParent('..')

    # Frame inputs
    cmds.rowLayout( numberOfColumns=5, columnWidth5=(85,250,50, 50, 30), adjustableColumn=2, columnAlign=(5, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='Frame Start/End:' )
    cmds.text( label='' )

    startAnim = cmds.playbackOptions(query=True, ast=True)
    endAnim = cmds.playbackOptions(query=True, aet=True)

    altusCMDUIID_dict['ALTUSframeStart'] = cmds.textField(tx='%04d' % startAnim, width = 50 )
    altusCMDUIID_dict['ALTUSframeEnd'] = cmds.textField(tx='%04d' % endAnim, width = 50 )
    cmds.button(label='?', command='ALTUSrangeHELP()')

    cmds.setParent('..')

    # ------------------------------------------------------
    cmds.separator(h = 10, style = "double")
    # ------------------------------------------------------

    # Settings title
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    cmds.text( label='Settings', fn = 'boldLabelFont', bgc = [.2,.2,.2])
    cmds.setParent('..')


    # Settings
    # Filter Settings
    # Filter Radius
    cmds.rowLayout( numberOfColumns=3, adjustableColumn=1, columnWidth=[2,50], columnAlign=(1, 'left') )

    cmds.text( label='Filter Radius:' )
    altusCMDUIID_dict['ALTUSfilterRadius'] = cmds.intField( minValue=0, value=10 )
    cmds.button(label='?', command='ALTUSfilterHELP()')

    cmds.setParent('..')

    # KC
    cmds.text( label='kc_1            kc_2         kc_3' )
    cmds.rowLayout( adj = True, numberOfColumns=4, adjustableColumn=3, columnWidth4=[50,50,100,50])

    altusCMDUIID_dict['ALTUSkc1'] = cmds.floatField( tze = False, minValue=0, value=0.45 )
    altusCMDUIID_dict['ALTUSkc2'] = cmds.floatField( tze = False, minValue=0, value=0.45 )
    altusCMDUIID_dict['ALTUSkc3'] = cmds.floatField( tze = False, minValue=0, value=1000000 )
    cmds.button(label='?', command='ALTUSkcHELP()')

    cmds.setParent('..')

    # cmds.text( label='\n' )
    # AOVs to use
    cmds.text( label=' Enable:  ' )
    cmds.rowLayout( numberOfColumns=2, adjustableColumn=3 )
    cmds.columnLayout(adj = True, width = 150, columnAlign=('center'))
    altusCMDUIID_dict['rgbToggle'] = cmds.checkBox( label='RGB (Beauty Composite)', v = 1 )
    altusCMDUIID_dict['albToggle'] = cmds.checkBox( label='Diffuse', v = 1 )
    altusCMDUIID_dict['posToggle'] = cmds.checkBox( label='WorldSpace Pos', v = 1 )
    cmds.setParent('..')

    cmds.columnLayout(adj = True, width = 150, columnAlign=('center'))
    altusCMDUIID_dict['norToggle'] = cmds.checkBox( label='Camera Norm', v = 1 )
    altusCMDUIID_dict['visToggle'] = cmds.checkBox( label='Matte Shadow', v = 0 )
    altusCMDUIID_dict['cauToggle'] = cmds.checkBox( label='Caustics', v = 0 )
    cmds.setParent('..')

    cmds.setParent('..')
    # cmds.separator(h = 5, style = "double")
    # cmds.text( label='', h = 5)

    cmds.separator(h = 4, style = "double")
    cmds.separator(h = 4, style = "double")


    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # Altus Tools Title
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))

    cmds.text( label='--- V-Ray Setup ---', h = 40, fn = 'boldLabelFont', bgc = [0,0,0])
    cmds.setParent('..')

    #########################################################################################
    # RENDER ELEMENTS
    #########################################################################################

    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    cmds.text( label='Setup Scene with basic required render elements',h= 15, fn = 'boldLabelFont', bgc = [.2,.2,.2])
    cmds.setParent('..')


    # Enviroment for element names

    cmds.rowLayout( numberOfColumns=2, adjustableColumn=2 )

    cmds.text( label='Enviroment:    ' )

    cmds.columnLayout(adj = True, width = 50, columnAlign=('center'))
    global createElements_radioCol
    createElements_radioCol = cmds.radioCollection(gl=True)
    cmds.radioButton( l='default names' )
    MDSradiobutton = cmds.radioButton( l='MDS names' )
    cmds.radioCollection(createElements_radioCol, edit=True, select=MDSradiobutton )
    cmds.setParent('..')


    cmds.setParent('..')

    cmds.text( label='After creation of elements; Enable: ' )
    cmds.rowLayout( numberOfColumns=4, adjustableColumn=4 )

    cmds.columnLayout(adj = True, width = 80, columnAlign=('center'))
    altusCMDUIID_dict['albButton'] = cmds.checkBox( label='Diffuse', v = 1 )
    altusCMDUIID_dict['posButton'] = cmds.checkBox( label='World Pos', v = 1 )
    cmds.setParent('..')

    cmds.columnLayout(adj = True, width = 100, columnAlign=('center'))
    altusCMDUIID_dict['norButton'] = cmds.checkBox( label='Camera Norm', v = 1 )
    altusCMDUIID_dict['visButton'] = cmds.checkBox( label='Matte Shadow', v = 0 )
    cmds.setParent('..')

    cmds.columnLayout(adj = True, width = 100, columnAlign=('center'))
    altusCMDUIID_dict['cauButton'] = cmds.checkBox( label='Caustics', v = 0 )
    cmds.text( label='' )
    cmds.setParent('..')

    cmds.columnLayout(adj = True, width = 100, columnAlign=('center'))
    cmds.setParent('..')

    cmds.setParent('..')

    cmds.button(h = 25, label='> Create Elements <', bgc = [.4,.5,.5], command='setupAltusAOV (cmds.checkBox(altusCMDUIID_dict["cauButton"],q = True, v = True), cmds.checkBox(altusCMDUIID_dict["albButton"],q = True, v = True), cmds.checkBox(altusCMDUIID_dict["visButton"],q = True, v = True), cmds.checkBox(altusCMDUIID_dict["posButton"],q = True, v = True), cmds.checkBox(altusCMDUIID_dict["norButton"],q = True, v = True), cmds.radioButton(cmds.radioCollection(createElements_radioCol, query=True, select=True), query=True, l=True ))')




    # Setup Noise Title
    cmds.columnLayout(adj = True, width = 300, columnAlign=('center'))
    cmds.text( label='Setup Scene for Noise-Seed Variance',h= 15, fn = 'boldLabelFont', bgc = [.2,.2,.2])
    cmds.setParent('..')

    # Scene Setup toggles
    cmds.text( label=' Create renderLayers and perform:  ' )

    cmds.rowLayout( numberOfColumns=3, adjustableColumn=3 )
    cmds.text( label='Layer Overrides                        ' )
    cmds.text( label='Render Settings' )
    cmds.text( label='' )
    cmds.setParent('..')

    # Settings
    cmds.rowLayout( numberOfColumns=2, adjustableColumn=2 )
    cmds.columnLayout(adj = True, width = 150, columnAlign=('center'))

    # Layer overrides column
    altusCMDUIID_dict['ALTUSsetseedTOGL'] = cmds.checkBox( label='Set Seed', v = 1 )
    # ALTUSversTOGL = cmds.checkBox( label='Set Version b0/1', v = 0, vis =False )
    cmds.text( label='' )
    cmds.setParent('..')

    # Render Settings column
    cmds.columnLayout(adj = True, width = 150, columnAlign=('center'))
    altusCMDUIID_dict['ALTUSstaticTOGL'] = cmds.checkBox( label='Set Static Noise', v = 0 )
    altusCMDUIID_dict['ALTUSpadTOGL'] = cmds.checkBox( label='Set 4 Frame Padding', v = 1 )
    # ALTUSprefixTOGL = cmds.checkBox( label='Set Filename Prefix', v = 0, vis =False )
    # ALTUSexrTOGL = cmds.checkBox( label='Set to single EXR', v = 0, vis =False )
    cmds.setParent('..')

    cmds.setParent('..')

    cmds.rowLayout( numberOfColumns=2, adjustableColumn=2 )
    # cmds.text( label='Filename Prefix: ' , vis =False)
    # ALTUSprefix = cmds.textField(tx='<Scene>.<Version>', bgc = [.2,.2,.2], vis =False )
    cmds.setParent('..')


    # Seed Input
    cmds.rowLayout( numberOfColumns=7, columnWidth5=(85,250,50, 50, 30), adjustableColumn=2, columnAlign=(5, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text( label='Noise Seed:' )
    cmds.text( label='' )
    # input rand will result in a random seed
    cmds.text( label='b0: ')
    ALTUSseedb0 = cmds.textField(tx='0', width = 50, en=0 )
    cmds.text( label='b1: ' )
    altusCMDUIID_dict['ALTUSseedb1'] = cmds.textField(tx='rand', width = 50 )
    cmds.button(label='?', command='print"DMC seed input for alternate renderLayers"')
    cmds.setParent('..')

    cmds.button(h = 25, label='> Configure Altus RenderLayers <', command='setupAltusRL_button()', bgc = [.4,.5,.5])

    global setupAltusRL_button
    def setupAltusRL_button():
        qALTUSsetseedTOGL = cmds.checkBox(altusCMDUIID_dict['ALTUSsetseedTOGL'], query=True, v=True )
        # qALTUSversTOGL = cmds.checkBox(ALTUSversTOGL, query=True, v=True )
        qALTUSstaticTOGL = cmds.checkBox(altusCMDUIID_dict['ALTUSstaticTOGL'], query=True, v=True )
        qALTUSpadTOGL = cmds.checkBox(altusCMDUIID_dict['ALTUSpadTOGL'], query=True, v=True )
        # qALTUSprefixTOGL = cmds.checkBox(ALTUSprefixTOGL, query=True, v=True )
        # qALTUSexrTOGL = cmds.checkBox(ALTUSexrTOGL, query=True, v=True )

        # qALTUSprefix = cmds.textField(ALTUSprefix, query=True, tx=True )
        # qALTUSseedb0 = cmds.textField(ALTUSseedb0, query=True, tx=True )
        qALTUSseedb1 = cmds.textField(altusCMDUIID_dict['ALTUSseedb1'], query=True, tx=True )

        AltusLayersButton(qALTUSsetseedTOGL,qALTUSstaticTOGL,qALTUSpadTOGL,qALTUSseedb1)


    ############ OTHER METHODS NOT USED ATM ####################

    # cmds.button(h = 25, label='Create Two Temp Scenes', command='ALTUStoRenderFunc()', bgc = [.4,.5,.5], en =False)

    # cmds.rowLayout( numberOfColumns=2, columnWidth3=(150, 150, 150), adjustableColumn=2)
    # cmds.button(h = 25, w= 150, label='Set b0', command='print""', bgc = [.4,.5,.5], en =False)
    # cmds.button(h = 25, w= 150, label='Set b1', command='print""', bgc = [.4,.5,.5], en =False)
    # cmds.setParent('..')
    global AltusDOCK
    AltusDOCK = 'AltusDOCK'

    
    if cmds.dockControl(AltusDOCK, exists=True):
        cmds.deleteUI(AltusDOCK)
    

    cmds.dockControl('AltusDOCK', area='right', content=altusCMDUIID, allowedArea=['left','right'], l='Altus Tools' )
    # cmds.showWindow()

    #########################################################################################################
