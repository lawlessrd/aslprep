#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from __future__ import print_function
import glob,sys,getopt
from weasyprint import HTML,CSS


def main(argv):
	out_dir = ''
	try:
		opts, args = getopt.getopt(argv, "ho:p:s:c",["out_dir=","project=","subject=","session="])
	except getopt.GetoptError:
		print('html2pdf.py -o <folder> --project <project> --subject <subject> --session <session>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('html2pdf.py -o <folder> --project <project> --subject <subject> --session <session>')
			sys.exit()
		elif opt in ("-o", "--out_dir"):
			out_dir = arg
        elif opt in ("-p", "--project"):
            project = arg
        elif opt in ("-s", "--subject"):
            subject = arg
        elif opt in ("-c", "--session"):
            session = arg
	
	print('Output Folder: ', out_dir)

	html_out = glob.glob(out_dir + '/aslprep/sub-*.html')

	for x in html_out:
		with open(x,"r") as file:
			file_data = file.readlines()
		first_line=[]
		last_line=[]
		line_number = 0
		# locate and remove ratings widget
		for line in file_data:
			line_number += 1
			if '<div id="boilerplate">' in line:
				first_line.append((line_number))
			if '<div id="errors">' in line:
				last_line.append((line_number-1))
		#add in first and last line variables
		parsed_data = file_data[:first_line[0]]+file_data[last_line[0]:]
		html = ''
		for i in parsed_data:
			html += i
		#Apply html to pdf conversion
		HTML(string=html).write_pdf(project + '_' + subject + '_' + session +'_aslprep_QA.pdf',stylesheets=[CSS(string='body { font-family: !important }')])

if __name__ == '__main__':
	main(sys.argv[1:])
