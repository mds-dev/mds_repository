'''
Created on Jun 26, 2013

@author: owner
'''
from maya import cmds, mel
import libUtilities, libFile
reload(libUtilities)
import pymel.core as pm
import correctiveBlendshapeCreator as correcter

reload(correcter)

if (cmds.window(correcter.bsWin, q=True, exists=True)):
    cmds.deleteUI(correcter.bsWin, window=True)
global sphereShape
sphereShape = [[0.00, 0.0, 0.56],
               [0.00, 0.28, 0.48],
               [0.00, 0.48, 0.28],
               [0.00, 0.56, 0.00],
               [0.00, 0.48, -0.28],
               [0.00, 0.28, -0.48],
               [0.00, 0.00, -0.56],
               [0.00, -0.28, -0.48],
               [0.00, -0.48, -0.28],
               [0.00, -0.56, 0.00],
               [0.00, -0.48, 0.28],
               [0.00, -0.28, 0.48],
               [0.00, 0.00, 0.56],
               [0.39, 0.00, 0.39],
               [0.56, 0.00, 0.00],
               [0.39, 0.00, -0.39],
               [0.00, 0.00, -0.56],
               [-0.39, 0.00, -0.39],
               [-0.56, 0.00, 0.00],
               [-0.48, 0.28, 0.00],
               [-0.28, 0.48, 0.00],
               [0.00, 0.56, 0.00],
               [0.28, 0.48, 0.00],
               [0.48, 0.28, 0.00],
               [0.56, 0.00, 0.00],
               [0.48, -0.28, 0.00],
               [0.28, -0.48, 0.00],
               [0.00, -0.56, 0.00],
               [-0.28, -0.48, 0.00],
               [-0.48, -0.28, 0.00],
               [-0.56, 0.00, 0.00],
               [-0.39, 0.00, 0.39],
               [0.00, 0.00, 0.56]]


def build_ctrls():
    ##
    ##Build a default setup for a face GUI. Return a dictnary of Ctrl Objects which have links to parent and ctrl itself,
    ##
    # List of faceCtrls
    faceCtrls = []
    faceParents = []

    faceDict = {}
    # Return a class control
    class ctrl(object):
        def __init__(self):
            self.ctrl = ""
            self.par = ""
            self.attr = {}

        def __str__(self):
            return self.ctrl

    # Left Eye
    leftEye = cmds.circle(n="Eye_Ctrl_L", ch=0, o=1, r=1)[0]
    leftEyePar = libUtilities.parZero(leftEye, "Grp")
    faceCtrls.append(leftEye)
    faceParents.append(leftEyePar)

    faceDict["leftEye"] = ctrl()
    faceDict["leftEye"].ctrl = pm.PyNode(leftEye)
    faceDict["leftEye"].par = pm.PyNode(leftEyePar)
    # Right Eye
    rightEye = cmds.circle(n="Eye_Ctrl_R", ch=0, o=1, r=1)[0]
    rightEyePar = libUtilities.parZero(rightEye, "Grp")
    faceCtrls.append(rightEye)
    faceParents.append(rightEyePar)

    faceDict["rightEye"] = ctrl()
    faceDict["rightEye"].ctrl = pm.PyNode(rightEye)
    faceDict["rightEye"].par = pm.PyNode(rightEyePar)

    # Mouth

    libFile.importFile(r"\\productions\boad\Pipeline\tools\maya\rigging\XY_Box.ma")

    mouthCtrl = pm.PyNode("Mouth_Ctrl")

    shapeInfo = [[0.32798915216208485, 0.15672232497824087, -1.1994460910207978e-16],
                 [-2.5286341215658653e-17, -0.071295490151495819, -1.6245036249775376e-16],
                 [-0.32798915216208457, 0.15672232497824096, -1.1994460910207978e-16],
                 [-0.46384670729887317, -4.002721177608611e-15, -1.2258929400370895e-16],
                 [-0.32798915216208463, -0.1567223249782487, -1.1845819213636195e-16],
                 [-6.6784107271810394e-17, -0.22163883751087765, 0.0],
                 [0.32798915216208441, -0.15672232497824881, -1.1845819213636195e-16],
                 [0.46384670729887317, -4.1859892197389677e-15, -1.2258929400370895e-16],
                 [0.32798915216208485, 0.15672232497824087, -1.1994460910207978e-16],
                 [-2.5286341215658653e-17, -0.071295490151495819, -1.6245036249775376e-16],
                 [-0.32798915216208457, 0.15672232497824096, -1.1994460910207978e-16]]

    mouthCtrlPar = pm.PyNode("Mouth_Ctrl_boxTemplate")
    mouthCtrl.setCVs(shapeInfo)
    mouthCtrl.cv[1].select()
    pm.move([0.128808, 1.202678, -0.135647], r=1)
    pm.move([-0.128808, -1.202678, 0.135647], r=1)
    pm.select(cl=1)
    faceParents.append(str(mouthCtrlPar))

    faceDict["mouth"] = ctrl()
    faceDict["mouth"].ctrl = mouthCtrl
    faceDict["mouth"].par = mouthCtrlPar

    faceDict["mouth"].clamps = {}

    faceDict["mouth"].clamps["max_y"] = pm.PyNode("max_y")
    faceDict["mouth"].clamps["min_y"] = pm.PyNode("min_y")
    faceDict["mouth"].clamps["max_x"] = pm.PyNode("max_x")
    faceDict["mouth"].clamps["min_x"] = pm.PyNode("min_x")


    # Face Ctrl
    face = cmds.circle(n="Face_Ctrl", ch=0, o=1, r=11)[0]
    facePar = libUtilities.parZero(face, "Grp")

    faceDict["face"] = ctrl()
    faceDict["face"].ctrl = pm.PyNode(face)
    faceDict["face"].par = pm.PyNode(facePar)

    leftEyePar.translate.set(2 * 2, 4 * 2, 0)
    rightEyePar.translate.set(-2 * 2, 4 * 2, 0)
    mouthCtrlPar.translate.set(0, 1, 0)

    # Parent the ctrl
    for par in faceParents:

        try:
            pm.parent(par, face)
        except:
            print "Failed to parent %s to %s" % (par, face)
            print pm.objExists(par)
            print pm.objExists(face)


    # Lock the attributes
    for ctrl in faceCtrls + faceParents:
        ctrl = pm.PyNode(ctrl)
        ctrlShape = ctrl.getShape()
        if ctrlShape:
            ctrlShape.rename(str(ctrl) + "Shape")
        for attr in ctrl.listAttr(k=1):
            attr.lock()
            mel.eval('setAttr -keyable false -channelBox false "%s"' % str(attr))
    # Unlock all R_Eye L_Eye
    for eye in [faceDict["leftEye"].ctrl, faceDict["rightEye"].ctrl]:
        for attr in [eye.tx, eye.ty]:
            attr.unlock()
            mel.eval('setAttr  -channelBox true "%s"' % str(attr))
            mel.eval('setAttr  -keyable true "%s"' % str(attr))
            spl = str(attr).split(".")
            mel.eval("transformLimits -%s -1 1 -e%s 1 1 %s;" % (attr.shortName(), attr.shortName(), spl[0]))

    shapeInfo = [[8.619727873803475, 8.6197278738034626, 0.0],
                 [-1.3907487668612258e-15, 12.190136063098267, 0.0],
                 [-8.6197278738034662, 8.6197278738034662, 0.0],
                 [-8.9389020234023882, 3.5323964579609529e-15, 0.0],
                 [-6.3207582371099811, -6.1185245462649771, 0.0],
                 [-3.6731258999495718e-15, -9.5017388884022171, 0.0],
                 [6.3207582371099758, -6.1185245462649807, 0.0],
                 [8.9389020234023882, -6.5473458592086441e-15, 0.0],
                 [8.619727873803475, 8.6197278738034626, 0.0],
                 [-1.3907487668612258e-15, 12.190136063098267, 0.0],
                 [-8.6197278738034662, 8.6197278738034662, 0.0]]
    face = pm.PyNode(face)
    face.setCVs(shapeInfo)
    face.cv[1].select()
    pm.move([0.128808, 1.202678, -0.135647], r=1)
    pm.move([-0.128808, -1.202678, 0.135647], r=1)
    pm.select(cl=1)

    libUtilities.colorCurve("Eye_Ctrl_L", 18)
    libUtilities.colorCurve("Eye_Ctrl_R", 20)
    libUtilities.colorCurve("Mouth_Ctrl", 23)
    libUtilities.colorCurve("Face_Ctrl", 21)
    return faceDict


def add_corrective(mainGeo, left, right, preCorrective):
    ##
    ##Add a corrective blendshape for two blendshape, eg use a corrective middle smile for smile_L and smile_R.
    ##
    corrective = correcter.createCorrectiveBlendshape(mainGeo, left, right)
    pm.select(preCorrective, corrective)
    blend = pm.blendShape()[0]
    eval("blend.%s.set(1)" % preCorrective)
    pm.delete(corrective, ch=1)
    dummy_blendshape = correcter.applyBlendshapesToDummy(mainGeo, left, right, corrective)
    correcter.addDummyToMasterBlendshape(mainGeo, dummy_blendshape)
    correcter.addCorrectiveExpressionToMaster(mainGeo, dummy_blendshape, left, right)
    pm.delete(corrective, dummy_blendshape)


def add_to_blend(blendShape, target, newShape):
    ##
    ##Add a new blendtarget to a blendshape
    ##
    ind = get_new_blend_index(blendShape)
    print "blendShape -e  -t %s %i %s 1 %s;" % (target, ind, newShape, blendShape)
    mel.eval("blendShape -e  -t %s %i %s 1 %s;" % (target, ind, newShape, blendShape))


def get_new_blend_index(blendShape):
    ##
    ##Get the next blend target. Useful for adding inbetween shapes
    ##

    return pm.blendShape(blendShape, q=1, weightCount=1) + 1


def build_y_quarterbox(type, label=[]):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}
        squareShape = [[-0.112423266524, 1.0, 0.0],
                       [-0.112423266524, -0.0071601628344506452, 0.0],
                       [0.112423266524, -0.0071601628344506452, 0.0],
                       [0.112, 1.0, 0.0],
                       [-0.112423266524, 1.0, 0.0]]
        box = pm.curve(d=1, p=squareShape, n=type + "_Prnt")
        boxShape = box.getShape()
        boxShape.overrideEnabled.set(1)
        boxShape.overrideDisplayType.set(1)

        ctrl = pm.circle(nr=[0, 0, 0], r=0.2, ch=0, n=type + "_Ctrl")[0]
        pm.parent(ctrl, box)
        pm.transformLimits(ctrl, tx=[0, 0], etx=[1, 1], ety=[1, 1], ty=[0, 1])
        libUtilities.lockAttr(str(ctrl), ["tz", "tx", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["border"] = box
        mainDict["ctrl"] = ctrl

        if label:
            mainDict["label"] = build_label(label, box)

        return mainDict
    else:
        raise Exception(type + " setup already exists")


def build_y_halfbox(type, label=[]):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}

        squareShape = [[-0.112423266524, 1.0, 0.0],
                       [-0.112423266524, -1.0, 0.0],
                       [0.112423266524, -1.0, 0.0],
                       [0.112, 1.0, 0.0],
                       [-0.112423266524, 1.0, 0.0]]

        box = pm.curve(d=1, p=squareShape, n=type + "_Prnt")
        boxShape = box.getShape()
        boxShape.overrideEnabled.set(1)
        boxShape.overrideDisplayType.set(1)

        ctrl = pm.circle(nr=[0, 0, 0], r=0.2, ch=0, n=type + "_Ctrl")[0]
        pm.parent(ctrl, box)
        pm.transformLimits(ctrl, tx=[0, 0], etx=[1, 1], ety=[1, 1], ty=[-1, 1])
        libUtilities.lockAttr(str(ctrl), ["tz", "tx", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["border"] = box
        mainDict["ctrl"] = ctrl

        if label:
            mainDict["label"] = build_label(label, box)

        return mainDict

    else:
        raise Exception(type + " setup already exists")


def build_upper_halfbox(type, label=[], connections=True):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}

        squareShape = [[-1.0, 1.0, 0.0],
                       [-1.0, 0.0043876273513161479, 0.0],
                       [1.0, 0.0043876273513161479, 0.0],
                       [1.0, 1.0, 0.0],
                       [-1.0, 1.0, 0.0]]

        box = pm.curve(d=1, p=squareShape, n=type + "_Prnt")
        boxShape = box.getShape()
        boxShape.overrideEnabled.set(1)
        boxShape.overrideDisplayType.set(1)
        ctrl = pm.circle(nr=[0, 0, 0], r=0.2, ch=0, n=type + "_Ctrl")[0]
        pm.parent(ctrl, box)
        pm.transformLimits(ctrl, tx=[-1, 1], etx=[1, 1], ety=[1, 1], ty=[0, 1])
        libUtilities.lockAttr(str(ctrl), ["tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["border"] = box
        mainDict["ctrl"] = ctrl

        if connections:
            connect_dict = {}
            connect_dict["TopLeftCorner"] = build_left_top_corner(type, ctrl)
            connect_dict["TopRightCorner"] = build_right_top_corner(type, ctrl)
            mainDict["connections"] = connect_dict

        if label:
            mainDict["label"] = build_label(label, box)

        return mainDict
    else:
        raise Exception(type + " setup already exists")


def build_fullbox(type, label=[], connections=True):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}

        squareShape = [[-1.0, 1.0, 0.0],
                       [-1.0, -1.0, 0.0],
                       [1.0, -1.0, 0.0],
                       [1.0, 1.0, 0.0],
                       [-1.0, 1.0, 0.0]]

        box = pm.curve(d=1, p=squareShape, n=type + "_Prnt")
        boxShape = box.getShape()
        boxShape.overrideEnabled.set(1)
        boxShape.overrideDisplayType.set(1)
        ctrl = pm.circle(nr=[0, 0, 0], r=0.2, ch=0, n=type + "_Ctrl")[0]
        pm.parent(ctrl, box)
        pm.transformLimits(ctrl, tx=[-1, 1], etx=[1, 1], ety=[1, 1], ty=[-1, 1])
        libUtilities.lockAttr(str(ctrl), ["tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["border"] = box
        mainDict["ctrl"] = ctrl

        if connections:
            connect_dict = {}
            connect_dict["TopLeftCorner"] = build_left_top_corner(type, ctrl)
            connect_dict["TopRightCorner"] = build_right_top_corner(type, ctrl)
            connect_dict["BottomLeftCorner"] = build_left_bottom_corner(type, ctrl)
            connect_dict["BottomRightCorner"] = build_right_bottom_corner(type, ctrl)
            mainDict["connections"] = connect_dict

        if label:
            mainDict["label"] = build_label(label, box)

        return mainDict
    else:
        raise Exception(type + " setup already exists")


def build_face_full_control(type, connections=True):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}
        prnt = pm.createNode("transform", n=type + "_Prnt")
        ctrl = pm.curve(d=1, p=sphereShape, n=type + "_Ctrl")
        pm.parent(ctrl, prnt)
        pm.transformLimits(ctrl, tx=[-1, 1], etx=[1, 1], ety=[1, 1], ty=[-1, 1])
        libUtilities.lockAttr(str(ctrl), ["tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["prnt"] = prnt
        mainDict["ctrl"] = ctrl

        if connections:
            connect_dict = {}
            connect_dict["RightCorner"] = build_right_corner(type, ctrl)
            connect_dict["LeftCorner"] = build_left_corner(type, ctrl)
            connect_dict["BottomCorner"] = build_bottom_corner(type, ctrl)
            connect_dict["TopCorner"] = build_top_corner(type, ctrl)
            mainDict["connections"] = connect_dict

        return mainDict

    else:
        raise Exception(type + " setup already exists")


def build_face_y_control(type, connections=True):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}
        prnt = pm.createNode("transform", n=type + "_Prnt")
        ctrl = pm.curve(d=1, p=sphereShape, n=type + "_Ctrl")
        pm.parent(ctrl, prnt)
        pm.transformLimits(ctrl, tx=[0, 0], etx=[0, 0], ety=[1, 1], ty=[-1, 1])
        libUtilities.lockAttr(str(ctrl), ["tx", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["prnt"] = prnt
        mainDict["ctrl"] = ctrl

        if connections:
            connect_dict = {}
            connect_dict["BottomCorner"] = build_bottom_corner(type, ctrl)
            connect_dict["TopCorner"] = build_top_corner(type, ctrl)
            mainDict["connections"] = connect_dict
        return mainDict
    else:
        raise Exception(type + " setup already exists")


def build_face_x_control(type, connections=True):
    if not pm.objExists(type + "_Prnt"):
        mainDict = {}
        prnt = pm.createNode("transform", n=type + "_Prnt")
        ctrl = pm.curve(d=1, p=sphereShape, n=type + "_Ctrl")
        pm.parent(ctrl, prnt)
        pm.transformLimits(ctrl, tx=[-1, 1], etx=[1, 1])
        libUtilities.lockAttr(str(ctrl), ["ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"])

        mainDict["prnt"] = prnt
        mainDict["ctrl"] = ctrl

        if connections:
            connect_dict = {}
            connect_dict["RightCorner"] = build_right_corner(type, ctrl)
            connect_dict["LeftCorner"] = build_left_corner(type, ctrl)
            mainDict["connections"] = connect_dict
        return mainDict
    else:
        raise Exception(type + " setup already exists")


def build_label(label, box):
    label_dict = {}
    topBottom = ["top", "bottom"]
    for i in range(len(label)):
        curLabel = build_text(label[i])
        pm.parent(curLabel, box)
        label_dict[topBottom[i]] = curLabel

    return label_dict


def build_text(text):
    # curLabel = pm.PyNode(pm.textCurves(ch=10,f="Times New Roman|h-13|w400|c0", t=text)[0])
    curLabel = pm.PyNode(pm.textCurves(ch=10, f="cafeta|h-13|w400|c0", t=text)[0])
    pm.parent(curLabel.listRelatives(type="nurbsCurve", ad=1), curLabel)
    for transform in curLabel.listRelatives(type="transform", ad=1):
        if not transform.getShape():
            pm.delete(transform)
    curLabel.scale.set(0.2, 0.2, 0.2)
    curLabel.overrideEnabled.set(1)
    curLabel.overrideDisplayType.set(1)
    return curLabel


def build_left_top_corner(type, ctrl):
    ##************************************** build connections for right top corner shape *******************************
    ##**************************************************************************************************************


    leftTopCornerAddDoubleLinear = pm.createNode("addDoubleLinear", n=type + "_LTopLeftCorner_ADL_utility")
    ctrl.tx >> leftTopCornerAddDoubleLinear.input1
    leftTopCornerAddDoubleLinear.input2.set(1)

    leftTopCornerClampX = pm.createNode("clamp", n=type + "_LTopLeftCorner_ClampX_utility")
    leftTopCornerAddDoubleLinear.output >> leftTopCornerClampX.inputR
    leftTopCornerClampX.maxR.set(1)

    leftTopCornerClampY = pm.createNode("clamp", n=type + "_LTopLeftCorner_ClampY_utility")
    ctrl.ty >> leftTopCornerClampY.inputR
    leftTopCornerClampY.maxR.set(1)

    leftTopCornerMD = pm.createNode("multiplyDivide", n=type + "_LTopLeftCorner_MD_utility")
    leftTopCornerClampX.outputR >> leftTopCornerMD.input1X
    leftTopCornerClampY.outputR >> leftTopCornerMD.input2X

    return leftTopCornerMD


def build_right_top_corner(type, ctrl):
    rightTopLeftXMD = pm.createNode("multiplyDivide", n=type + "_RTopLeftMD_utility")
    ctrl.tx >> rightTopLeftXMD.input1X
    rightTopLeftXMD.input2X.set(-1)

    rightTopCornerAddDoubleLinear = pm.createNode("addDoubleLinear", n=type + "_RTopLeftCorner_ADL_utility")
    rightTopLeftXMD.outputX >> rightTopCornerAddDoubleLinear.input1
    rightTopCornerAddDoubleLinear.input2.set(1)

    rightTopCornerClampX = pm.createNode("clamp", n=type + "_RTopLeftCorner_ClampX_utility")
    rightTopCornerAddDoubleLinear.output >> rightTopCornerClampX.inputR
    rightTopCornerClampX.maxR.set(1)

    rightTopCornerClampY = pm.createNode("clamp", n=type + "_RTopLeftCorner_ClampY_utility")
    ctrl.ty >> rightTopCornerClampY.inputR
    rightTopCornerClampY.maxR.set(1)

    rightTopCornerMD = pm.createNode("multiplyDivide", n=type + "_RTopLeftCorner_MD_utility")
    rightTopCornerClampX.outputR >> rightTopCornerMD.input1X
    rightTopCornerClampY.outputR >> rightTopCornerMD.input2X
    return rightTopCornerMD


def build_left_bottom_corner(type, ctrl):
    leftBottomLeftMD = pm.createNode("multiplyDivide", n=type + "_LBottomCorner_MD_utility")
    ctrl.ty >> leftBottomLeftMD.input1X
    leftBottomLeftMD.input2X.set(-1)

    leftBottomCornerClamp = pm.createNode("clamp", n=type + "_LBottomCorner_Clamp_utility")
    leftBottomLeftMD.outputX >> leftBottomCornerClamp.inputR
    leftBottomCornerClamp.maxR.set(1)

    leftBottomCornerAddDoubleLinear = pm.createNode("addDoubleLinear", n=type + "_LBottomCorner_ADL_utility")
    ctrl.tx >> leftBottomCornerAddDoubleLinear.input1
    leftBottomCornerAddDoubleLinear.input2.set(1)

    leftBottomCornerClamp2 = pm.createNode("clamp", n=type + "_LBottomCorner_Clamp2_utility")
    leftBottomCornerAddDoubleLinear.output >> leftBottomCornerClamp2.inputR
    leftBottomCornerClamp2.maxR.set(1)

    leftBottomCornerMD2 = pm.createNode("multiplyDivide", n=type + "_LBottomCorner_MD2_utility")
    leftBottomCornerClamp2.outputR >> leftBottomCornerMD2.input1X
    leftBottomCornerClamp.outputR >> leftBottomCornerMD2.input2X
    return leftBottomCornerMD2


def build_right_bottom_corner(type, ctrl):
    rightBottomRightMD1 = pm.createNode("multiplyDivide", n=type + "_RBottomCorner_MD1_utility")
    rightBottomCornerAddDoubleLinear = pm.createNode("addDoubleLinear", n=type + "_RBottomCorner_ADL_utility")
    rightBottomRightMD1.input2X.set(-1)

    ctrl.tx >> rightBottomRightMD1.input1X
    rightBottomRightMD1.outputX >> rightBottomCornerAddDoubleLinear.input1
    rightBottomCornerAddDoubleLinear.input2.set(1)

    rightBottomClampX = pm.createNode("clamp", n=type + "_RBottomX_Clamp_utility")
    rightBottomCornerAddDoubleLinear.output >> rightBottomClampX.inputR
    rightBottomClampX.maxR.set(1)

    rightBottomRightMDY = pm.createNode("multiplyDivide", n=type + "_RBottomCorner_MDY_utility")
    ctrl.ty >> rightBottomRightMDY.input1X
    rightBottomRightMDY.input2X.set(-1)

    rightBottomClampY = pm.createNode("clamp", n=type + "_RBottomY_Clamp_utility")
    rightBottomRightMDY.outputX >> rightBottomClampY.inputR
    rightBottomClampY.maxR.set(1)

    rightBottomMD2 = pm.createNode("multiplyDivide", n=type + "_RBottom_MD2_utility")
    rightBottomClampY.outputR >> rightBottomMD2.input1X
    rightBottomClampX.outputR >> rightBottomMD2.input2X

    return rightBottomMD2


def build_right_corner(type, ctrl):
    rightMD1 = pm.createNode("multiplyDivide", n=type + "_RCorner_MD1_utility")
    rightMD1.input2X.set(-1)

    ctrl.tx >> rightMD1.input1X

    rightClamp = pm.createNode("clamp", n=type + "_RCorner_Clamp_utility")
    rightMD1.outputX >> rightClamp.inputR
    rightClamp.maxR.set(1)
    rightClamp.minR.set(0)

    return rightClamp


def build_bottom_corner(type, ctrl):
    bottomMD1 = pm.createNode("multiplyDivide", n=type + "_BCorner_MD1_utility")
    bottomMD1.input2X.set(-1)

    ctrl.ty >> bottomMD1.input1X
    bottomClamp = pm.createNode("clamp", n=type + "_BCorner_Clamp_utility")
    bottomMD1.outputX >> bottomClamp.inputR
    bottomClamp.maxR.set(1)
    bottomClamp.minR.set(0)

    return bottomClamp


def build_left_corner(type, ctrl):
    leftClamp = pm.createNode("clamp", n=type + "_LCorner_Clamp_utility")
    ctrl.tx >> leftClamp.inputR
    leftClamp.maxR.set(1)
    leftClamp.minR.set(0)

    return leftClamp


def build_top_corner(type, ctrl):
    topClamp = pm.createNode("clamp", n=type + "_TCorner_Clamp_utility")
    ctrl.ty >> topClamp.inputR
    topClamp.maxR.set(1)
    topClamp.minR.set(0)

    return topClamp

# cmds.file(new=1,f=1)
# build_fullbox("Mouth",["Open","Close"])
