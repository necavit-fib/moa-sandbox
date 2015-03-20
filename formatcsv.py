#! /usr/bin/env python

from __future__ import print_function
import argparse
import os

def writeToFile(out, string):
	print(string, file=out)

def reformatRow(numbers):
	s = ''
	s += numbers[0] + '.' + numbers[1]
	s += ','
	s += numbers[2] + '.' + numbers[3]
	s += ','
	s += numbers[4] + '.' + numbers[5]
	return s

def reformatFile(file, outDir, suffix):
	o = outDir + '/' + os.path.basename(file.name) + '.' + suffix
	with open(o, 'wb') as outFile:
		lines = file.readlines()
		for i, row in enumerate(lines, 0):
			if i == 0:
				writeToFile(outFile, row.strip())
			else:
				numbers = row.strip().split(',')
				writeToFile(outFile, reformatRow(numbers))

def reformatFiles(files, outDir, suffix):
	for f in files:
		with open(f, 'rb') as file:
			reformatFile(file, outDir, suffix)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Reformats the moa-ppsm CSV evaluation files that were corrupted by Windows and its crappy locale settings.')
	parser.add_argument('-s', '--suffix', default='refmt',
						help='append this prefix to the output files')
	parser.add_argument('out_dir', help='the directory where the reformatted files will be output')
	parser.add_argument('files', nargs='+', help='the files to be reformatted')
	args = parser.parse_args()

	reformatFiles(args.files, args.out_dir, args.suffix)
