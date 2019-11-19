#!/usr/bin/python
from __future__ import division

import argparse
import math
import pprint

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)

import numpy as np

matplotlib.use('Agg')

"""
Program to Create a heatmap from tagPileUp tabular file and contrast Threshold file.
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


def plot_heatmap(data01, c, out_file_name, upper_lim, lower_lim, row_num, col_num, ticks, ddpi, xlabel, heatmapTitle, sites):

    # initialize color
    levs = range(100)
    assert len(levs) % 2 == 0, 'N levels must be even.'

    # select colors from color list
    my_cmap = mcolors.LinearSegmentedColormap.from_list(
        name='white_sth', colors=c, N=len(levs) - 1,)

    # initialize figure
    plt.figure(figsize=(col_num / 96, row_num / 96), dpi=96)
    # remove margins , # this helps to maintain the ticks to be odd
    ax = plt.axes([0, 0, 1, 1])
    plt.imshow(data01, cmap=my_cmap, interpolation='nearest',
               vmin=lower_lim, vmax=upper_lim, aspect='auto')  # plot heatmap

    # little trick to create custom tick labels.
    # [ only works if the difference between col and row is 100 (cols - rows = 100), fails for (300,150) & (300,100) etc]

    # calculate the major tick locations
    locaters = col_num // 4
    ax.xaxis.set_major_locator(MultipleLocator(locaters))
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

    # Draw a horizontal line through the midpoint.
    plt.axvline(color='black', linestyle='--', x=locs[mid], linewidth=2)

    print "\n DEBUG INFO \n locs : {} \n length_locs : {} \n labels : {} \n length_labels:{}\n".format(
        locs, len(locs), labels, len(labels))

    plt.yticks([])
    plt.xlabel(xlabel, fontsize=14)
    ylabel = "{:,}".format(sites) + " sites"
    plt.ylabel(ylabel, fontsize=14)
    plt.title(heatmapTitle, fontsize=18)

    # to increase the width of the plot borders
    plt.setp(ax.spines.values(), linewidth=2)

    plt.savefig(out_file_name, bbox_inches='tight',
                pad_inches=0.05, frameon=False, dpi=ddpi)


def plot_colorbar(data01, c, out_file_name, row_num, col_num, categories):

    # initialize color
    levs = range(100)
    assert len(levs) % 2 == 0, 'N levels must be even.'

    # select colors from color list
    my_cmap = mcolors.LinearSegmentedColormap.from_list(
        name='white_sth', colors=c, N=len(levs) - 1,)

    # initialize figure
    fig = plt.figure(figsize=(col_num / 96, row_num / 96), dpi=300)
    # remove margins , # this helps to maintain the ticks to be odd
    ax = plt.axes([0, 0, 1, 1])
    plt.imshow(data01, cmap=my_cmap, interpolation='nearest',
               aspect='auto')  # plot heatmap
    plt.xticks([])
    plt.yticks([])

    # to increase the width of the plot borders
    plt.setp(ax.spines.values(), linewidth=2)

    # calculate how long the color box should be for each by setting up a ratio: (this site)/(total sites) = (height of unknown box)/(feature box height)
    totalsites = sum(categories)
    rpheight = categories[0] / totalsites * data01.shape[0]
    stmheight = categories[1] / totalsites * data01.shape[0]
    srgheight = categories[2] / totalsites * data01.shape[0]
    cycheight = categories[3] / totalsites * data01.shape[0]
    cofheight = categories[4] / totalsites * data01.shape[0]
    unbheight = categories[5] / totalsites * data01.shape[0]
    # print "cofheight: {}, unbheight : {}".format(unbheight, cofheight)

    # now calculate the "top" location of each box, each top should be the ending position of the previous box
    topstm = rpheight
    topsrg = topstm + stmheight
    topcyc = topsrg + srgheight
    topcof = topcyc + cycheight
    topunb = topcof + cofheight

    # find the actual position of the numbers by centering the numbers in the colored boxes and applying an arbitrary offset
    rppos = int(rpheight / 2)
    stmpos = int(stmheight / 2 + topstm)
    srgpos = int(srgheight / 2 + topsrg)
    cycpos = int(cycheight / 2 + topcyc)
    cofpos = int(cofheight / 2 + topcof)
    unbpos = int(unbheight / 2 + topunb)

    # positions for the values
    print "rp: {}, stm: {}, ess : {}, cof : {}, unb : {}, trna : {}".format(
        rppos, stmpos, srgpos, cycpos, cofpos, unbpos)

    # The default transform specifies that text is in data co-ordinates, that is even though the
    # image is compressed , the point are plotted based on datapoint in (x,y) like a graph

    # Assigning the rotation based on minimum value
    if min(categories) == categories[0]:
        if categories[0] != 0:
            plt.text(25, rppos, categories[0], horizontalalignment='center',
                     verticalalignment='center', fontsize=10, color='white', weight='bold')
    else:
        plt.text(25, rppos, categories[0], horizontalalignment='center',
                 verticalalignment='center', fontsize=10, color='white', weight='bold')

    # Assigning the rotation based on minimum value
    if min(categories) == categories[1]:
        if categories[1] != 0:
            plt.text(25, stmpos, categories[1], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='black', weight='bold')
    else:
        plt.text(25, stmpos, categories[1], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='black', rotation=90, weight='bold')

    # Assigning the rotation based on minimum value
    if min(categories) == categories[2]:
        if categories[2] != 0:
            plt.text(25, srgpos, categories[2], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='white', weight='bold')
    else:
        plt.text(25, srgpos, categories[2], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='white', rotation=90, weight='bold')

    # Assigning the rotation based on minimum value
    if min(categories) == categories[3]:
        if categories[3] != 0:
            plt.text(25, cycpos, categories[3], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='white', weight='bold')
    else:
        plt.text(25, cycpos, categories[3], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='white', rotation=90, weight='bold')

    # Assigning the rotation based on minimum value
    if min(categories) == categories[4]:
        if categories[4] != 0:
            plt.text(25, cofpos, categories[4], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='white', weight='bold')
    else:
        plt.text(25, cofpos, categories[4], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='white', rotation=90, weight='bold')

    # Assigning the rotation based on minimum value
    if min(categories) == categories[5]:
        if categories[5] != 0:
            plt.text(25, unbpos, categories[5], horizontalalignment='center',
                     verticalalignment='center', fontsize=10, color='white', weight='bold')
    else:
        plt.text(25, unbpos, categories[5], horizontalalignment='center',
                 verticalalignment='center', fontsize=10, color='white', rotation=90, weight='bold')

    # removing all the borders and frame
    for item in [fig, ax]:
        item.patch.set_visible(False)

    # saving the file
    with open(out_file_name, 'w') as outfile:
        fig.canvas.print_png(outfile)


def load_Data(input_file, out_file, upper_lim, lower_lim, color, header, start_col, row_num, col_num, ticks, ddpi, xlabel, heatmapTitle, generateColorbar):
    data = open(input_file, 'r')
    if header == 'T':
        data.readline()

    data0 = []
    dataGenes = []  # to store colorbar data
    # to store counts for RP, SAGA  and TFIID
    catergoryCount = [0, 0, 0, 0, 0, 0]
    sites = 0  # to calculate the # of sites in the heatmap
    for rec in data:
        tmp = [(x.strip()) for x in rec.split('\t')]
        sites = sites + 1
        if generateColorbar == '1':
            rankOrder = int(rec.split("\t")[0])
            if rankOrder <= 19999:
                dataGenes.append([1] * len(tmp[start_col:]))
                catergoryCount[0] = catergoryCount[0] + 1
            elif rankOrder <= 29999 and rankOrder >= 20000:
                dataGenes.append([2] * len(tmp[start_col:]))
                catergoryCount[1] = catergoryCount[1] + 1
            elif rankOrder <= 39999 and rankOrder >= 30000:
                dataGenes.append([3] * len(tmp[start_col:]))
                catergoryCount[2] = catergoryCount[2] + 1
            elif rankOrder <= 49999 and rankOrder >= 40000:
                dataGenes.append([4] * len(tmp[start_col:]))
                catergoryCount[3] = catergoryCount[3] + 1
            elif rankOrder <= 59999 and rankOrder >= 50000:
                dataGenes.append([5] * len(tmp[start_col:]))
                catergoryCount[4] = catergoryCount[4] + 1
            elif rankOrder <= 219999 and rankOrder >= 210000:
                dataGenes.append([6] * len(tmp[start_col:]))
                catergoryCount[5] = catergoryCount[5] + 1
        data0.append(tmp[start_col:])

    data0 = np.array(data0, dtype=float)
    print "# sites in the heatmap", sites

    # creating the np-array to plot the colorbar
    dataGenes = np.array(dataGenes, dtype=float)
    print "catergoryCount : {}".format(catergoryCount)

    if row_num == -999:
        row_num = data0.shape[0]
    if col_num == -999:
        col_num = data0.shape[1]

    # rebin data0 (compresses the data using treeView compression algorithm)
    if row_num < data0.shape[0] and col_num < data0.shape[1]:
        data0 = rebin(data0, (row_num, col_num))
        if generateColorbar == '1':
            # i have hard-coded the width for colorbar(50)
            dataGenes = rebin(dataGenes, (row_num, 50))
    elif row_num < data0.shape[0]:
        data0 = rebin(data0, (row_num, data0.shape[1]))
        if generateColorbar == '1':
            dataGenes = rebin(dataGenes, (row_num, 50))
    elif col_num < data0.shape[1]:
        data0 = rebin(data0, (data0.shape[0], col_num))
        if generateColorbar == '1':
            dataGenes = rebin(dataGenes, (data0.shape[0], 50))

    # set color here
    # convert rgb to hex (since matplotlib doesn't support 0-255 format for colors)
    s = color.split(",")
    color = '#{:02X}{:02X}{:02X}'.format(int(s[0]), int(s[1]), int(s[2]))
    c = ["white", color]

    # generate heatmap
    plot_heatmap(data0, c, out_file, upper_lim, lower_lim, row_num,
                 col_num, ticks, ddpi, xlabel, heatmapTitle, sites)

    # checking if we need to plot the color bar
    if generateColorbar == '1':
        print "Creating the colobar"
        mycolors = ['#ff2600', '#ffd54f', '#43a047',
                    '#0096ff', '#9437ff', '#9e9e9e']
        colors = []

        # deciding colors based on the catergory values.
        for i in range(0, len(catergoryCount)):
            if catergoryCount[i] != 0:
                colors.append(mycolors[i])

        plot_colorbar(dataGenes, colors, "colorbar.png",
                      900, 35, catergoryCount)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='tagPileUp input')
    parser.add_argument('threshold', help='thresphold file')
    parser.add_argument('color', help='color in rgb')
    parser.add_argument('rows', help='The height of the heatmap')
    parser.add_argument('columns', help='The width of the heatmap')
    parser.add_argument('ticks', help='The axis start and end')
    parser.add_argument(
        'DPI', help='The dpi (pixels per inch) for the output image')
    parser.add_argument('xlabel', help='The Label under the x-axis')
    parser.add_argument('heatmapTitle', help='Heatmap Title')
    parser.add_argument(
        'generateColorbar', help='Do you want to generate colorbar (0 : False; 1: True)')
    parser.add_argument('outfilename', help='outfilename')
    args = parser.parse_args()

    params = {}
    openfile = open(args.threshold, 'r').readlines()
    for line in openfile:
        line = line.strip()
        temp = line.split(":")
        if temp[0] not in params.keys():
            params[temp[0]] = temp[1]

    print " \n Parameters for the heatmap"
    pprint.pprint(params)
    upper_lim = float(params['upper_threshold'])
    lower_lim = int(params['lower_threshold'])
    header = params['header']
    start_col = int(params['start_col'])
    row_num = int(args.rows)
    col_num = int(args.columns)

    load_Data(args.input, args.outfilename, upper_lim, lower_lim, args.color, header,
              start_col, row_num, col_num, args.ticks, int(args.DPI), args.xlabel, args.heatmapTitle, str(args.generateColorbar))
