#! /usr/bin/env python

import argparse
import os
from subprocess import call
from termcolor import colored

def executeMOATask(reportFile, outDir):
	basename = os.path.splitext(os.path.basename(reportFile.name))[0]
	outFile = outDir + '/' + basename + '.txt'
	cmdFormat = {
		'report': reportFile.name,
		'out': outFile
	}
	cmd = './moa.sh "ReadAnonymizationReport -r %(report)s" > %(out)s' % cmdFormat
	print colored('[RUNNING]', 'green'), 'Executing:', cmd
	call(cmd, shell=True)

def dumpReportsWithArgs(args):
	for file in args.report_files:
		executeMOATask(file, args.out_dir)

if __name__ == '__main__':
	# argument parsing
	parser = argparse.ArgumentParser(
						description='Executes MOA to read anonymization reports and dump them in the'+
									' specified directory.')
	parser.add_argument('-r', '--report-files', nargs='+', type=argparse.FileType('r'), required=True,
						help='the MOA report files to be read')
	parser.add_argument('-o', '--out-dir', required=True,
						help='the directory where the dumped report will be written')
	args = parser.parse_args()

	# main procedure
	dumpReportsWithArgs(args)
