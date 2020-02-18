#!/usr/bin/python
import getopt
import math
import sys

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import numpy as np
matplotlib.use('Agg')

"""
Program to Create a heatmap from tagPileUp tabular CDT file.
"""


def rebin(a, new_shape):
    M, N = a.shape
    m, n = new_shape
    if m >= M:
        # repeat rows in data matrix
        a = np.repeat(a, math.ceil(float(m) / M), axis=0)

    M, N = a.shape
    m, n = new_shape

    row_delete_num = M % m
    col_delete_num = N % n

    np.random.seed(seed=0)

    if row_delete_num > 0:
        # select deleted rows with equal intervals
        row_delete = np.linspace(0, M - 1, num=row_delete_num, dtype=int)
        # sort the random selected deleted row ids
        row_delete = np.sort(row_delete)
        row_delete_plus1 = row_delete[1:-1] + \
            1  # get deleted rows plus position
        # get deleted rows plus position (top +1; end -1)
        row_delete_plus1 = np.append(
            np.append(row_delete[0] + 1, row_delete_plus1), row_delete[-1] - 1)
        # put the info of deleted rows into the next rows by mean
        a[row_delete_plus1, :] = (
            a[row_delete, :] + a[row_delete_plus1, :]) / 2
        a = np.delete(a, row_delete, axis=0)  # random remove rows

    if col_delete_num > 0:
        # select deleted cols with equal intervals
        col_delete = np.linspace(0, N - 1, num=col_delete_num, dtype=int)
        # sort the random selected deleted col ids
        col_delete = np.sort(col_delete)
        col_delete_plus1 = col_delete[1:-1] + \
            1  # get deleted cols plus position
        # get deleted cols plus position (top +1; end -1)
        col_delete_plus1 = np.append(
            np.append(col_delete[0] + 1, col_delete_plus1), col_delete[-1] - 1)
        # put the info of deleted cols into the next cols by mean
        a[:, col_delete_plus1] = (
            a[:, col_delete] + a[:, col_delete_plus1]) / 2
        a = np.delete(a, col_delete, axis=1)  # random remove columns

    M, N = a.shape

    # compare the heatmap matrix
    a_compress = a.reshape((m, int(M / m), n, int(N / n))).mean(3).mean(1)
    return np.array(a_compress)


def plot_heatmap(data01, c, out_file_name, upper_lim, lower_lim, row_num, col_num, sites, heatmapTitle, xlabel, ddpi, ticks):

    # initialize color
    levs = range(100)
    assert len(levs) % 2 == 0, 'N levels must be even.'
    # select colors from color list
    my_cmap = mcolors.LinearSegmentedColormap.from_list(
        name='white_sth', colors=c, N=len(levs) - 1,)

    # initialize figure
    plt.figure(figsize=(col_num / 96, row_num / 96), dpi=96)
    ax = plt.axes([0, 0, 1, 1])  # remove margins

    plt.imshow(data01, cmap=my_cmap, interpolation='nearest',
               vmin=lower_lim, vmax=upper_lim, aspect='auto')  # plot heatmap

    # little trick to create custom tick labels.
    # [ only works if the difference between col and row is 100, fails for (500,500) etc]
    # get the initial ticks
    locs, labels = plt.xticks()

    # remove the first location to get proper heatmap tick position.
    locs = np.delete(locs, 0)
    labels.pop()

    # find the mid value and set it to zero, since ax is helping to make sure there are odd number of ticks.

    mid = int(len(labels) // 2)
    labels[0] = "-" + ticks
    labels[mid] = "0"
    labels[len(labels) - 1] = ticks

    # display the new ticks
    plt.xticks(locs, labels, fontsize=14)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which='major', length=10, width=2, color='black')
    ax.tick_params(which='minor', length=6, width=2, color='black')
    print("\n DEBUG INFO \n locs : {} \n length_locs : {} \n labels : {} \n length_labels:{}\n".format(
        locs, len(locs), labels, len(labels)))

    plt.yticks([])
    plt.xlabel(xlabel, fontsize=14)
    ylabel = "{:,}".format(sites) + " sites"
    plt.ylabel(ylabel, fontsize=14)
    plt.title(heatmapTitle, fontsize=18)

    # to increase the width of the plot borders
    plt.setp(ax.spines.values(), linewidth=2)

    # saving the figure
    plt.savefig(out_file_name, bbox_inches='tight',
                pad_inches=0.05, dpi=ddpi, facecolor=None)


def load_Data(input_file, out_file, quantile, absolute, color, header, start_col, row_num, col_num, heatmapTitle, xlabel, ddpi, ticks):
    data = open(input_file, 'r')
    if header == 'T':
        data.readline()

    data0 = []
    sites = 0  # to calculate the # no. of sites

    for rec in data:
        tmp = [(x.strip()) for x in rec.split('\t')]
        # print(tmp)
        data0.append(tmp[start_col:])
        sites = sites + 1
        # data.close()
    data0 = np.array(data0, dtype=float)

    print("# sites: ", sites)

    if row_num == -999:
        row_num = data0.shape[0]
    if col_num == -999:
        col_num = data0.shape[1]

    # rebin data0 (compresses the data using treeView compression algorithm)
    if row_num < data0.shape[0] and col_num < data0.shape[1]:
        data0 = rebin(data0, (row_num, col_num))
    elif row_num < data0.shape[0]:
        data0 = rebin(data0, (row_num, data0.shape[1]))
    elif col_num < data0.shape[1]:
        data0 = rebin(data0, (data0.shape[0], col_num))

    # Calculate contrast limits here
    rows, cols = np.nonzero(data0)

    if rows.size != 0 and cols.size != 0:
        upper_lim = np.percentile(data0[rows, cols], quantile)
    else:
        upper_lim = 0

    lower_lim = 0
    if absolute != -999:
        upper_lim = absolute

    # Setting an absolute threshold to a minimum,
    # in cases the 95th percentile contrast is <= user defined min_upper_lim
    min_upper_lim = 5.0
    if quantile != 90.0:
        print("\nQUANTILE: {}".format(quantile))
        print("Quantile calculated UPPER LIM: {}".format(upper_lim))
        print("LOWER LIM: {}".format(lower_lim))
        if upper_lim <= min_upper_lim:
            print("setting heatmap upper_threshold to min_upper_lim\n")
            upper_lim = min_upper_lim

    print('heatmap upper threshold: ' + str(upper_lim))
    print('heatmap lower threshold: ' + str(lower_lim))

    # set color here
    # convert rgb to hex (since matplotlib doesn't support 0-255 format for colors)
    s = color.split(",")
    color = '#{:02X}{:02X}{:02X}'.format(int(s[0]), int(s[1]), int(s[2]))
    c = ["white", color]

    # generate heatmap
    plot_heatmap(data0, c, out_file, upper_lim, lower_lim, row_num,
                 col_num, sites, heatmapTitle, xlabel, ddpi, ticks)


############################################################################
# python cdt_to_heatmap.py -i test.tabular.split_line -o test.tabular.split_line.png -q 0.9 -c black -d T -s 2 -r 500 -l 300 -b test.colorsplit
############################################################################

usage = """
Usage:
This script will create a heatmap given a tab-delimited
matrix file

python cdt_to_heatmap.py -i <input file> -o <output file> -q <quantile>  -t <absolute tag threshold> -c <rgb color> -d <header T/F> -s <start column> -r <row num after compress> -l <col num after compress>'

Example:
python cdt_to_heatmap.py -i test.tabular.split_line -o test.tabular.split_line.png -q 0.9 -c 193,66,66 -d T -s 2 -r 500 -l 300 -m 'Heatmap title' -x 'X-label goes here' -p 150 -k 100
"""

if __name__ == '__main__':

    # check for command line arguments
    if len(sys.argv) < 2 or not sys.argv[1].startswith("-"):
        sys.exit(usage)
        # get arguments
    try:
        optlist, alist = getopt.getopt(
            sys.argv[1:], 'hi:o:q:t:c:d:s:r:l:x:p:m:k:')
    except getopt.GetoptError:
        sys.exit(usage)

    # default quantile contrast saturation = 0.9
    quantile = 0.9
    # absolute contrast saturation overrides quantile
    absolute = -999

    # default figure width/height is defined by matrix size
    # if user-defined size is smaller than matrix, activate rebin function
    row_num = -999
    col_num = -999

    for opt in optlist:
        if opt[0] == "-h":
            sys.exit(usage)
        elif opt[0] == "-i":
            input_file = opt[1]
        elif opt[0] == "-o":
            out_file = opt[1]
        elif opt[0] == "-q":
            quantile = float(opt[1])
        elif opt[0] == '-t':
            absolute = float(opt[1])
        elif opt[0] == "-c":
            color = opt[1]
        elif opt[0] == "-d":
            header = opt[1]
        elif opt[0] == "-s":
            start_col = int(opt[1])
        elif opt[0] == "-r":
            row_num = int(opt[1])
        elif opt[0] == "-l":
            col_num = int(opt[1])
        elif opt[0] == "-m":
            heatmapTitle = opt[1]
        elif opt[0] == "-x":
            xlabel = opt[1]
        elif opt[0] == "-p":
            ddpi = int(opt[1])
        elif opt[0] == "-k":
            ticks = opt[1]

    print("Header present:", header)
    print("Start column:", start_col)
    print("Row number (pixels):", row_num)
    print("Col number (pixels):", col_num)
    print("heatmapTitle:", heatmapTitle)
    print("xlabel:", xlabel)
    print("dpi:", ddpi)
    print("ticks:", ticks)
    if absolute != -999:
        print("Absolute tag contrast threshold:", absolute)
    else:
        print("Percentile tag contrast threshold:", quantile)

    if absolute == -999 and quantile <= 0:
        print("\nInvalid threshold!!!")
        sys.exit(usage)

    load_Data(input_file, out_file, quantile, absolute, color, header,
              start_col, row_num, col_num, heatmapTitle, xlabel, ddpi, ticks)
