# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 10:45:20 2021

@author: anmorrow
"""
import pydicom
import random
import os

mypath = r"K:\Physics Division\Therapy\Functions\External Beam\7. IMRT & Rapid Arc QA Measurements\2021\12. December"
os.chdir(mypath)
planFileName = "RP.panc.dcm"
planFile = pydicom.dcmread(planFileName)
dlgoffset=0.35#in mm!
offset = dlgoffset/2  #offset per leaf

#determine if jaw tracking is used.  if the second control point specifies jaw positions it will have the following value of 3.  our tbs with jt have leaf gap = 0.2, our novalis doesnt have jt and its min leaf gap is 0.5
if len(planFile.BeamSequence[0].ControlPointSequence[1].BeamLimitingDevicePositionSequence)==3:
        jawTracking = True
else:
        jawTracking= False 
        
if not(jawTracking):
#for each field we want to change
    for beam in range(len(planFile.BeamSequence)):
        for leaf in range(60):#120 leaves in 2 banks.  first control point without jaw tracking has 3 BLDPSs, rest have 1
            planFile.BeamSequence[beam].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[leaf] -= offset
            planFile.BeamSequence[beam].ControlPointSequence[0].BeamLimitingDevicePositionSequence[2].LeafJawPositions[leaf+60] += offset
        for cp in range(1,len(planFile.BeamSequence[beam].ControlPointSequence)):
            for leaf in range(60):#120 leaves
                planFile.BeamSequence[beam].ControlPointSequence[cp].BeamLimitingDevicePositionSequence[0].LeafJawPositions[leaf] -= offset
                planFile.BeamSequence[beam].ControlPointSequence[cp].BeamLimitingDevicePositionSequence[0].LeafJawPositions[leaf+60] += offset

elif jawTracking:
    for beam in range(len(planFile.BeamSequence)):
        for cp in range(len(planFile.BeamSequence[beam].ControlPointSequence)):
            for leaf in range(60):#120 leaves
                planFile.BeamSequence[beam].ControlPointSequence[cp].BeamLimitingDevicePositionSequence[2].LeafJawPositions[leaf] -= offset
                planFile.BeamSequence[beam].ControlPointSequence[cp].BeamLimitingDevicePositionSequence[2].LeafJawPositions[leaf+60] += offset
                
planFile[0x20,0xe].value = str(random.randint(0,1000000000000000000000000000000))
planFile.StudyInstanceUID = str(random.randint(0,1000000000000000000000000000000))
planFile.SOPInstanceUID = str(random.randint(0,1000000000000000000000000000000))

planFile.SeriesDescription =str(dlgoffset)+planFileName
planFile.RTPlanLabel = str(dlgoffset)+planFileName

savename = str(dlgoffset)+planFileName
planFile.save_as(savename)