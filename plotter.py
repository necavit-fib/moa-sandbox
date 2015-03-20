#!/usr/bin/env python

import argparse
import csv
import json
import matplotlib.pyplot as plotter
import os
import re
import sys


# useful regular expressions
alpha = re.compile('[a-zA-Z]*')
decimal = re.compile('\d+.\d+')
number = re.compile('\d+')

# plot options for colored plots
colorOptions = [
# solid linestyle
    {'color': 'blue', 'marker': None, 'linestyle': '-'},
    {'color': 'red', 'marker': None, 'linestyle': '-'},
    {'color': 'green', 'marker': None, 'linestyle': '-'},
    {'color': 'cyan', 'marker': None, 'linestyle': '-'},
    {'color': 'magenta', 'marker': None, 'linestyle': '-'},
# dashed linestyle
    {'color': 'blue', 'marker': None, 'linestyle': '--'},
    {'color': 'red', 'marker': None, 'linestyle': '--'},
    {'color': 'green', 'marker': None, 'linestyle': '--'},
    {'color': 'cyan', 'marker': None, 'linestyle': '--'},
    {'color': 'magenta', 'marker': None, 'linestyle': '--'},
# dash-dot linestyle
    {'color': 'blue', 'marker': None, 'linestyle': '-.'},
    {'color': 'red', 'marker': None, 'linestyle': '-.'},
    {'color': 'green', 'marker': None, 'linestyle': '-.'},
    {'color': 'cyan', 'marker': None, 'linestyle': '-.'},
    {'color': 'magenta', 'marker': None, 'linestyle': '-.'},
# dot linestyle
    {'color': 'blue', 'marker': None, 'linestyle': ':'},
    {'color': 'red', 'marker': None, 'linestyle': ':'},
    {'color': 'green', 'marker': None, 'linestyle': ':'},
    {'color': 'cyan', 'marker': None, 'linestyle': ':'},
    {'color': 'magenta', 'marker': None, 'linestyle': ':'}
]

# plot options for B&W plots
bwOptions = [
# no marker
    {'color': 'k', 'marker': None, 'linestyle': '-'},
    {'color': 'k', 'marker': None, 'linestyle': '--'},
    {'color': 'k', 'marker': None, 'linestyle': '-.'},
    {'color': 'k', 'marker': None, 'linestyle': ':'},
# circle marker
    {'color': 'k', 'marker': 'o', 'linestyle': '-'},
    {'color': 'k', 'marker': 'o', 'linestyle': '--'},
    {'color': 'k', 'marker': 'o', 'linestyle': '-.'},
    {'color': 'k', 'marker': 'o', 'linestyle': ':'},
# down triangle marker
    {'color': 'k', 'marker': 'v', 'linestyle': '-'},
    {'color': 'k', 'marker': 'v', 'linestyle': '--'},
    {'color': 'k', 'marker': 'v', 'linestyle': '-.'},
    {'color': 'k', 'marker': 'v', 'linestyle': ':'},
# square marker
    {'color': 'k', 'marker': 's', 'linestyle': '-'},
    {'color': 'k', 'marker': 's', 'linestyle': '--'},
    {'color': 'k', 'marker': 's', 'linestyle': '-.'},
    {'color': 'k', 'marker': 's', 'linestyle': ':'},
# up triangle marker
    {'color': 'k', 'marker': '^', 'linestyle': '-'},
    {'color': 'k', 'marker': '^', 'linestyle': '--'},
    {'color': 'k', 'marker': '^', 'linestyle': '-.'},
    {'color': 'k', 'marker': '^', 'linestyle': ':'}
]

'''
def plot(file, params):
    print 'Plot with CSV: ', str(csv), ' and parameters: ', json.dumps(params, sort_keys=True, indent=4)
    column = 0
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        yValues = []
        xValues = []
        yAxisLabel = ''
        for i, row in enumerate(reader,0):
            if i == 0:
                yAxisLabel = str(row[column])
            else:
                yValues.append(float(row[column]))
                xValues.append(i)


        plotTitle = os.path.splitext(os.path.basename(file))[0]
        plotter.plot(xValues, yValues)
        #plotter.suptitle(plotTitle, fontsize=50)
        plotter.xlabel('Instaces')
        plotter.ylabel(yAxisLabel)

        plotFilename = 'plots/' + plotTitle


def exportAndShow():
    plotter.savefig('plot1.pdf') #, bbox_inches='tight'
    plotter.show()

def plotFiles(col, files):
    column = col
    for file in files:
        with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            yValues = []
            xValues = []
            yAxisLabel = ''
            for j, row in enumerate(reader,0):
                if j == 0:
                    yAxisLabel = str(row[column])
                else:
                    yValues.append(float(row[column]))
                    xValues.append(j)
            plotter.plot(xValues, yValues)
            plotter.xlabel('Instaces')
            plotter.ylabel(yAxisLabel)
    exportAndShow()
'''

'''

def getParams(paramsList):
    params = []

    for paramDescription in paramsList:
        param = {}

        name = re.match(alpha, paramDescription).group(0)
        param['name'] = name

        value = re.search(decimal, paramDescription)
        if value:
            param['value'] = float(value.group(0))
        else:
            value = re.search(number, paramDescription).group(0)
            param['value'] = int(value)

        params.append(param)

    return params

def parseStreamParams(streamString):
    chunks = re.split('-', streamString)

    streamParams = {}
    streamParams['stream'] = chunks[0]
    streamParams['instances'] = int(chunks[1])

    return streamParams

def parseFilterParams(filterString):
    chunks = re.split('-', filterString)

    filterParams = {}
    filterParams['filterName'] = chunks[0]
    filterParams['parameters'] = getParams(chunks[1:len(chunks)])

    return filterParams

def parseBasename(basename):
    chunks = re.split('_', basename)
    # chunks has 2 items: the filter and its parameters [0] and the stream [1]

    plotParams = {}
    plotParams['filter'] = parseFilterParams(chunks[0])
    plotParams['stream'] = parseStreamParams(chunks[1])

    print 'plotParams:', json.dumps(plotParams, sort_keys=True, indent=4)

    return plotParams
'''


def plotDataSeries(data, options):
    plotter.plot(data.x, data.y,
                    color=options['color'],
                    marker=options['marker'],
                    linestyle=options['linestyle'])

def exportTo(outFile):
    print outFile
    plotter.savefig(outFile)

def plotWithArgs(args):
    print args
    # TODO

    #data

    # export the plot to the PDF output file
    #exportTo(args.out_file.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots data from CSV files using Matplotlib.')
    parser.add_argument('-w', '--black-white', action='store_true',
                        help='build the plot using a black and white scheme (use ticks, instead of color)')
    parser.add_argument('-x', '--x-axis', help='the label of the X axis')
    parser.add_argument('-y', '--y-axis', help='the label of the Y axis')
    parser.add_argument('-p', '--parameters', nargs='+',
                        help='the selected parameters to be included in the plot legend')
    parser.add_argument('-c', '--columns', type=int, nargs='+', required=True,
                        help='the selected columns to be plotted')
    parser.add_argument('-o', '--out-file', type=argparse.FileType('w'), required=True,
                        help='the file where the plot will be saved to')
    parser.add_argument('-i', '--in-files', nargs='+', type=argparse.FileType('r'), required=True,
                        help='the CSV file or files used as input data')
    args = parser.parse_args()

    # main procedure
    plotWithArgs(args)
