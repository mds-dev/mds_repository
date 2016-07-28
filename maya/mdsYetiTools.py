import os.path
import os
import maya.cmds as cmds



def mdsPrePublishYetiCache():
    selectedYetiNodes = cmds.ls(sl=True, dag=True, ni=True, type='pgYetiMaya')

    if len(selectedYetiNodes) == 1:
        yetiOldSh = selectedYetiNodes[0]
        yetiNewSh = mel.eval('pgYetiCreate()')
        yetiOld = yetiOldSh[:yetiOldSh.find('Shape')]
        yetiNew = yetiNewSh[:yetiNewSh.find('Shape')]

        yetiNewName = yetiOld+"_cached"

        shade = cmds.listSets(t=1, ets=True, o=yetiOldSh)
        cmds.sets(yetiNewSh, e=True, fe = shade[0])

        attrField = cmds.getAttr(yetiOldSh+'.outputCacheFileName')
        cmds.setAttr(yetiNewSh+'.viewportDensity', 0.1)
        cmds.setAttr(yetiNewSh+'.viewportWidth', 5)
        cmds.setAttr(yetiNewSh+'.fileMode', 1)
        cmds.setAttr(yetiNewSh+'.cacheFileName', attrField, typ='string')
        cmds.getAttr(yetiOldSh+'.ghostRangeEnd')

        cmds.rename(yetiNew, yetiNewName)

        parent = cmds.listRelatives(selectedYetiNodes[0], p=True, f=True)
        cmds.hide(cmds.listRelatives(parent, p=True, f=True))
        cmds.currentTime( cmds.playbackOptions( q=True,ast=True), edit=True )

        print('Made an empty Yeti node with cache and shader network of '+yetiOld )

    else:
        cmds.error( 'Please select the single yeti node you wish to use for publishing' )

def mdsSetUpYetiScene():
    selYetiNode = cmds.ls(sl=True, dag=True, ni=True, type='pgYetiMaya')
    selMeshNode = cmds.ls(sl=True, dag=True, ni=True, type='mesh')

    if len(selYetiNode) and len(selMeshNode)==2 and len(cmds.ls(sl=True))==3:
        print('Yeti Node is = '+selYetiNode[0]+'\n')
        print('Base Mesh is = '+selMeshNode[0]+'\n')
        print ('Anim Mesh is = '+selMeshNode[1]+'\n')

        cmds.select(selMeshNode[0], r=True)
        mel.eval('CreateTextureReferenceObject')
        cmds.hide()

        cmds.setAttr(selMeshNode[0]+'.yetiSubdivision',1)
        cmds.select(selMeshNode[1], r=True)
        cmds.select(selMeshNode[0], add=True)
        cmds.blendShape( foc=True,o='world', w=[0,1]);

        print('Linking to Alembic Completed!')

        fileName = os.path.basename(cmds.file(q=True, sn=True)).replace('.ma','').replace('_Fur_','_furSim_')
        userhome = os.path.expanduser('~')
        desktopFolder = userhome.replace('/Documents','') + '/Desktop/furSim/' + fileName +'/'

        if not os.path.exists(desktopFolder):
            os.makedirs(desktopFolder)

        cmds.setAttr(selYetiNode[0]+'.outputCacheFileName', desktopFolder + fileName+'.%04d.fur', typ='string')

        # startAnim = cmds.playbackOptions(query=True, ast=True)
        # endAnim = cmds.playbackOptions(query=True, aet=True)

        parent = cmds.listRelatives(selMeshNode[0], p=True, f=True)
        cmds.hide(cmds.listRelatives(parent, p=True, f=True))

    else:
        cmds.error ('Please select: ONE yeti node, ONE base mesh, ONE animated alembic mesh. In that order only.')

# def mdsHARDCODE_fredaCat():
#     if cmds.objExists('groom_fredaCat_main') and cmds.objExists('groom_fredaCat_whiskers'):
#         cmds.select('groom_fredaCat_main', r=True)
#         cmds.select('groom_fredaCat_whiskers', add=True)
#
#         if cmds.objExists('animatedAlembicGroup|fredaCat_model_group*|fredaCat_eye_group|fredaCat_eye_L_group|geo_fredaCat_eyeConjunctiva_L'):
#             cmds.select('animatedAlembicGroup|fredaCat_model_group*|fredaCat_eye_group|fredaCat_eye_L_group|geo_fredaCat_eyeConjunctiva_L', add=True)
#
#         if cmds.objExists('animatedAlembicGroup|fredaCat_model_group*|fredaCat_eye_group|fredaCat_eye_R_group|geo_fredaCat_eyeConjunctiva_R'):
#             cmds.select('animatedAlembicGroup|fredaCat_model_group*|fredaCat_eye_group|fredaCat_eye_R_group|geo_fredaCat_eyeConjunctiva_R', add=True)
#
#         if cmds.objExists('animatedAlembicGroup|fredaCat_model_group*|geo_fredaCat_skin_LOD2'):
#             cmds.select('animatedAlembicGroup|fredaCat_model_group*|geo_fredaCat_skin_LOD2', add=True)
#
#         if cmds.objExists('fredaCat_model_group1|fredaCat_eye_group|fredaCat_eye_L_group|geo_fredaCat_eyeConjunctiva_L'):
#             cmds.select('fredaCat_model_group1|fredaCat_eye_group|fredaCat_eye_L_group|geo_fredaCat_eyeConjunctiva_L', add=True)
#
#         if cmds.objExists('fredaCat_model_group1|fredaCat_eye_group|fredaCat_eye_R_group|geo_fredaCat_eyeConjunctiva_R'):
#             cmds.select('fredaCat_model_group1|fredaCat_eye_group|fredaCat_eye_R_group|geo_fredaCat_eyeConjunctiva_R', add=True)
#
#         if cmds.objExists('fredaCat_model_group1|geo_fredaCat_skin_LOD2'):
#             cmds.select('fredaCat_model_group1|geo_fredaCat_skin_LOD2', add=True)
#
#         if cmds.objExists('pandent_Claw'):
#             cmds.select('pandent_Claw', add=True)
#
#         if cmds.objExists('pandent_Sphere'):
#             cmds.select('pandent_Sphere', add=True)
#
#         if cmds.objExists('collar_leatherCollar'):
#             cmds.select('collar_leatherCollar', add=True)

def mdsYetiSetupCall():
    mdsSetUpYetiScene()
    #mdsHARDCODE_fredaCat()

def mdsYetiGroomCollideWith():
    yetiGrooms = cmds.ls(sl=True, dag=True, ni=True, type='pgYetiGroom')
    colliderMeshes = cmds.ls(sl=True, dag=True, ni=True, type='mesh')

    for selGroom in yetiGrooms:
        for selMesh in colliderMeshes:
            test=True
            count = -1
            while test:
                count+=1
                if not cmds.connectionInfo(selGroom+'.collisionGeometry['+str(count)+']', isDestination=True):
                    test = False

                if count > 100:
                    test = False

            cmds.connectAttr(selMesh+'.worldMesh[0]', selGroom+'.collisionGeometry['+str(count)+']', f=True)
            print ('Linked collision object '+selMesh+' to '+selGroom+'.\n');
    cmds.currentTime( cmds.playbackOptions( q=True,ast=True), edit=True )
