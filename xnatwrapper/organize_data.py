#!/usr/bin/env python

# Script for organizing ASL data to BIDS format
# Pull scan name from asl and m0 image, NEED TO DO: output to examcard2json
# Remove asl image (or just don't put it in the BIDS folder?)
# Convert dicom to nifti

import glob
import os
import sys, getopt
from pydicom import dcmread
import json

def main(argv):
	indir = ''
	try:
		opts, args = getopt.getopt(argv, "hi:a:m:s:p:",["indir=","asl=","m0=","source="])
	except getopt.GetoptError:
		print('organize_data.py')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('organize_data.py')
			sys.exit()
		elif opt in ("-i", "--indir"):
			indir = arg
		elif opt in ("-a", "--asl"):
			asl = arg
		elif opt in ("-m", "--m0"):
			m0 = arg
		elif opt in ("-s", "--source"):
			source = arg
	
	# set T1
	t1w=indir + '/T1.dcm'

	# check if file paths are absolute
	if os.path.isabs(asl) == False:
		asl = indir + '/' + asl
		m0 = indir + '/' + m0
		source = indir + '/' + source

	# get pydicom info for each scan
	ds_asl = dcmread(asl)
	ds_m0 = dcmread(m0)
	ds_t1w = dcmread(t1w)
	ds_source = dcmread(source)

	# pull scan name from dicom header
	scanname = {}
	scanname['asl'] = ds_asl.SeriesDescription
	scanname['m0'] = ds_m0.SeriesDescription

	# write scanname dict to json
	with open('SeriesDescription.json','w') as outfile:
		json.dump(scanname,outfile)

	# move scans to BIDS directories
	os.system('mkdir -p ' + indir + '/BIDS/sub-01/ses-01/anat/')
	os.system('mkdir -p ' + indir + '/BIDS/sub-01/ses-01/perf/')

	os.system('cp ' + source + ' ' + indir + '/BIDS/sub-01/ses-01/perf/' + os.path.basename(source))
	os.system('cp ' + m0 + ' ' + indir + '/BIDS/sub-01/ses-01/perf/' + os.path.basename(m0))
	os.system('cp ' + t1w + ' ' + indir + '/BIDS/sub-01/ses-01/anat/' + os.path.basename(t1w))

	# run dcm2niix on source and m0 scans
	os.system('dcm2niix -f %b ' + indir + '/BIDS/sub-01/ses-01/anat')
	os.system('dcm2niix -f %b ' + indir + '/BIDS/sub-01/ses-01/perf')

	# remove leftover dicoms
	for file in glob.glob(indir + '/BIDS/sub-01/ses-01/*/*'):
		if file.endswith('.dcm'):
			os.system('rm ' + file)

	# rename nii/json files to match bids formatting
	
	#ds_t1w.SeriesDescription = ds_t1w.SeriesDescription.replace(" ","").replace('/', "").replace(":", "").replace("_", "")
	#ds_asl.SeriesDescription = ds_asl.SeriesDescription.replace(" ","").replace('/', "").replace(":", "").replace("_", "")
	#ds_m0.SeriesDescription = ds_m0.SeriesDescription.replace(" ","").replace('/', "").replace(":", "").replace("_", "")

	anat_rename = 'sub-01_ses-01_T1w'
	for file in glob.glob(indir + '/BIDS/sub-01/ses-01/anat/*'):
		if file.endswith('.json'):
			os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + anat_rename + '.json')
		else:
			os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + anat_rename + '.nii')
			os.system('gzip ' + os.path.dirname(file) + '/' + anat_rename + '.nii')

	asl_rename = 'sub-01_ses-01_asl'
	m0_rename = 'sub-01_ses-01__m0scan'
	for file in glob.glob(indir + '/BIDS/sub-01/ses-01/perf/*'):
		if 'M0' in file:
			if file.endswith('.json'):
				os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + m0_rename + '.json')
			else:
				os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + m0_rename + '.nii')
				os.system('gzip ' + os.path.dirname(file) + '/' + m0_rename + '.nii')
		else:
			if file.endswith('.json'):
				os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + asl_rename + '.json')
			else:
				os.system('mv ' + file + ' ' + os.path.dirname(file) + '/' + asl_rename + '.nii')
				os.system('gzip ' + os.path.dirname(file) + '/' + asl_rename + '.nii')
	
	# create dataset_description.json
	dataset_description = {
	  "BIDSVersion": "1.0.1",
	  "Name": "XNAT Project",
  	  "DatasetDOI": "https://xnat2.vanderbilt.edu/xnat",
  	  "Author": "No Author defined on XNAT"
	  }
	
	with open(indir + '/BIDS/dataset_description.json','w') as outfile:
		json.dump(dataset_description,outfile)


if __name__ == '__main__':
	main(sys.argv[1:])
