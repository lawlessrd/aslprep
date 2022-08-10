#!/usr/bin/python

'''
Inputs:
	-i: Filename of text file containing Exam Card info
	-s: List of asl scan names to search in exam card
	-b: BIDS file structure containing nifti files and json sidecars
Outputs:
	updated json sidecar for ASL images in Exam Card
		Name: sub-01_ses-01_asl.json OR sub-01_ses-01_m0scan.json

Required inputs for json sidecar
ASL general metadata fields:
	MagneticFieldStrength
	MRAcquisitionType (2D or 3D)
	EchoTime
	If MRAcquisitionType definied as 2D:
		SliceTiming
	If LookLocker is True:
		RepetitionTimePreparation
		FlipAngle
	ArterialSpinLabelingType (CASL, PCASL, PASL)
	PostLabelingDelay (in seconds) (0 for m0scans)
	BackgroundSuppression
	M0Type
	TotalAcquiredPairs

(P)CASL specific metadata fields:
	LabelingDuration (0 for m0scans)	

PASL specific metadata fields:
	BolusCutOffFlag (boolean)
	If BolusCutOffFlag is True:
		BolusCutOffDelayTime
		BolusCutOffTechnique

m0scan metadata fields:
	EchoTime
	RepetitionTimePreparation
	If LookLocker is True:
		FlipAngle
	IntendedFor (string with associated ASL image filename)

Units of time should always be seconds.

'''

from __future__ import print_function
import json
import re
import sys, getopt
import glob
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def search_string_in_file(file_name, string_to_search, starting_line):
	"""
	Search for given string in file starting at provided line number
	and return the first line containing that string,
	along with line numbers.
	:param file_name: name of text file to scrub
	:param string_to_search: string of text to search for in file
	:param starting_line: line at which search starts
	"""
	line_number = 0
	list_of_results = []
	# Open file in read only mode
	with open(file_name, 'r') as read_obj:
		# Read all lines one by one
		for line in read_obj:
			line_number += 1
			if line_number < starting_line:
				continue
			else:
				line = line.rstrip()
				if re.search(r"{}".format(string_to_search),line):
					# If yes add the line number & line as a tuple in the list
					list_of_results.append((line_number,line.rstrip()))
	#Return list of tuples containing line numbers and lines where string is found
	return list_of_results

def modify_json(json_file, s_dict):
	"""
	Add contents of s_dict to .json file
	:param json_file: name of json file
	:param s_dict: dictionary of info to add to .json file
	"""
	if json_file:
		with open(json_file, 'r') as f:
			json_contents = json.load(f)
			json_contents.update(s_dict)
			f.close
		with open(json_file, 'w') as f:
			json.dump(json_contents,f,indent = 4,cls=NumpyEncoder)
			f.close
		print('Added exam card information to',json_file)
	else:
		print('Files not found or data is not in BIDS format. Please repeat with correct file/structure.')
		sys.exit()

def main(argv):
	indir = ''
	scannames = ''
	bids = ''
	inputfile= ''
	try:
		opts, args = getopt.getopt(argv, "hi:b:e:",["input=","bids=","examcard="])
	except getopt.GetoptError:
		print('examcard2json.py -i <indir> -b <folder> -e <examcard.txt>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('examcard2json.py -i <indir> -b <folder> -e <examcard.txt>')
			sys.exit()
		elif opt in ("-i", "--input"):
			indir = arg
		elif opt in ("-b", "--bids"):
			bids = arg
		elif opt in ("-e","--examcard"):
			inputfile = arg


	#Initialize dictionaries
	scan_dict = {}
	
	#Get scans from SeriesDescription.json
	with open(indir + '/SeriesDescription.json','r') as infile:
		scannames = json.load(infile)

	for scan in scannames.values():

		scan_dict[scan] = {}

		print('\nStarting scan:', scan)
		find_scans = search_string_in_file(inputfile,scan,0)
		# Find start of scan section
		string_to_search = 'Protocol Name:  ' + scan
		if find_scans:
			for line in find_scans:
				for num in line:
					if re.search(r"\b{}\b".format(string_to_search),str(num)):
						start_line = line[0]
			search_tmp = search_string_in_file(inputfile,'Arterial Spin labeling',start_line)	
			tmp = search_tmp[0][1].split(':')
			asl_type = tmp[-1].strip()

			# set repetiion time prep until better method found
			scan_dict[scan]["RepetitionTimePreparation"] = 0
			print('\tRepetition Time Preparation:',str(0), 'sec')

			# If ASL type is 'NO', then scan is m0
			if asl_type == 'NO':
				print('\tASL type: M0 scan')
				# Get file name for non-m0 scan to set as 'IntendedFor'
				for s in scannames:
					if s.find('m0') == -1 & s.find('M0') == -1:
						for nii_file in glob.glob(bids + '/sub-*/ses-*/perf/*.nii.gz'):
							if nii_file.find('m0') == -1 & nii_file.find('M0') == -1:
								asl_nii = nii_file.split('/')
								IntendedFor = '/'.join(asl_nii[-3:])
								print('\tM0 intended for: ',IntendedFor)
								scan_dict[scan]["IntendedFor"] = IntendedFor	
				
				# Parse examcard for AcquisitionVoxelSize
				acq_vox_size = []
				search_tmp = search_string_in_file(inputfile,'ACQ voxel size',start_line)
				tmp = search_tmp[0][1].split(':')
				acq_vox_size.append(float(tmp[-1].strip()))
				tmp = search_tmp[1][1].split(':')
				acq_vox_size.append(float(tmp[-1].strip()))

				search_tmp = search_string_in_file(inputfile,'Slice thickness',start_line)
				tmp = search_tmp[0][1].split(':')
				acq_vox_size.append(float(tmp[-1].strip()))

				print('\tAcquisitionVoxelSize:', acq_vox_size, 'mm')
				scan_dict[scan]["AcquisitionVoxelSize"] = acq_vox_size


				# Add exam card info to m0 json
				json_file = glob.glob(bids+'/sub-*/ses-*/perf/*m0scan.json')
				modify_json(json_file[0],scan_dict[scan])

			else:
				print('\tASL type:',asl_type)
				scan_dict[scan]["ArterialSpinLabelingType"] = asl_type.upper()
				# Set M0 type
				if any('m0' or 'M0' in s for s in scannames):
					M0_type = 'Separate'
				else:
					M0_type = 'Absent'
				
				scan_dict[scan]["M0Type"] = M0_type

				print('\tM0 type:',M0_type)
				
				# Parse exam card for background suppression
				search_tmp = search_string_in_file(inputfile,'back. supp.',start_line)
				tmp = search_tmp[0][1].split(':')
				back_supp = tmp[-1].strip()
				if back_supp == 'NO':
					back_supp = False
				else:
					back_supp = True
				print('\tBackground Suppression:', back_supp)
				scan_dict[scan]["BackgroundSuppression"] = back_supp

				# Parse exam card for label delay
				search_tmp = search_string_in_file(inputfile,'label delay',start_line)
				tmp = search_tmp[0][1].split(':')
				label_delay = float(tmp[-1].strip())/1000
				print('\tLabel delay:',label_delay, 'sec')
				scan_dict[scan]["PostLabelingDelay"] = label_delay

				# Parse exam card for TR and nSlices to generate slice timing
				search_tmp = search_string_in_file(inputfile,'Slices',start_line)
				tmp = search_tmp[0][1].split(':')
				n_slices = int(tmp[-1].strip())
				
				search_tmp = search_string_in_file(inputfile,'TR ',start_line)
				tmp = search_tmp[0][1].split(':')
				if tmp[-1].strip() == 'USER_DEF':
					search_tmp = search_string_in_file(inputfile,'(ms)',search_tmp[0][0])
					tmp = search_tmp[0][1].split(':')
					tr = float(tmp[-1].strip())/1000
				else:
					tr = float(tmp[-1].strip())/1000
				
				# calculate slice timing
				ta = tr/n_slices
				slice_timing = np.linspace(0,tr-ta,n_slices) #ascending

				# If slice order is descending, flip the slice timing list
				search_tmp = search_string_in_file(inputfile,'Slice scan order',start_line)
				tmp = search_tmp[0][1].split(':')
				if tmp[-1].strip() == 'DESCEND':
					slice_timing = slice_timing.reverse()

				print('\tSlice timing:',slice_timing, 'sec')
				scan_dict[scan]["SliceTiming"] = slice_timing.tolist()

				if asl_type == 'pCASL' or 'CASL' or 'PCASL':
					# Parse exam card for background suppression
					search_tmp = search_string_in_file(inputfile,'label duration',start_line)
					if not search_tmp:
						search_tmp = search_string_in_file(inputfile,'EX_FLL_casl_dur',start_line)
					tmp = search_tmp[0][1].split(':')
					label_duration = float(tmp[-1].strip())/1000
					print('\tLabeling duration:',label_duration, 'sec')
					scan_dict[scan]["LabelingDuration"] = label_duration

					# Parse examcard for Background Suppression Pulses
					search_tmp = search_string_in_file(inputfile,'back. supp. pulses',start_line)
					tmp = search_tmp[0][1].split(':')
					back_supp_pulses_str = tmp[-1].strip()

					back_supp_pulses = list(back_supp_pulses_str.split(" "))

					back_supp_list = [float(x)/1000 for x in back_supp_pulses]
					back_supp_num_pulses = len(back_supp_list)

					print('\tBackground Suppression Pulses:', back_supp_list, 'sec')
					print('\tNumber of Background Suppression Pulses:', back_supp_num_pulses)
					scan_dict[scan]["BackgroundSuppressionPulseTime"] = back_supp_list
					scan_dict[scan]["BackgroundSuppressionNumberPulses"] = back_supp_num_pulses

					# Parse examcard for label distance
					search_tmp = search_string_in_file(inputfile,'label distance',start_line)
					tmp = search_tmp[0][1].split(':')
					label_distance = tmp[-1].strip()
					print('\tLabel Distance:', label_distance, 'mm')
					scan_dict[scan]["LabelDistance"] = label_distance

					# Parse examcard for AcquisitionVoxelSize
					acq_vox_size = []
					search_tmp = search_string_in_file(inputfile,'ACQ voxel size',start_line)
					tmp = search_tmp[0][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))
					tmp = search_tmp[1][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))

					search_tmp = search_string_in_file(inputfile,'Slice thickness',start_line)
					tmp = search_tmp[0][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))

					print('\tAcquisitionVoxelSize:', acq_vox_size, 'mm')
					scan_dict[scan]["AcquisitionVoxelSize"] = acq_vox_size

					# Parse examcard for Vascular crushing
					search_tmp = search_string_in_file(inputfile,'vascular crushing',start_line)
					tmp = search_tmp[0][1].split(':')
					vasc_crush = tmp[-1].strip()
					if vasc_crush == 'NO':
						vasc_crush = False
					else:
						vasc_crush = True
					print('\tVascular crushing:', vasc_crush)
					scan_dict[scan]["VascularCrushing"] = vasc_crush


				if asl_type == 'pASL':
					# Parse exam card for background suppression
					#search_tmp = search_string_in_file(inputfile,'BolusCutOffFlag',start_line)
					#tmp = search_tmp[0][1].split(':')
					#bolus = tmp[-1].strip()
					#print('\tBolus Cut Off Flag:',bolus)
					scan_dict[scan]["BolusCutOffFlag"] = False

					# Parse exam card for background suppression
					search_tmp = search_string_in_file(inputfile,'label duration',start_line)
					if not search_tmp:
						search_tmp = search_string_in_file(inputfile,'EX_FLL_casl_dur',start_line)
					tmp = search_tmp[0][1].split(':')
					label_duration = float(tmp[-1].strip())/1000
					print('\tLabeling duration:',label_duration, 'sec')
					scan_dict[scan]["LabelingDuration"] = label_duration

					# Parse examcard for Background Suppression Pulses
					search_tmp = search_string_in_file(inputfile,'back. supp. pulses',start_line)
					tmp = search_tmp[0][1].split(':')
					back_supp_pulses_str = tmp[-1].strip()

					back_supp_pulses = list(back_supp_pulses_str.split(" "))

					back_supp_list = [float(x)/1000 for x in back_supp_pulses]
					back_supp_num_pulses = len(back_supp_list)

					print('\tBackground Suppression Pulses:', back_supp_list, 'sec')
					print('\tNumber of Background Suppression Pulses:', back_supp_num_pulses)
					scan_dict[scan]["BackgroundSuppressionPulseTime"] = back_supp_list
					scan_dict[scan]["BackgroundSuppressionNumberPulses"] = back_supp_num_pulses

					# Parse examcard for label distance
					search_tmp = search_string_in_file(inputfile,'label distance',start_line)
					tmp = search_tmp[0][1].split(':')
					label_distance = tmp[-1].strip()
					print('\tLabel Distance:', label_distance, 'mm')
					scan_dict[scan]["LabelDistance"] = label_distance

					# Parse examcard for AcquisitionVoxelSize
					acq_vox_size = []
					search_tmp = search_string_in_file(inputfile,'ACQ voxel size',start_line)
					tmp = search_tmp[0][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))
					tmp = search_tmp[1][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))

					search_tmp = search_string_in_file(inputfile,'Slice thickness',start_line)
					tmp = search_tmp[0][1].split(':')
					acq_vox_size.append(float(tmp[-1].strip()))

					print('\tAcquisitionVoxelSize:', acq_vox_size, 'mm')
					scan_dict[scan]["AcquisitionVoxelSize"] = acq_vox_size

					# Parse examcard for Vascular crushing
					search_tmp = search_string_in_file(inputfile,'vascular crushing',start_line)
					tmp = search_tmp[0][1].split(':')
					vasc_crush = tmp[-1].strip()
					if vasc_crush == 'NO':
						vasc_crush = False
					else:
						vasc_crush = True
					print('\tVascular crushing:', vasc_crush)
					scan_dict[scan]["VascularCrushing"] = vasc_crush

				# Add exam card info to asl json
				json_file = glob.glob(bids+'/sub-*/ses-*/perf/*asl.json')
				modify_json(json_file[0],scan_dict[scan])
		else:
			print(scan,' not found. Please repeat with correct scan name.')
			sys.exit()


if __name__ == '__main__':
	main(sys.argv[1:])