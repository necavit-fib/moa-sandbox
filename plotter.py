#!/usr/bin/env python

import sys
import csv
import matplotlib.pyplot as plotter
import re
import os
import json

# useful regular expressions
alpha = re.compile('[a-zA-Z]*')
decimal = re.compile('\d+.\d+')
number = re.compile('\d+')

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
def plotFile(filePath, parameters):
    print filePath

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

def plotFiles(filesDir):
    files = os.listdir(filesDir)
    files.sort()
    for file in files:
        if file.endswith('.csv'):
            basename = os.path.splitext(os.path.basename(file))[0]
            plotParams = parseBasename(basename)
            plotFile(file, plotParams)
'''

if __name__ == '__main__':
    # TODO do this: plotFiles('evaluation')
    #   and remove the following code

    plotParams = {}
    column = int(sys.argv[1])
    plotFiles(column, sys.argv[2:len(sys.argv)])
    #plot(file=sys.argv[1], params=plotParams)
