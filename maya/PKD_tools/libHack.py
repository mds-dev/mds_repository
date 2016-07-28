'''
Created on 22/05/2014

@author: admin
'''
'''
Created on 6/04/2014

@author: admin
'''
import pymel.core as pm
from libs import libUtilities


def hack(ctrl, upAxis="", mirror=1, courseCorrect=False, worldOrient=False, remap={}):
    ctrl = pm.PyNode(ctrl)
    # Get the name
    name = ctrl.name()

    # OldParent
    oldParent = ctrl.getParent()
    # Ctrl
    ctrlShape = ctrl.getShape()
    ctrlShapeName = ctrlShape.name()
    # Change _Ctrl to _Old
    ctrl.rename(name.replace("_Ctrl", "_Old"))
    # Shape

    # Create a offset
    hackSet = pm.createNode("transform", name=name.replace("_Ctrl", "_HackSet"))
    # Create New Transform
    new_ctrl = pm.createNode("transform", name=name)
    # Create new Xtra
    newXtra = pm.createNode("transform", name=name.replace("_Ctrl", "_NewXtra"))
    # Parent the Control to Xtra

    libUtilities.snapper(newXtra, ctrl)

    pm.parent(newXtra, oldParent)
    pm.parent(ctrl, newXtra)
    # Snap to Controller
    pm.parent(new_ctrl, hackSet)

    if worldOrient:
        # pm.parent(new_ctrl,hackSet)
        libUtilities.snapper(hackSet, ctrl, r=0)
    else:
        # Create Snap Vector

        vector = pm.createNode("transform", name="tempVec")
        vector.attr(upAxis).set(mirror)
        # parent to Control
        pm.parent(vector, new_ctrl)
        # Course correct
        courseVector = None
        if courseCorrect:
            courseVector = pm.createNode("transform", name="courseCorrect")
            courseVector.tx.set(mirror)
            pm.parent(courseVector, new_ctrl)

        # Snap to Controller
        # pm.parent(new_ctrl,hackSet)
        libUtilities.snapper(hackSet, ctrl)
        # parent snap to world
        pm.parent(vector, w=1)
        if courseCorrect:
            pm.parent(courseVector, w=1)

        # pm.delete(pm.aimConstraint(xtra,snap,aimVector= [0,1,0],upVector=[0,1,0]))
        aimVector = None
        #     if upAxis == "tx":
        #         aimVector = [1,0,0]
        #     elif upAxis == "ty":
        #         aimVector = [0,1,0]
        #     else:
        #         aimVector = [0,0,1]

        pm.delete(pm.aimConstraint(vector, hackSet, aimVector=[0, 1, 0], upVector=[0, mirror, 0]))

        if courseCorrect:
            courseVector.select()
            pm.delete(pm.aimConstraint(courseVector, hackSet, aimVector=[1, 0, 0], upVector=[0, mirror, 0]))
            pm.delete(courseVector)


        # pm.delete(snap)
        pm.delete(vector)

    # Parent to oldParent
    pm.parent(hackSet, oldParent)

    # Reparent
    pm.parent(newXtra, new_ctrl)


    # Get the shape
    pm.parent(ctrlShape, new_ctrl, r=1, s=1)

    ctrlShape.rename(ctrlShapeName)
    if not courseCorrect:
        libUtilities.snapper(ctrlShape.cv, ctrl, t=0)


    # Set the default values status
    for default in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
        new_ctrl.attr(default).setLocked(ctrl.attr(default).isLocked())
        new_ctrl.attr(default).setKeyable(ctrl.attr(default).isKeyable())
        new_ctrl.attr(default).showInChannelBox(ctrl.attr(default).isInChannelBox())

    attrList = []
    # Create the User Defeined Attributes and transfer
    for attr in ctrl.listAttr(ud=1):
        nn = pm.attributeQuery(attr.longName(), node=ctrl, niceName=True)
        sn = attr.longName()

        if attr.type() == "enum":
            pm.addAttr(new_ctrl, at="enum", en='Average:Longest:Shortest', longName=sn, nn=nn)
        if attr.type() == "string":
            pm.addAttr(new_ctrl, dt="string", longName=sn, nn=nn)
            strInput = attr.get()
            if strInput == None:
                strInput = ''
            new_ctrl.attr(sn).set(strInput)

        if attr.type() == "double":
            sv = (attr.getSoftRange()[0] != None)
            max = None
            if attr.getMax() is None:
                max = 1000
            else:
                max = attr.getMax()
            min = None
            if attr.getMin() is None:
                min = -1000
            else:
                min = attr.getMin()
            libUtilities.addAttr(new_ctrl, attrName=nn, attrMax=max, attrMin=min, SV=sv, sn=sn)
        if attr.type() == "bool":
            pm.addAttr(new_ctrl, at="bool", longName=sn, nn=nn)

        new_ctrl.attr(sn).setLocked(attr.isLocked())
        new_ctrl.attr(sn).setKeyable(attr.isKeyable())
        new_ctrl.attr(sn).showInChannelBox(attr.isInChannelBox())
        attrList.append(attr.shortName().split(".")[-1])

    pm.copyAttr(ctrl, new_ctrl, inConnections=True, values=True, outConnections=True, attribute=attrList + ["message"])

    new_ctrl.rotateOrder.set(2)
    new_ctrl.select()

    for attr in remap:
        for con in ctrl.attr(attr).listConnections(p=1):
            new_ctrl.attr(remap[attr]) >> con


def fix_pv(pv, ik):
    parentPV = pv.getParent()
    constraint = pm.listRelatives(parentPV, type="constraint")[0]

    placementConnection = constraint.w0.listConnections(p=1)[0]
    pm.disconnectAttr(placementConnection, constraint.w0)

    ikConnection = constraint.w1.listConnections(p=1)[0]
    pm.disconnectAttr(ikConnection, constraint.w1)

    pm.delete(parentPV, cn=1)

    newConstraint = pm.parentConstraint("Placement", parentPV, mo=1)
    newConstraint.w0.set(0)
    pm.parentConstraint(ik, parentPV, mo=1)

    placementConnection >> newConstraint.w0
    ikConnection >> newConstraint.w1
