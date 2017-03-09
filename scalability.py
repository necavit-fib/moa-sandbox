#!/usr/bin/env python

import argparse
from filtermappings import getFilterCode
import itertools
import json
import os
import re
from subprocess import call
import sys
from termcolor import colored
import textwrap

# global flags
dryRun = False

def getCodedFilterSpec(filterSpec):
	filterComponents = filterSpec.split(' ')
	filterName = filterComponents[0]
	filterParams = ''.join(filterComponents[1:len(filterComponents)])
	return getFilterCode(filterName) + filterParams

def getBaseFilename(stream, filterSpec, instances):
	streamName = stream.split('.')[1]
	codedFilterSpec = getCodedFilterSpec(filterSpec)
	return codedFilterSpec + '_' + streamName # no instances (concatenate!)

def getFile(outDir, baseFilename, extension):
	return outDir + '/' + baseFilename + '.' + extension

def getTaskOptions(options, filterSpec, stream, instances):
	optionsSpec = ''
	baseFilename = getBaseFilename(stream,filterSpec, instances)

	# instances to anonymize
	optionsSpec += '-m ' + instances + ' '

	# task report
	reportOptions = options['report']
	if reportOptions['summarizeReport'] or scalability:
		optionsSpec += '-z '
	if reportOptions['writeTaskReport']:
		file = getFile(reportOptions['taskReportDirectory'], baseFilename, 'txt')
		optionsSpec += '-r ' + file + ' '

	# throughput
	throughputOptions = options['throughput']
	if throughputOptions['writeThroughput']:
		file = getFile(throughputOptions['throughputDirectory'], baseFilename, 'csv')
		optionsSpec += '-t ' + file + ' '
		optionsSpec += '-U ' + str(throughputOptions['throughputUpdateRate']) + ' '

	return optionsSpec

def anonymizeStream(stream, privacyFilter, instances, options):
	# build the command line call
	cmdFormat = {
		'scalability': '-e' if scalability else '',
		'stream': '(%s)' % stream,
		'filter': '(%s)' % privacyFilter,
		'taskOpts': getTaskOptions(options, privacyFilter, stream, instances)
	}
	cmd = './moa.sh %(scalability)s "Anonymize -s %(stream)s -f %(filter)s %(taskOpts)s"' % cmdFormat

	# add the necessary redirection for scalability experiment execution
	if scalability:
		global firstTimeScalability
		scalabilityFile = getFile(options['scalabilityDirectory'], getBaseFilename(stream, privacyFilter, instances), 'csv')
		if firstTimeScalability:
			firstTimeScalability = False
			cmd += ' | cat > ' + scalabilityFile
		else:
			cmd += ' | grep csv, | cat >> ' + scalabilityFile

	# build wrapper to print nice, short lines in the CLI
	wrapper = textwrap.TextWrapper(initial_indent='    ', width=120, subsequent_indent='    ')
	# check whether or not to actually execute the tasks
	if not dryRun:
		print colored('[RUNNING]', 'green'), 'Executing:'
		print wrapper.fill(colored(cmd, 'cyan'))
		call(cmd, shell=True)
	else:
		print colored('[DRY RUN]', 'red'), 'Would be calling:'
		print wrapper.fill(colored(cmd, 'cyan'))

def buildFilterParams(paramsPermutation, paramsNames):
	params = ''
	for i, value in enumerate(paramsPermutation, 0):
		params = params+'-'+paramsNames[i]+' '+str(value)+' '

	return params.strip()

def anonymizeWithConfig(configuration):
	filters = configuration['filters']
	streams = configuration['streams']
	options = configuration['options']
	replicas = configuration['replicas']

	# for each filter in the configuration
	for privacyFilter in filters:
		filterName = privacyFilter['filter']
		params = privacyFilter['params']

		# generate all permutations of filter parameters
		paramsNames = []
		paramsValues = []
		discriminantParameter = privacyFilter['discriminantParameter']
		discriminantValues = []
		for param in params:
			name = param['name']
			if name == discriminantParameter:
				discriminantValues = param['values']
			else:
				paramsNames.append(param['name'])
				paramsValues.append(param['values'])
		paramsPermutations = list(itertools.product(*paramsValues))

		# for each permutation of filter parameters
		for permutation in paramsPermutations:
			# generate filter specification
			filterParams = buildFilterParams(permutation, paramsNames)
			builtFilter = filterName + ' ' + filterParams
			# for each stream to anonymize, with the built filter specification
			for stream in streams:
				# for each number of instances
				for instances in options['maximumInstances']:
					# discriminate over a parameter (all executions go to the same CSV file)
					first = True
					for value in discriminantValues:
						for i in range(0, replicas): # for the specified number of replicas
							print stream, instances, builtFilter, value, first
							if first:
								first = False
						#TODO anonymizeStream(stream, builtFilter, str(instances), options)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Test scalability of MOA-PPSM filters.')
	parser.add_argument('config_file',
						help='a JSON file with the execution configuration')
	parser.add_argument('-d', '--dry-run', action='store_true',
						help='do not execute, just print the commands that WOULD be executed')
	args = parser.parse_args()

	# check if a dried run was requested
	dryRun = args.dry_run

	# execute with the config file given!
	with open(args.config_file, 'rb') as configFile:
		config = json.load(configFile)
		if not config['isScalability']:
			print 'error: the configuration provided is not a scalability experiment config file'
			sys.exit(1)
		else:
			anonymizeWithConfig(configuration=config)
