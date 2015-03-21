#!/usr/bin/env python

import argparse
from collections import namedtuple
import csv
import matplotlib.pyplot as plotter
import os
import re

# Data named tuple (data type)
Data = namedtuple('Data', ['x', 'y', 'legend'])

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
# solid
    {'color': 'k', 'marker': '^', 'linestyle': '-'},
    {'color': 'k', 'marker': 's', 'linestyle': '-'},
    {'color': 'k', 'marker': 'v', 'linestyle': '-'},
    {'color': 'k', 'marker': 'o', 'linestyle': '-'},
# dashed
    {'color': 'k', 'marker': '^', 'linestyle': '--'},
    {'color': 'k', 'marker': 's', 'linestyle': '--'},
    {'color': 'k', 'marker': 'v', 'linestyle': '--'},
    {'color': 'k', 'marker': 'o', 'linestyle': '--'},
# dash-dot
    {'color': 'k', 'marker': '^', 'linestyle': '-.'},
    {'color': 'k', 'marker': 's', 'linestyle': '-.'},
    {'color': 'k', 'marker': 'v', 'linestyle': '-.'},
    {'color': 'k', 'marker': 'o', 'linestyle': '-.'},
# dot
    {'color': 'k', 'marker': '^', 'linestyle': ':'},
    {'color': 'k', 'marker': 's', 'linestyle': ':'},
    {'color': 'k', 'marker': 'v', 'linestyle': ':'},
    {'color': 'k', 'marker': 'o', 'linestyle': ':'}
]

def parseParams(paramsString):
    params = {}
    chunks = paramsString.split('-')

    for chunk in chunks[1:len(chunks)]:
        name = re.match(alpha, chunk).group(0)
        match = re.search(decimal, chunk)
        if match:
            value = float(match.group(0))
        else:
            value = int(re.search(number, chunk).group(0))
        params[name] = value

    return params

def parseParamsFromFile(file):
    basename = os.path.basename(file.name)
    return parseParams(basename.split('_')[0])

def getLegendLabelForFile(file, args):
    if args.parameters == None:
        return '_nolegend_'

    legend = ''
    params = parseParamsFromFile(file)
    for selectedParam in args.parameters:
        if params[selectedParam] == None:
            raise NameError('You have selected a parameter that was not specified ' +
                            'in the file name: ' + selectedParam)
        else:
            legend += selectedParam + ' = ' + str(params[selectedParam]) + ' '

    return legend

def selectDataFromFile(file, args):
    legendLabel = getLegendLabelForFile(file, args)
    xValues = []
    yValues = []

    col = args.column
    reader = csv.reader(file)
    for i, row in enumerate(reader,0):
        if i > 0: # skip the CSV header
            xValues.append(i)
            yValues.append(float(row[col]))

    data = Data(x=xValues, y=yValues, legend=legendLabel)
    return data

def getDataSelection(args):
    selection = []

    for file in args.in_files:
        data = selectDataFromFile(file, args)
        selection.append(data)

    return selection

def plotDataSeries(ax, data, options):
    ax.plot(data.x, data.y,
            label=data.legend,
            color=options['color'],
            marker=options['marker'],
            linestyle=options['linestyle'],
            markevery=100,
            markersize=5.0)

def labelPlot(ax, args):
    ax.set_ylabel(getYLabel(args))
    ax.set_xlabel(args.x_label)
    if args.title != None:
        ax.set_title(args.title)

def formatAxes(ax):
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')

def makeLegend(ax):
    legend = ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    frame = legend.get_frame()
    frame.set_alpha(0.0)
    return legend

def exportTo(figure, outFile, legend):
    figure.savefig(outFile, bbox_inches='tight', bbox_extra_artists=(legend,))

def getPlotOptions(args):
    if args.black_white:
        return bwOptions
    else:
        return colorOptions

def getYLabel(args):
    if args.y_label == 'infer':
        with open(args.in_files[0].name, 'rb') as f:
            header = f.readline().strip()
            return header.split(',')[args.column]
    else:
        return args.y_label

def plotWithArgs(args):
    selection = getDataSelection(args)
    lineOptions = getPlotOptions(args)

    # PLOTTING BEGINS HERE!
    # prepare canvas and axes
    figure = plotter.figure(1)
    ax = figure.add_subplot(111)

    # for each data set selected previously ((x,y) values, legend...),
    #  plot them to the current axes (figure)
    for i, data in enumerate(selection, 0):
        if i >= len(lineOptions):
            raise NameError('You are trying to plot too many data series. No more line style combinations are possible.')
        plotDataSeries(ax, data, lineOptions[i])

    labelPlot(ax, args) # axis labeling and title
    formatAxes(ax) # spines and frame options
    lgd = makeLegend(ax) # plot legend
    exportTo(figure, args.out_file.name, lgd) # export the plot to the PDF output file

    # show  the plot if necessary
    if args.show:
        plotter.show()

if __name__ == '__main__':
    # argument parsing
    parser = argparse.ArgumentParser(
                        description='Plots moa-ppsm evaluation data from CSV files using Matplotlib.')
    parser.add_argument('-s', '--show', action='store_true',
                        help='shows the plot, besides exporting it')
    parser.add_argument('-w', '--black-white', action='store_true',
                        help='build the plot using a black and white scheme (use ticks, instead of color)')
    parser.add_argument('-t', '--title', default=None,
                        help='the title for the plot')
    parser.add_argument('-x', '--x-label', default='X',
                        help='the label of the X axis')
    parser.add_argument('-y', '--y-label', default='infer',
                        help='the label of the Y axis. If not specified or "infer" is set, '+
                                'the label will be extracted from the CSV header')
    parser.add_argument('-p', '--parameters', nargs='+',
                        help='the selected parameters to be included in the plot legend')
    parser.add_argument('-c', '--column', type=int, required=True,
                        help='the selected column to be plotted')
    parser.add_argument('-o', '--out-file', type=argparse.FileType('w'), required=True,
                        help='the file where the plot will be saved to')
    parser.add_argument('-i', '--in-files', nargs='+', type=argparse.FileType('r'), required=True,
                        help='the CSV file or files used as input data')
    args = parser.parse_args()

    # main procedure
    plotWithArgs(args)
