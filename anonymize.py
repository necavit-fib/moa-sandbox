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

'''
"options": {
	"suppressAnonymizationHeader": false
}
	stream=$(basename "$file" .arff)
	arff_file=streams/$stream.arff
	eval_file=evaluation/$stream-$filter_options.csv
	anon_file=anonymized/anon-$stream-$filter_options.arff

	#./moa.sh "Anonymize -s (ArffFileStream -f $arff_file) -f ($filter) -e evaluation/randomRBF-10000.csv -a anonymized/anonimized-random-RBF-10000.arff -u 1 -m 1000000000"
	#use -Q to silence anonymization (arff file out)
'''
# global flags
dryRun = False

def getCodedFilterSpec(filterSpec):
	filterComponents = filterSpec.split(' ')
	filterName = filterComponents[0]
	filterParams = ''.join(filterComponents[1:len(filterComponents)])
	return getFilterCode(filterName) + filterParams

def getBaseFilename(stream, filterSpec):
	streamName = os.path.splitext(os.path.basename(stream))[0]
	codedFilterSpec = getCodedFilterSpec(filterSpec)
	return codedFilterSpec + '_' + streamName

def getEvaluationFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.csv'

def getAnonymizedFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.arff'

def getReportFilename(outDir, stream, filterSpec):
	return outDir + '/' + getBaseFilename(stream, filterSpec) + '.moa'

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
		'streamSpec': '(ArffFileStream %s)' % stream,
		'filterSpec': '(%s)' % privacyFilter,
		'optString': getOptionsForFilterAndStream(options, privacyFilter, stream)
	}
	cmd = './moa.sh "Anonymize -s %(streamSpec)s -f %(filterSpec)s %(optString)s"' % cmdFormat

	# build wrapper to print nice, short lines in the CLI
	wrapper = textwrap.TextWrapper(initial_indent='    ', width=120, subsequent_indent='    ')

	if not dryRun:
		print colored('[RUNNING]', 'green'), 'Executing:'
		print wrapper.fill(colored(cmd, 'cyan'))
		# TODO call(cmd, shell=True)
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

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Anonymize stream files using MOA privacy filters.')
	parser.add_argument('config_file',
						help='a JSON file with the execution configuration (filters, streams, evaluation, ...)')
	parser.add_argument('-d', '--dry-run', action='store_true',
						help='do not execute, just print the commands that WOULD be executed')
	args = parser.parse_args()

	# check if a dried run was requested
	dryRun = args.dry_run

	# execute with the config file given!
	with open(args.config_file, 'rb') as configFile:
		config = json.load(configFile)
		anonymizeWithConfig(configuration=config)
