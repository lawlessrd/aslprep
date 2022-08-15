#!/usr/bin/env python

'''
Inputs:
	-b: BIDS file structure containing nifti files and json sidecars
Outputs:
	updated json sidecar for ASL images in Exam Card
		Name: sub-01_ses-01_asl.json OR sub-01_ses-01_m0scan.json


'''
from __future__ import print_function
import os
import csv
import sys, getopt
import glob
import nibabel as nib

def main(argv):
	bids = ''
	try:
		opts, args = getopt.getopt(argv, "hb:",["bids="])
	except getopt.GetoptError:
		print('create_tsv.py -b <folder>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('create_tsv.py -b <folder>')
			sys.exit()
		elif opt in ("-b", "--bids"):
			bids = arg

	print('BIDS Folder: ', bids)

	asl_file = glob.glob(bids+'/sub-*/ses-*/perf/*_asl.nii.gz')

	if asl_file:
		asl_img = nib.load(asl_file[0])
		if len(asl_img.shape) < 4:
			print('ASL data not 4-dimensional. Please repeat with correct file.')
			sys.exit()
		else:
			abs_path = os.path.abspath(asl_file[0])
			file_struct = abs_path.split('/')
			tsv_loc = '/'.join(file_struct[:-1]) + ''
			name_struct = file_struct[-1].split('_')
			tsv_name = '_'.join(name_struct[:-1]) + '_aslcontext.tsv'

			with open(tsv_loc + '/' + tsv_name,'wt') as tsv_file:
				csv_writer=csv.writer(tsv_file,delimiter='\t')
				csv_writer.writerow(['volume_type'])
				for x in range(asl_img.shape[3]):
					if (x % 2) == 0:
						csv_writer.writerow(['control'])
					else:
						csv_writer.writerow(['label'])

	else:
		print('Files not found or data is not in BIDS format. Please repeat with correct file/structure.')
		sys.exit()

if __name__ == '__main__':
	main(sys.argv[1:])