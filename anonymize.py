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

def getBaseFilename(stream, filterSpec):
	streamName = stream.split('.')[1]
	codedFilterSpec = getCodedFilterSpec(filterSpec)
	return codedFilterSpec + '_' + streamName

def getEvaluationFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.csv'

def getAnonymizedFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.arff'

def getReportFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.moa'

def getParallelLogFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.log'

def getOptionsForFilterAndStream(options, filterSpec, stream):
	optionsSpec = ''

	# task report
	if options['silenceTaskReport']:
		optionsSpec += '-O /dev/null '
	else:
		file = getReportFilename(options['taskReportOutputDirectory'], stream, filterSpec)
		optionsSpec += '-O ' + file + ' '

	# anonymization
	optionsSpec += '-m ' + str(options['maximumInstances']) + ' '
	if options['suppressAnonymizationHeader']:
		optionsSpec += '-h '
	if options['silenceAnonymization']:
		optionsSpec += '-Q '
	else:
		file = getAnonymizedFilename(options['anonymizationOutputDirectory'], stream, filterSpec)
		optionsSpec += '-a ' + file + ' '

	# evaluation
	optionsSpec += '-u ' + str(options['evaluationUpdateRate']) + ' '
	if options['silenceEvaluation']:
		optionsSpec += '-q '
	else:
		file = getEvaluationFilename(options['evaluationOutputDirectory'], stream, filterSpec)
		optionsSpec += '-e ' + file + ' '

	return optionsSpec

def anonymizeStream(stream, privacyFilter, options):
	cmdFormat = {
		'streamSpec': '(%s)' % stream,
		'filterSpec': '(%s)' % privacyFilter,
		'optString': getOptionsForFilterAndStream(options, privacyFilter, stream)
	}
	cmd = './moa.sh "Anonymize -s %(streamSpec)s -f %(filterSpec)s %(optString)s"' % cmdFormat

	if parallel:
		cmd += ' &> %s' % getParallelLogFilename(logsDir, stream, privacyFilter)

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
		if not dryRun:
			print colored('[RUNNING]', 'green'), 'Executing:'
			print wrapper.fill(colored(cmd, 'cyan'))
			call(cmd, shell=True)
		else:
			print colored('[DRY RUN]', 'red'), 'Would be calling:'
			print wrapper.fill(colored(cmd, 'cyan'))

def anonymizeWithFilter(privacyFilter, streams, options):
	for stream in streams:
		anonymizeStream(stream, privacyFilter, options)

def getFilterParams(paramsPermutation, paramsNames):
	params = ''
	for i, value in enumerate(paramsPermutation, 0):
		params = params+'-'+paramsNames[i]+' '+str(value)+' '

	return params.strip()

def getFilter(filterName, filterParams):
	return filterName + ' ' + filterParams

def anonymizeWithConfig(configuration):
	filters = configuration['filters']
	streams = configuration['streams']
	options = configuration['options']

	for privacyFilter in filters:
		filterName = privacyFilter['filter']
		params = privacyFilter['params']

		# generate all permutations
		paramsNames = []
		paramsValues = []
		for param in params:
			paramsNames.append(param['name'])
			paramsValues.append(param['values'])
		paramsPermutations = list(itertools.product(*paramsValues))

		# generate filter string and anonymize for each stream
		for permutation in paramsPermutations:
			filterParams = getFilterParams(permutation, paramsNames)
			builtFilter = getFilter(filterName, filterParams)
			anonymizeWithFilter(builtFilter, streams, options)

	if parallel:
		with open('Makefile', 'a') as makefile:
			tasks = ' '.join(str(x) for x in parallelTasks)
			makefile.write('all: ')
			makefile.write(tasks)
			makefile.write('\n')
			#print 'all:', tasks
			#print colored('REMEMBER to execute', 'red'), '"make -j JOBS"', colored('on the generated Makefile', 'red')

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
