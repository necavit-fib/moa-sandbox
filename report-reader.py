#! /usr/bin/env python

import argparse
import os
from subprocess import call
from termcolor import colored
from collections import namedtuple
import csv
import re
from filtermappings import getFilterName

alpha = re.compile('[a-zA-Z]*')
decimal = re.compile('\d+.\d+')
number = re.compile('\d+')

Param = namedtuple('Param', 'name value')

def parseParams(paramsString):
	params = []
	chunks = paramsString.split('-')
	for chunk in chunks[1:len(chunks)]:
		name = re.match(alpha, chunk).group(0)
		match = re.search(decimal, chunk)
		if match:
			value = float(match.group(0))
		else:
			value = int(re.search(number, chunk).group(0))
		param = Param(name=name, value=value)
		params.append(param)
	return params

def parseParamsFromFile(file):
    basename = os.path.basename(file.name)
    return parseParams(basename.split('_')[0])

def parseMethodFromFile(file):
	basename = os.path.basename(file.name)
	methodCode = basename.split('_')[0].split('-')[0]
	return getFilterName(methodCode)

def parseStreamFromFile(file):
	basename = os.path.basename(file.name)
	return basename.split('_')[1].split('-')[0]

def parseInstancesFromFile(file):
	basename = os.path.splitext(file.name)[0]
	return basename.split('_')[1].split('-')[1]

def parseDisclosureRiskFromFile(file):
	'''
	Total disclosure risk:  0.957178000000
	'''
	file.seek(0)
	match = re.search(r'Total\sdisclosure\srisk:\s\s(\d+.\d+)', file.read())
	if match:
		return match.group(1)
	else:
		raise NameError('No disclosure risk measure was found in file ' + file.name)

def parseInformationLossFromFile(file):
	'''
	Total information loss: 11247.654446313676
	'''
	file.seek(0)
	match = re.search(r'Total\sinformation\sloss:\s(\d+.\d+)', file.read())
	if match:
		return match.group(1)
	else:
		raise NameError('No information loss measure was found in file ' + file.name)

def getCSVHeader(params):
	paramsHeader = ''
	for param in params:
		paramsHeader += param.name + ','
	header = 'method,stream,instances,' + paramsHeader + 'disclosureRisk,informationLoss'
	return header

def getCsvLine(method, stream, instances, params, discRisk, infoLoss):
	line = method + ',' + stream + ',' + instances + ','
	for param in params:
		line += str(param.value) + ','
	line += discRisk + ',' + infoLoss
	return line

def readReports(args):
	out = args.out_file
	for i, report in enumerate(args.report_files, 0):
		# data acquisition:
		method = parseMethodFromFile(report)
		stream = parseStreamFromFile(report)
		instances = parseInstancesFromFile(report)
		params = parseParamsFromFile(report)
		discRisk = parseDisclosureRiskFromFile(report).replace(',','.')
		infoLoss = parseInformationLossFromFile(report).replace(',','.')

		# write to CSV:
		if i == 0:
			header = getCSVHeader(params)
			out.write(header + '\n')
		csvLine = getCsvLine(method, stream, instances, params, discRisk, infoLoss)
		out.write(csvLine+'\n')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
						description='Reads a list of MOA dumped reports, parses their content and outputs'+
									' a CSV file with the result.')
	parser.add_argument('-r', '--report-files', nargs='+', type=argparse.FileType('r'), required=True,
						help='the dumped, plain-text, MOA report files to be read')
	parser.add_argument('-o', '--out-file', type=argparse.FileType('w'), required=True,
						help='the CSV file to which the results will be saved')
	args = parser.parse_args()

	# main procedure
	readReports(args)
