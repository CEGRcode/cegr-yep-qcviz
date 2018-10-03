#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 28th June, 2018
#
# last modified : 28th June, 2018
#

from __future__ import division
import sys,argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import scipy
import pprint
# import matplotlib.patches as mpatches

"""
Program to take in a strand separate Experimental CDT (tabular) file
from tag pile up and creating the motif specific composite plots.

"""

parser = argparse.ArgumentParser()
parser.add_argument('sample',help='Sample CDT file from Tag Pileup Frequency')
args = parser.parse_args()


# reading the CDT file.
try:
    signalData = pd.read_csv(args.sample, sep='\t',index_col=0)
except:
    print "\nUnable to OPEN input files !\n"
    parser.print_help()
    sys.exit()



# Calculating the region to plot [-500 to 500]
start_col = 2000 - 500
stop_col = 2000 + 500

# prepare PlotData, remove extra decimal values
signalData = signalData.round(decimals=3)

# General DEBUG
print signalData.index
print signalData.shape

# retrieve the row index from the dataframe
rowIndex = list(signalData.index)

# retrieve data for Sense strand
sx = list(signalData.loc[rowIndex[0]])

# retrieve values for y axis and convert them to float
sy = list(signalData.columns)
sy = map(float,sy)

# prepare PlotData for antisense strand
cx = list(signalData.loc[rowIndex[1]])

# convert antisense data values to negative, to plot it below the sense data.
x1 = [ -i for i in cx]

fig,ax = plt.subplots()
plt.plot(sy,sx,'b',sy,x1,'r') # plotting the graph

# adding the fill color for both the strands.
d = scipy.zeros(len(sx))
d1 = scipy.zeros(len(sx))
plt.fill_between(sy,sx, where=sx>=d, interpolate=False, color="blue")
plt.fill_between(sy,x1, where=sx>=d1, interpolate=False, color="red")

# Option to draw a vertical line at origin on x-axis
# plt.axvline(x=0, color='black', linestyle='--')

# creating the grid lines
#plt.grid(linestyle='--', linewidth=0.5)
plt.gca().xaxis.grid(True,linestyle='--',linewidth=0.5)

# creating the legend using custom patches of color
# red_patch = mpatches.Patch(color='red', label='Anti-Sense')
# blue_patch = mpatches.Patch(color='blue', label='Sense')
# plt.legend(handles=[blue_patch,red_patch])
# plt.legend(loc='upper right')

# adding custom xticks and yticks
plt.xticks(range(-100,150,50),fontsize=14)
plt.yticks(fontsize=14)

# if you chose to not include the xticks , since they are similar to heatmap x-axis ticks
#plt.xticks([])

# plt.yticks(range(-10,12,2))
# plt.xticks([-500,0,500])

#start,end=ax.get_ylim()
#ax.set_ylim(start-1,end+1)

# Customizing the border/ spines on each side of the plot.
# frame1 = plt.gca()
# frame1.axes.xaxis.set_ticklabels([])
# frame1.axes.yaxis.set_ticklabels([])
# frame1.axes.spines['top'].set_visible(False)
# frame1.axes.spines['right'].set_visible(False)
# frame1.axes.spines['bottom'].set_visible(False)
# frame1.axes.spines['left'].set_visible(False)

# plt.show()

# setting the margins
plt.margins(0.01)

# saving the image at 300dpi , web standard for printing images.
plt.savefig('MotifComposite_sense_antisense.png',frameon=False,dpi=150,pad_inches=0)
