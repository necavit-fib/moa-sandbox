#!/usr/bin/env python

import argparse
import subprocess
from termcolor import colored
import textwrap

# global flags and variables
generators = [
	{
		'spec': 'generators.WaveformGenerator',
		'filePrefix': 'waveform'
	},
	{
		'spec': 'generators.RandomRBFGenerator',
		'filePrefix': 'randomRBF'
	},
	{
		'spec': 'generators.AgrawalGenerator -p 0.0',
		'filePrefix': 'agrawal'
	}
]
instances = [10000, 100000, 1000000, 10000000]
dryRun = False


def getFileName(outDir, generator, instances):
	return outDir + '/' + generator['filePrefix'] + '-' + str(instances) + '.arff'

def generateStreams(outDir):
	for generator in generators:
		for m in instances:
			fileName = getFileName(outDir, generator, m)
			cmdConfig = {
				'stream': '-s (%s)' % generator['spec'],
				'file': '-f %s' % fileName,
				'inst':'-m ' + str(m)
			}
			cmd = './moa.sh "WriteStreamToARFFFile %(stream)s %(file)s %(inst)s"' % cmdConfig

			# build wrapper to print nice, short lines in the CLI
			wrapper = textwrap.TextWrapper(initial_indent='    ', width=120, subsequent_indent='    ')
			if not dryRun:
				print colored('[RUNNING]', 'green'), 'Executing:'
				print wrapper.fill(colored(cmd, 'cyan'))
				subprocess.call(cmd, shell=True)
			else:
				print colored('[DRY RUN]', 'red'), 'Would be calling:'
				print wrapper.fill(colored(cmd, 'cyan'))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generates random data using MOA generators and outputs it to different ARFF files.')
	parser.add_argument('out_dir', help='the output directory where the stream files will be stored')
	parser.add_argument('-d', '--dry-run', action='store_true',
						help='do not execute, just print the commands that WOULD be executed')
	args = parser.parse_args()

	dryRun = args.dry_run
	generateStreams(args.out_dir)
