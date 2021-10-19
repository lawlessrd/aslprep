#!/usr/bin/python

'''
Inputs:
	-i: Filename of text file containing Exam Card info
	-s: List of asl scan names to search in exam card
	-f: List of associated filenames for nifti of each scan
Outputs:
	updated json sidecar for all ASL images in Exam Card
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

To do: test background suppression options, pasl, one with Save ASL set to 'ALL'

Test: python examcard2json.py -i ~/Documents/ASLPrep/examcard2txt/Kaczkurkin_20210201.txt -s pCASL,pCASL_M0

'''

import json
import os
import re
import sys, getopt


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

def main(argv):
	inputfile = ''
	scannames = ''
	try:
		opts, args = getopt.getopt(argv, "hi:s:f:",["input=","scans=","files="])
	except getopt.GetoptError:
		print ('examcard2json.py -i <input_examcard.txt> -s <scan1,scan2> -f <file1,file2>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('examcard2json.py -i <input_examcard.txt> -s <scan1,scan2> -f <file1,file2>')
			sys.exit()
		elif opt in ("-i", "--input"):
			inputfile = arg
		elif opt in ("-s", "--scans"):
			scannames = arg.split(',')
		elif opt in ("-f", "--files"):
			filenames = arg.split(',')
	print ('Exam card: ', inputfile)
	print ('Scans: ', scannames)
	print ('Files: ', filenames)

	# Set text lists for each ASL type
	on_json = ['MagneticFieldStrength', 'MRAcquisitionType','EchoTime','FlipAngle']

	asl_requirements = ['Slices','SliceTiming','LookLocker','RepetitionTimePreparation',
						 'Arterial Spin labeling', 'label delay',
						'back. supp.','M0Type', 'TotalAcquiredPairs']
	
	pcasl_requirements = ['label duration']

	pasl_requirements = ['BolusCutOffFlag','BolusCutOffDelayTime','BolusCutOffTechnique']

	m0scan_requirements = ['RepetitionTimePreparation','IntendedFor']


	#Get scans from start of file

	for scan in scannames:
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
			

			# If ASL type is 'NO', then scan is m0
			if asl_type == 'NO':
				print('\tASL type: M0 scan')
				# Get file name for non-m0 scan to set as 'IntendedFor'
				for file in filenames:
					if file.find('m0') == -1 & file.find('M0') == -1:
						IntendedFor = file
						print('\tM0 intended for: ', file)									
			else:
				print('\tASL type:',asl_type)
				
				# Set M0 type
				if any('m0' or 'M0' in s for s in scannames):
					M0_type = 'Separate'
				else:
					M0_type = 'Absent'
				
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

				# Parse exam card for label delay
				search_tmp = search_string_in_file(inputfile,'label delay',start_line)
				tmp = search_tmp[0][1].split(':')
				label_delay = int(tmp[-1].strip())/1000
				print('\tLabel delay:',label_delay, 'sec')
			
			if asl_type == 'pCASL' or 'CASL':
				# Parse exam card for background suppression
				search_tmp = search_string_in_file(inputfile,'label duration',start_line)
				tmp = search_tmp[0][1].split(':')
				label_duration = int(tmp[-1].strip())/1000
				print('\tLabel duration:',label_duration, 'sec')

			if asl_type == 'pASL':
				# Parse exam card for background suppression
				search_tmp = search_string_in_file(inputfile,'BolusCutOffFlag',start_line)
				tmp = search_tmp[0][1].split(':')
				bolus = tmp[-1].strip()
				print('\tBolus Cut Off Flag:',bolus)
		else:
			print(scan,' not found. Please repeat with correct scan name.')
			sys.exit()


if __name__ == '__main__':
	main(sys.argv[1:])