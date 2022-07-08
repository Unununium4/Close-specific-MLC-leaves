# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 08:35:23 2021

@author: anmorrow
tested with brainlab, head mrn 44444444
"""

import pydicom
import numpy as np
import random
import os

"""
[[list of fields to change],[[leaf pairs to change for field 1],[leaf pairs to change for field two],...]]
the user puts these in directly.  we will subtract one from each value later as the arrays are zero indexed.

in eclipse, the leaf closest to CAX on the Y2 side is 31.  The leaf closest to CAX on the Y1 side is 30.

"""

mypath = r"K:\Physics Division\Personal folders\ANM\code\closeMLCs\test"
os.chdir(mypath)
planFileName = "MC.dcm"
#planFileName = "test.dcm" #novalis test
planFile = pydicom.dcmread(planFileName)
#toChange = [[5],[[27,33]]] #tbtest
#toChange = [[5],[[24,25,35]]] #novalis test
toChange = [[1,2,3],[[32,33,34],[31,32,33,34],[32]]]

"""
for each control point in the field, replace A and B leaf positions for the leaves we want to be at the x1 jaw. leaf jaw indices are 0-119.
0-59 are bank B, 60-119 are bank A. negative leaf position is X1, or bank B.  eclipse will show something different -> a leaf position will
be positive if the leaf is on its own side of the field.  units are in mm
"""

numFields = len(toChange[0])

#determine if jaw tracking is used.  if the second control point specifies jaw positions it will have the following value of 3.  our tbs with jt have leaf gap = 0.2, our novalis doesnt have jt and its min leaf gap is 0.5
if len(planFile.BeamSequence[0].ControlPointSequence[1].BeamLimitingDevicePositionSequence)==3:
        jawTracking = True
        minGap= 0.2
else:
        jawTracking= False 
        minGap= 0.5
fullGap = minGap+0.1


if not(jawTracking):
#for each field we want to change
    for i in range(numFields):
        fieldNum = toChange[0][i] -1
        #this is the x1 jaw position, we will move the leaves we want to move to this spot. neg is x1 direction, pos is x2 direction
        newPos = planFile.BeamSequence[fieldNum].ControlPointSequence[0].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0]
        numPairs = len(toChange[1][i])
        numCPs = len(planFile.BeamSequence[fieldNum].ControlPointSequence)
    
        #for each leaf pair that we want to change
        for j in range(numPairs):
            pairNum = toChange[1][i][j]-1
            #first control point only has 3 lists in beamlimitingdevicepositionsseqence positions in it, the rest have 1.  this is probably different for truebeams
            #for truebeams probably will need to find the most open position of the x1 jaw and put this there
            planFile.BeamSequence[fieldNum].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[pairNum] = newPos
            #other leaf is 60 incices offset from the other, and needs to be a distance equal to the arc or dose dynamic leaf tolerance away
            planFile.BeamSequence[fieldNum].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[pairNum+60] = newPos+fullGap
            for k in range(1,numCPs):
                planFile.BeamSequence[fieldNum].ControlPointSequence[k].BeamLimitingDevicePositionSequence[0].LeafJawPositions[pairNum] = newPos  #for jaw tracking use beamlimitingdevice...[2] like the 1st control point
                planFile.BeamSequence[fieldNum].ControlPointSequence[k].BeamLimitingDevicePositionSequence[0].LeafJawPositions[pairNum+60] = newPos+fullGap
    
    """
    so that last section closes user defined leaves
    now i want to close any leaves that just sit at the same position in the middle of the field
    """
    
    numBeams = len(planFile.BeamSequence)
    for i in range(numBeams):
        numCPs = len(planFile.BeamSequence[i].ControlPointSequence)
        changeArray = [0]*60
        #if all  cps have a pair of leaves at 0, close the leaves for all cps.  I round fractions of a mm to 0
        for k in range(60):
                x1 = np.round(planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k])
                x2 = np.round(planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k+60])
                if x1 !=0 and x2 != 0:
                    changeArray[k]=1            
    
        for j in range(1,numCPs):
            for k in range(60):
                x1 = np.round(planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[0].LeafJawPositions[k])
                x2 = np.round(planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[0].LeafJawPositions[k+60])
                if x1 !=0 and x2 != 0:
                    changeArray[k]=1
    
        newPos = planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0] ##for jaw tracking instead find the furthest x1 position (future version)           
        for k in range(60):
            if changeArray[k] == 0:            
                #newPos = planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0]
                planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k] = newPos
                planFile.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k+60] = newPos+fullGap
                for j in range(1,numCPs):
                    planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[0].LeafJawPositions[k] = newPos
                    planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[0].LeafJawPositions[k+60] = newPos+fullGap

elif jawTracking:
    for i in range(numFields):
        fieldNum = toChange[0][i] -1

        numPairs = len(toChange[1][i])
        numCPs = len(planFile.BeamSequence[fieldNum].ControlPointSequence)
        
        #need to find the minimum xjaw position and place the closed mlcs here
        minXArray = [0]*numCPs
        for k in range(numCPs):
            minXArray[k]=planFile.BeamSequence[fieldNum].ControlPointSequence[k].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0]
        newPos = np.min(minXArray)
        
        #for each leaf pair that we want to change
        for j in range(numPairs):
            pairNum = toChange[1][i][j]-1
            for k in range(numCPs):
                planFile.BeamSequence[fieldNum].ControlPointSequence[k].BeamLimitingDevicePositionSequence[2].LeafJawPositions[pairNum] = newPos  #for jaw tracking use beamlimitingdevice...[2] like the 1st control point
                planFile.BeamSequence[fieldNum].ControlPointSequence[k].BeamLimitingDevicePositionSequence[2].LeafJawPositions[pairNum+60] = newPos+fullGap
    
    """
    so that last section closes user defined leaves
    now i want to close any leaves that just sit at the same position in the middle of the field
    """
    
    numBeams = len(planFile.BeamSequence)
    for i in range(numBeams):
        numCPs = len(planFile.BeamSequence[i].ControlPointSequence)
        changeArray = [0]*60        
    
        for j in range(numCPs):
            for k in range(60):
                x1 = np.round(planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k])
                x2 = np.round(planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k+60])
                if x1 !=0 and x2 != 0:
                    changeArray[k]=1
        
        minXArray = [0]*numCPs
        for k in range(numCPs):
            minXArray[k]=planFile.BeamSequence[i].ControlPointSequence[k].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0]
        newPos = np.min(minXArray)
        
        for k in range(60):
            if changeArray[k] == 0:            
                for j in range(numCPs):
                    planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k] = newPos
                    planFile.BeamSequence[i].ControlPointSequence[j].BeamLimitingDevicePositionSequence[2].LeafJawPositions[k+60] = newPos+fullGap


planFile[0x20,0xe].value = str(random.randint(0,1000000000000000000000000000000))
planFile.StudyInstanceUID = str(random.randint(0,1000000000000000000000000000000))
planFile.SOPInstanceUID = str(random.randint(0,1000000000000000000000000000000))

planFile.SeriesDescription ="closedMLCs"+planFileName
planFile.RTPlanLabel = "closeMLCs"

savename = "closedMLCs"+planFileName
planFile.save_as(savename)