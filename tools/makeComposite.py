#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 17th April, 2018
#
# last modified : 18th July, 2018
#

from __future__ import division
import sys,argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import scipy
import math

"""

Tutorial links for pyplot
https://matplotlib.org/users/pyplot_tutorial.html
https://matplotlib.org/api/pyplot_api.html

For hex codes to display colors on the plots
https://htmlcolorcodes.com/

"""

parser = argparse.ArgumentParser(prog='python makeComposite.py', usage='%(prog)s [-h] [SAMPLE_CDT] [CONTROL_CDT] [compositeTitle][--chex CHEX] [--shex SHEX] [--bhex BHEX] [--vhex VHEX]')
parser.add_argument('sample',metavar='SAMPLE_CDT',nargs='?',help='Sample CDT file from Tag Pileup Frequency')
parser.add_argument('control',metavar='CONTROL_CDT',nargs='?', help='Control CDT file from Tag Pileup Frequency')
parser.add_argument('compositeTitle', help='Title for the compositePlot')
parser.add_argument('--chex', help="Color in Hexcode for the control in the plot (default:gray)")
parser.add_argument('--shex', help='Color in Hexcode for the sample in the plot (default:red)')
parser.add_argument('--bhex', help='Color in Hexcode for the background color in the plot (default:white)')
parser.add_argument('--vhex', help='Color in Hexcode for the center line in the plot (default:black)')
parser.add_argument('--region',type=int, help='Plots the composite within specified region from center (default:2000 , plots -2000bp to 2000bp)')
args = parser.parse_args()


def findRelativeMaxPoint(data):
    """
    Function to find the max and min for the input data of CDT values
    """

    values = list(data.iloc[0]) # selecting the first row values as a list
    maxi = max(values)    # finding the maximum of the values
    max_index = values.index(maxi) # finding the index of the max value within the list of values
    zero_relative = float(list(data.iloc[[],[max_index]])[0]) # co-ordinate on the composite plot

    return [zero_relative,maxi]

# reading the CDT file.
try:
    signalData = pd.read_csv(args.sample, sep='\t',index_col=0)
    controlData = pd.read_csv(args.control, sep='\t',index_col=0)
except:
    print "\nUnable to OPEN input files !\n"
    parser.print_help()
    sys.exit()


# Calculating the region to plot
if args.region:
    start_col = 2000 - int(args.region)
    stop_col = 2000 + int(args.region)
else:
    start_col = 0
    stop_col = 4000

# prepare PlotData for sample
signalData = signalData.round(decimals=3)

# Calculating the peak value index with respect to origin.
mPeak = findRelativeMaxPoint(signalData)
print mPeak

sx = list(signalData.iloc[:,start_col:stop_col].values.tolist())[0]
sy = list(signalData.iloc[:,start_col:stop_col].columns.astype(float))

# pre# prepare PlotData for control
controlData = controlData.round(decimals=3)
cx = list(controlData.iloc[:,start_col:stop_col].values.tolist())[0]
cy = list(controlData.iloc[:,start_col:stop_col].columns.astype(float))

#matplotlib.rcParams['font.family'] = "Arial"
# used to set the ceiling to be the top tick in the y-axis
fig,ax = plt.subplots()

# plotting the data for composite plots
if (args.shex):
    plt.plot(sy,sx,color="#"+args.shex,label="Signal")
else:
    plt.plot(sy,sx,color="red",label="Signal")
d = scipy.zeros(len(sx))
if (args.bhex):
    plt.fill_between(sy,sx, where=sx>=d, interpolate=False, color="#"+args.bhex)
if (args.chex):
    plt.plot(cy,cx,color="#"+args.chex,label="Control")
else:
    plt.plot(cy,cx,color="gray",label="Control")
if (args.vhex):
    plt.axvline(x=0, color="#"+args.vhex, linestyle='--',linewidth=2)
else:
    plt.axvline(x=0, color='black', linestyle='--',linewidth=2)


# plt.legend(loc='upper right')
#plt.yticks(range(0,int(mPeak[1])+6,2))

plt.yticks([0,math.ceil(mPeak[1])],fontsize=18)
plt.ylabel('Tags',fontsize=18)

# adding text to the composite plot. (the peak location.)
# https://matplotlib.org/api/_as_gen/matplotlib.pyplot.text.html

# position of the peak relative to 0
#value = '(' +str(int(mPeak[0]))+')'
#plt.text(x=-450, y=(int(mPeak[1])-3), s=value, fontsize=8)

# setting the ylimits for ticks
ax.set_ylim(0,math.ceil(mPeak[1]))

# removing the x-axis ticks
plt.xticks([])
# plt.xticks(range(-500,750,250))

plt.title(args.compositeTitle,fontsize=25)
# plt.axis('off')
# plt.show()

plt.setp(ax.spines.values(), linewidth=2)

# referance for margins
#https://matplotlib.org/api/_as_gen/matplotlib.pyplot.margins.html#matplotlib.pyplot.margins
#plt.margins(0.01)
plt.margins(0)
plt.tick_params(length=8,width=2)

plt.savefig('Composite_plot.png',frameon=False,dpi=300,pad_inches=0.05,bbox_inches='tight')
