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

def getCodedFilterSpec(filterSpec, discriminantParameter, paramValue):
	# print '(', filterSpec, ')', discriminantParameter, paramValue
	filterComponents = filterSpec.split(' ')
	filterName = filterComponents[0]
	for i in range(len(filterComponents)):
		if filterComponents[i] == ('-'+discriminantParameter):
			del filterComponents[i+1]
			del filterComponents[i]
			break
	filterParams = ''.join(filterComponents[1:len(filterComponents)])
	return getFilterCode(filterName) + filterParams

def getBaseFilename(stream, filterSpec, discriminantParameter, paramValue):
	streamName = stream.split('.')[1]
	codedFilterSpec = getCodedFilterSpec(filterSpec, discriminantParameter, paramValue)
	return codedFilterSpec + '_' + streamName

def getFile(outDir, baseFilename, extension):
	return outDir + '/' + baseFilename + '.' + extension

def getTaskOptions(instances):
	return '-z -m %s' % instances

def cliCall(cmd):
	# build wrapper to print nice, short lines in the CLI
	wrapper = textwrap.TextWrapper(
											initial_indent='    ', width=120, subsequent_indent='    ')
	# check whether or not to actually execute the tasks
	if not dryRun:
		print colored('[RUNNING]', 'green'), 'Executing:'
		print wrapper.fill(colored(cmd, 'cyan'))
		call(cmd, shell=True) # execute the command call
	else:
		print colored('[DRY RUN]', 'red'), 'Would be calling:'
		print wrapper.fill(colored(cmd, 'cyan'))

def buildBaseCmd(stream, instances, filterSpec):
	cmdFormat = {
		'stream': '-s (%s)' % stream,
		'filter': '-f (%s)' % filterSpec,
		'task': getTaskOptions(instances)
	}
	return './moa.sh -e "Anonymize %(stream)s %(filter)s %(task)s"' % cmdFormat

def executeExperiment(stream, instances, filterSpec,
										  discriminantParameter, paramValue, isFirst, options):
	# build the command line call
	cmd = buildBaseCmd(stream, instances, filterSpec)

	# add the necessary redirection for scalability experiment execution
	scalabilityFile = getFile(options['scalabilityDirectory'], \
									getBaseFilename(stream,filterSpec,discriminantParameter,paramValue), \
									'csv')
	cmdFormat = {
		'head': discriminantParameter,
		'value': paramValue,
		'file': scalabilityFile
	}
	if isFirst:
		# change the CSV header and CSV record that MOA outputs as summary
		cmd += ' | sed "s/csvhead/%(head)s/;s/csv/%(value)s/" > %(file)s' % cmdFormat
	else:
		# only grep the CSV record and change it
		cmd += ' | grep csv, | sed "s/csv/%(value)s/" >> %(file)s' % cmdFormat

	# perform the CLI call
	cliCall(cmd)

def buildFilterParams(paramsPermutation, paramsNames, discriminantParameter, value):
	params = ''
	for i, paramValue in enumerate(paramsPermutation, 0):
		params += '-' + paramsNames[i] + ' ' + str(paramValue) + ' '
	params += '-' + discriminantParameter + ' ' + str(value)
	return params.strip()

def processWithConfig(configuration):
	filters = configuration['filters']
	streams = configuration['streams']
	options = configuration['options']
	replicas = configuration['replicas']

	# for each filter in the configuration
	for privacyFilter in filters:
		filterName = privacyFilter['filter']
		params = privacyFilter['params']

		# generate all permutations of filter parameters, without the discriminant
		#  parameter (the one over which the scalability is checked)
		paramsNames = []
		paramsValues = []
			# identify the discriminant parameter
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
			# for each stream to anonymize, with the built filter specification
			for stream in streams:
				# for each number of instances
				for instances in options['maximumInstances']:
					# discriminate over a parameter (all executions go to the same CSV file)
					first = True
					for value in discriminantValues:
						# generate filter specification
						filterParams = buildFilterParams(
														permutation, paramsNames, discriminantParameter, value)
						builtFilter = filterName + ' ' + filterParams
						for i in range(0, replicas): # for the specified number of replicas
							# print stream, instances, '(', builtFilter, ')', discriminantParameter, value, first
							executeExperiment(
									stream, str(instances), builtFilter, \
									discriminantParameter, str(value), first, options)
							# not the first one anymore!
							if first:
								first = False

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
			print 'ERROR: the configuration given is not a scalability experiment config file'
			sys.exit(1)
		else:
			processWithConfig(configuration=config)
