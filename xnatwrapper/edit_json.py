import os
import sys
import json
import glob
import pandas as pd
import pydicom
from pydicom import dcmread, Dataset


### CHANGE TO READING JSON SIDECAR INSTEAD OF DICOM ###
ds = dcmread("1.3.46.670589.11.45051.5.0.3184.2021020414012097000-501-1-zuxjau.dcm")

# Need: type of asl imaging (ASL,CASL,pCASL)
# split series description tag from DICOM header and check
series_desc = ds[0x08,0x103e].value.split('_')

if 'm0' or 'M0' in series_desc:
	scan_type = 'm0scan'
elif 'ASL' in series_desc:
	scan_type = 'ASL'
elif 'CASL' in series_desc: 
	scan_type = 'CASL'
elif 'pCASL' in series_desc:
	scan_type = 'pCASL'
else:
	print('Incorrect scan type. Please repeat with perfusion imaging data.')

# Check for 4th dimension of ASL data
data = ds.pixel_array

#if data.ndim == 3
# data only has 3 dimensions, so it must be 

## Get required info from dicom header ##
# MagneticFieldStrength,
mr_field = ds[0x18,0x0087].value

#MRAcquisitionType, 
mr_acq_type = ds[0x18,0x0023].value

#EchoTime, 
TE = ds[0x18,0x81].value

# SliceTiming in case MRAcquisitionType is defined as 2D,
# SliceTiming is not reported on Philips DICOM headers, so we must manually calculate 

# No TR stored in DICOM
#if mr_acq_type == '2D'
#	TR = ds[0x0018,0x0080].value
#	n_slices
#	TA = TR/nSlices
#	slice_timing = [0:TA:TR-TA] #ascending
	

# RepetitionTimePreparation, and FlipAngle in case LookLocker is true
# unsure if LookLocker is used, so only grabbing FA for now
FA = ds[0x18,0x1314].value


#PostLabelingDelay
#BackgroundSuppresion
#M0Type
#Total Acquired Pairs
#VascularCrushing
#AcquisitionVoxelSize
#BackgroundSuppresionNumberPulses
#Background suppression Pulse Time

## IF TYPE IS pCASL
#LabelingDuration
#pCASLType

## For M0 scan
# Echo time
# REpetitionTimePreparation
#Flip Angle
#intendedFor
#AcquisitionVoxelSize
