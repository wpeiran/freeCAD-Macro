# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Cad\Progetti_K\3D-FreeCad-tools\explode.ui'
#
# Created: Fri Sep 21 14:09:48 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

import FreeCAD, FreeCADGui, os, Part
import PySide
from PySide import QtGui, QtCore
from sys import platform as _platform
import sys,os
import time
global copper_diffuse, silks_diffuse

def say(msg):
    FreeCAD.Console.PrintMessage(msg)
    FreeCAD.Console.PrintMessage('\n')

metal_copper="""material DEF MET-COPPER Material {
        ambientIntensity 0.022727
        diffuseColor 0.7038 0.27048 0.0828
        specularColor 0.780612 0.37 0.000000
        emissiveColor 0.000000 0.000000 0.000000
        shininess 0.2
        transparency 0.0
        }"""    

copper_diffuse = (0.7038, 0.27048, 0.0828)
silks_diffuse = (0.98,0.92,0.84)

# Name      Ambient                             Diffuse                             Specular                            Shininess
# brass     0.329412    0.223529    0.027451    0.780392    0.568627    0.113725    0.992157    0.941176    0.807843    0.21794872
brass_diffuse = (0.780392,0.568627,0.113725)


import importDXF
from kicadStepUptools import make_unicode, make_string

def makeFaceDXF():
    global copper_diffuse, silks_diffuse
    doc=FreeCAD.ActiveDocument
    if doc is None:
        FreeCAD.newDocument()
        doc=FreeCAD.ActiveDocument
    docG=FreeCADGui.ActiveDocument
    Filter=""
    last_pcb_path=""
    pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/kicadStepUp")
    last_pcb_path = pg.GetString("last_pcb_path")
    fn, Filter = PySide.QtGui.QFileDialog.getOpenFileNames(None, "Open File...",
                make_unicode(last_pcb_path), "*.dxf")
    for fname in fn:
        path, name = os.path.split(fname)
        filename=os.path.splitext(name)[0]
        #importDXF.open(os.path.join(dirname,filename))
        if len(fname) > 0:
            #importDXF.open(fname)
            last_pcb_path=os.path.dirname(fname)
            pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/kicadStepUp")
            pg.SetString("last_pcb_path", make_string(last_pcb_path)) # py3 .decode("utf-8")
            pg = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/kicadStepUpGui")
            pcb_color_pos = pg.GetInt('pcb_color')
            #print(pcb_color_pos)
            if pcb_color_pos == 9:
                silks_diffuse = (0.18,0.18,0.18)  #slick black
            else:
                silks_diffuse = (0.98,0.92,0.84) # #antique white  # white (0.906,0.906,0.910)           
            doc=FreeCAD.ActiveDocument
            objects = []
            say("loading... ")
            t = time.time()
            if doc is not None:
                for o in doc.Objects:
                    objects.append(o.Name)
                importDXF.insert(fname, doc.Name)
            else:
                importDXF.open(fname)
            FreeCADGui.SendMsgToActiveView("ViewFit")
            timeP = time.time() - t
            say("loading time = "+str(timeP) + "s")
            
            
            edges=[]
            sorted_edges=[]
            w=[]
            
            for o in doc.Objects:
                if o.Name not in str(objects):
                    if hasattr(o,'Shape'):
                        w1 = Part.Wire(Part.__sortEdges__(o.Shape.Edges))
                        w.append(w1)
            #print (w)
            f=Part.makeFace(w,'Part::FaceMakerBullseye')
            for o in doc.Objects:
                if o.Name not in str(objects):
                    doc.removeObject(o.Name)
            if 'Silk' in filename:
                layerName = 'Silks'
            else:
                layerName = 'Tracks'
            if 'F.' in filename or 'F_' in filename:
                layerName = 'top'+layerName
            if 'B.' in filename or 'B_' in filename:
                layerName = 'bot'+layerName
        
            doc.addObject('Part::Feature',layerName).Shape=f
            newShape=doc.ActiveObject
            botOffset = 1.6
            if 'Silk' in layerName:
                docG.getObject(newShape.Name).ShapeColor = silks_diffuse
            else:
                docG.getObject(newShape.Name).ShapeColor = brass_diffuse #copper_diffuse  #(0.78,0.56,0.11)
            if len (doc.getObjectsByLabel('Pcb')) > 0:
                newShape.Placement = doc.getObjectsByLabel('Pcb')[0].Placement
                #botTracks.Placement = doc.Pcb.Placement
                if len (doc.getObjectsByLabel('Board_Geoms')) > 0:
                    doc.getObject('Board_Geoms').addObject(newShape)
                if hasattr(doc.getObjectsByLabel('Pcb')[0], 'Shape'):
                    botOffset = doc.getObjectsByLabel('Pcb')[0].Shape.BoundBox.ZLength
                else:
                    botOffset = doc.getObjectsByLabel('Pcb')[0].OutList[1].Shape.BoundBox.ZLength
            #elif 'bot' in layerName:
            #    newShape.Placement.Base.z-=1.6
            if 'top' in layerName:
                newShape.Placement.Base.z+=0.07
            if 'bot' in layerName:
                newShape.Placement.Base.z-=botOffset+0.07
            timeD = time.time() - t - timeP
            say("displaying time = "+str(timeD) + "s")
    FreeCADGui.SendMsgToActiveView("ViewFit")
    docG.activeView().viewAxonometric()
##
def checkDXFsettings():
    
    pgD = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
    dxfLI = pgD.GetBool("dxfUseLegacyImporter")
    dxfJG = pgD.GetBool("joingeometry")
    dxfCP = pgD.GetBool("dxfCreatePart")
    checkResult = True
    #FreeCAD.Console.PrintMessage (dxfLI);FreeCAD.Console.PrintMessage (dxfJG); FreeCAD.Console.PrintMessage (dxfCP)
    if not dxfLI:
        FreeCAD.Console.PrintError('DXF Legacy Importer NOT selected\n')
        checkResult = False
    if not dxfJG:
        FreeCAD.Console.PrintError('DXF Join Geometries NOT selected\n')
        checkResult = False
    if not dxfCP:
        FreeCAD.Console.PrintError('DXF Create Simple Part Shapes NOT selected\n')
        checkResult = False
    return checkResult
    
#makeFaceDXF()