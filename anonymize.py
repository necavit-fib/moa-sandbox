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
parallel = False
logsDir = 'logs'

# global variables
parallelTasks = []

def getCodedFilterSpec(filterSpec):
	filterComponents = filterSpec.split(' ')
	filterName = filterComponents[0]
	filterParams = ''.join(filterComponents[1:len(filterComponents)])
	return getFilterCode(filterName) + filterParams

def getBaseFilename(stream, filterSpec, instances):
	streamName = stream.split('.')[1]
	codedFilterSpec = getCodedFilterSpec(filterSpec)
	return codedFilterSpec + '_' + streamName + instances

def getFile(outDir, baseFilename, extension):
	return outDir + '/' + baseFilename + '.' + extension

def getTaskOptions(options, filterSpec, stream, instances):
	optionsSpec = ''
	baseFilename = getBaseFilename(stream,filterSpec, instances)

	# instances to anonymize
	optionsSpec += '-m ' + instances + ' '

	# task report
	reportOptions = options['report']
	if reportOptions['summarizeReport']:
		optionsSpec += '-z '
	if reportOptions['writeTaskReport']:
		file = getFile(reportOptions['taskReportDirectory'], baseFilename, 'txt')
		optionsSpec += '-r ' + file + ' '

	# anonymization
	anonOptions = options['anonymization']
	if anonOptions['writeAnonymization']:
		file = getFile(anonOptions['anonymizationDirectory'], baseFilename, 'arff')
		optionsSpec += '-a ' + file + ' '
		if anonOptions['suppressAnonymizationHeader']:
			optionsSpec += '-h '

	# evaluation
	evalOptions = options['evaluation']
	if evalOptions['writeEvaluation']:
		file = getFile(evalOptions['evaluationDirectory'], baseFilename, 'csv')
		optionsSpec += '-e ' + file + ' '
		optionsSpec += '-u ' + str(evalOptions['evaluationUpdateRate']) + ' '

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
		'stream': '(%s)' % stream,
		'filter': '(%s)' % privacyFilter,
		'taskOpts': getTaskOptions(options, privacyFilter, stream, instances)
	}
	cmd = './moa.sh "Anonymize -s %(stream)s -f %(filter)s %(taskOpts)s"' % cmdFormat

	# add the necessary redirection for parallel execution
	if parallel:
		cmd += ' &> %s' % getFile(logsDir, getBaseFilename(stream, privacyFilter, instances), 'log')

	# build wrapper to print nice, short lines in the CLI
	wrapper = textwrap.TextWrapper(initial_indent='    ', width=120, subsequent_indent='    ')

	if parallel:
		# generate Makefile
		with open('Makefile', 'a') as makefile:
			if len(parallelTasks) == 0:
				parallelTasks.append(1)
			else:
				parallelTasks.append(parallelTasks[len(parallelTasks) - 1] + 1)
			makefile.write('%s:\n' % parallelTasks[len(parallelTasks) -1])
			makefile.write('\t%s\n' % cmd)
	else:
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

	# for each filter in the configuration
	for privacyFilter in filters:
		filterName = privacyFilter['filter']
		params = privacyFilter['params']

		# generate all permutations of filter parameters
		paramsNames = []
		paramsValues = []
		for param in params:
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
					anonymizeStream(stream, builtFilter, str(instances), options)

	if parallel:
		with open('Makefile', 'a') as makefile:
			tasks = ' '.join(str(x) for x in parallelTasks)
			makefile.write('all: ')
			makefile.write(tasks)
			makefile.write('\n')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Anonymize stream files using MOA privacy filters.')
	parser.add_argument('config_file',
						help='a JSON file with the execution configuration (filters, streams, evaluation, ...)')
	parser.add_argument('-d', '--dry-run', action='store_true',
						help='do not execute, just print the commands that WOULD be executed')
	parser.add_argument('-p', '--parallel', action='store_true',
						help='writes the commands to execute into a Makefile to be executed in parallel using GNU Make. This option superseeds --dry-run')
	args = parser.parse_args()

	# check if a dried run was requested
	dryRun = args.dry_run

	# check if a Makefile generation was requested
	parallel = args.parallel
	
	if parallel:
		response = raw_input('Delete the previous Makefile and generate a new one? (y/n): ')
		if response != 'y':
			print colored('ABORTING', 'red')
			sys.exit(1)
		else:
			if os.path.isfile('Makefile'):
				os.remove('Makefile')
			print colored('Generating Makefile...', 'green')

	# execute with the config file given!
	with open(args.config_file, 'rb') as configFile:
		config = json.load(configFile)
		anonymizeWithConfig(configuration=config)
