# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a file to make MLC treatment files with an MLC offset to test DLG/spot size in a TPS.
Andrew Morrow dec 7 2021
"""
dlgoffset=0.05
offset = dlgoffset/2  #offset per leaf
templatefile = r"K:\Physics Division\Therapy\Functions\External Beam\9. Treatment Planning System\DLG\MLC DLG files 12 7 21\2mm 0DLG.mlc"
outfile = r"K:\Physics Division\Therapy\Functions\External Beam\9. Treatment Planning System\DLG\MLC DLG files 12 7 21\0.05.mlc"
filein = open(templatefile,'r')
fileout = open(outfile,'w')
lines = filein.readlines()
linestowrite =[]
for line in lines:
    templine = line
    if line.find(" =  -") != -1:
        val = '%.3f'%(float(templine[11:-1])+offset)
        templine = templine[:12]+val+templine[18:]
    elif line.find(" =   ") != -1:
        val = '%.3f'%(float(templine[11:-1])+offset)
        templine = templine[:13]+val+templine[18:]
    linestowrite.append(templine)  
fileout.writelines(linestowrite)
filein.close()
fileout.close()