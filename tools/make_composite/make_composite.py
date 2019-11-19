#!/usr/bin/python
from __future__ import division

import argparse
import math
import sys

import matplotlib
import matplotlib.pyplot as plt

import pandas as pd

import scipy

matplotlib.use('Agg')

"""
Program to create the composite plots from signal and control tag pile up CDT data matrix
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    'sampleData', help='Sample CDT file from Tag Pileup Frequency')
parser.add_argument(
    'controlData', help='Control CDT file from Tag Pileup Frequency')
parser.add_argument('compositeTitle', help='Title for the compositePlot')
parser.add_argument(
    'signalColor', help='Color in Hexcode for the sample in the plot ')
parser.add_argument(
    'controlColor', help="Color in Hexcode for the control in the plot ")
parser.add_argument(
    'backgroundColor', help='Color in Hexcode for the background color in the plot')
parser.add_argument(
    'centerLineColor', help='Color in Hexcode for the center line in the plot')
parser.add_argument('dpi', help='Dots per inch (DPI) for the image')
parser.add_argument(
    'yMaxTick', help='Min-Max value to set the Y-axis upper limit')

args = parser.parse_args()


def findRelativeMaxPoint(data):
    """
    Function to find the max and min for the input data of CDT values
    """

    values = list(data.iloc[0])  # selecting the first row values as a list
    maxi = max(values)    # finding the maximum of the values
    # finding the index of the max value within the list of values
    max_index = values.index(maxi)
    # co-ordinate on the composite plot
    zero_relative = float(list(data.iloc[[], [max_index]])[0])

    return [zero_relative, maxi]


# reading the CDT file.
try:
    signalData = pd.read_csv(args.sampleData, sep='\t', index_col=0)
    controlData = pd.read_csv(args.controlData, sep='\t', index_col=0)
except IOError:
    print "\nUnable to OPEN input files !\n"
    parser.print_help()
    sys.exit()

print "signalData shape : {}".format(signalData.shape)
print "controlData shape : {}".format(controlData.shape)

# prepare PlotData for sample
signalData = signalData.round(decimals=3)

# Calculating the peak value index with respect to origin.
mPeak = findRelativeMaxPoint(signalData)
print mPeak

# retrieve the row index from the dataframe
rowIndex = list(signalData.index)

# retrieve data for signal dataset
sx = list(signalData.loc[rowIndex[0]])

# retrieve values for y axis and convert them to float
sy = list(signalData.columns)
sy = map(float, sy)


# retrieve the row index from the controlData dataframe
rowIndex = list(controlData.index)

# retrieve data for control dataset
cx = list(controlData.loc[rowIndex[0]])

# retrieve values for y axis and convert them to float
cy = list(controlData.columns)
cy = map(float, cy)


# setting the font
# matplotlib.rcParams['font.family'] = "Arial"

# generating the figure
fig, ax = plt.subplots()

# plotting the signal data
plt.plot(sy, sx, color="#" + args.signalColor, label="Signal")

# adding the background color
d = scipy.zeros(len(sx))
plt.fill_between(sy, sx, where=sx >= d, interpolate=False,
                 color="#" + args.backgroundColor)

# plotting the control data
plt.plot(cy, cx, color="#" + args.controlColor, label="Control")

# adding the vertical line at midpoint
plt.axvline(x=0, color="#" + args.centerLineColor, linestyle='--', linewidth=2)

# adding yticks and label
plt.yticks([0, max(int(args.yMaxTick), math.ceil(mPeak[1]))], fontsize=18)
plt.ylabel('Tags', fontsize=18)

# setting the padding space between the y-axis label and the y-axis
if math.ceil(mPeak[1]) < 10:
    ax.yaxis.labelpad = -16
else:
    ax.yaxis.labelpad = -25

# adding text to the composite plot. (the peak location.)
# https://matplotlib.org/api/_as_gen/matplotlib.pyplot.text.html

# changing the co-ordinates to position the value to the top right corner
left, width = 0.28, .7
bottom, height = .28, .7
right = left + width
top = bottom + height

# position of the peak relative to 0
value = '(' + str(int(mPeak[0])) + ')'
# plt.text(x=-480, y=(int(math.ceil(mPeak[1])-0.2)), s=value, fontsize=12)
plt.text(right, top, value,
         horizontalalignment='right',
         verticalalignment='top',
         transform=ax.transAxes, fontsize=14)

# setting the ylimits for yticks
ax.set_ylim(0, max(int(args.yMaxTick), math.ceil(mPeak[1])))

# removing the x-axis ticks
plt.xticks([])

# adding the title and increase the spine width
plt.title(args.compositeTitle, fontsize=25)
plt.setp(ax.spines.values(), linewidth=2)

# referance for margins
# https://matplotlib.org/api/_as_gen/matplotlib.pyplot.margins.html#matplotlib.pyplot.margins

plt.margins(0)
plt.tick_params(length=8, width=2)

plt.savefig('Composite_plot.png', frameon=False, dpi=int(
    args.dpi), pad_inches=0.05, bbox_inches='tight')
