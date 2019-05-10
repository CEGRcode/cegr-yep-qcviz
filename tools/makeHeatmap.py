#!/usr/bin/python
from __future__ import division
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import matplotlib
import math
import argparse
import pprint

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

    matplotlib.rcParams['font.family'] = "Arial"

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
    plt.tick_params(length=8, width=2)

    # Draw a horizontal line through the midpoint.
    plt.axvline(color='black', linestyle='--', x=locs[mid], linewidth=2)

    print "\n DEBUG INFO \n locs : {} \n length_locs : {} \n labels : {} \n length_labels:{}\n".format(locs, len(locs), labels, len(labels))

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
    sagaheight = categories[1] / totalsites * data01.shape[0]
    tfiidheight = categories[2] / totalsites * data01.shape[0]

    # now calculate the "top" location of each box, each top should be the ending position of the previous box
    topsaga = rpheight
    toptfiid = topsaga + sagaheight

    # find the actual position of the numbers by centering the numbers in the colored boxes and applying an arbitrary offset
    rppos = int(rpheight / 2)
    sagapos = int(sagaheight / 2 + topsaga)
    tfiidpos = int(tfiidheight / 2 + toptfiid)

    # positions for the values
    print "r: {}, s: {}, tf2d : {}".format(rppos, sagapos, tfiidpos)

    # The default transform specifies that text is in data co-ordinates, that is even though the
    # image is compressed , the point are plotted based on datapoint in (x,y) like a graph

    # Assigning the rotation based on minimum value
    if min(categories) == categories[0]:
        if categories[0] != 0:
            plt.text(25, rppos, categories[0], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='white')
    else:
        plt.text(25, rppos, categories[0], horizontalalignment='center',
                 verticalalignment='center', fontsize=15, color='white', rotation=90)

    # Assigning the rotation based on minimum value
    if min(categories) == categories[1]:
        if categories[1] != 0:
            plt.text(25, sagapos, categories[1], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='white')
    else:
        plt.text(25, sagapos, categories[1], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='white', rotation=90)

    # Assigning the rotation based on minimum value
    if min(categories) == categories[2]:
        if categories[2] != 0:
            plt.text(25, tfiidpos, categories[2], horizontalalignment='center',
                     verticalalignment='center', fontsize=13, color='black')
    else:
        plt.text(25, tfiidpos, categories[2], horizontalalignment='center',
                 verticalalignment='center', fontsize=16, color='black', rotation=90)

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
    catergoryCount = [0, 0, 0]  # to store counts for RP, SAGA  and TFIID
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
        colors = ['#ff0000', '#008000', '#00bfff']

        # deciding colors
        if catergoryCount[0] == 0 and catergoryCount[1] != 0 and catergoryCount[2] != 0:
            colors = ['#008000', '#00bfff']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        elif catergoryCount[1] == 0 and catergoryCount[0] != 0 and catergoryCount[2] != 0:
            colors = ['#ff0000', '#00bfff']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        elif catergoryCount[2] == 0 and catergoryCount[0] != 0 and catergoryCount[1] != 0:
            colors = ['#ff0000', '#008000']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        elif catergoryCount[0] == 0 and catergoryCount[1] == 0 and catergoryCount[2] != 0:
            colors = ['#00bfff', '#00bfff']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        elif catergoryCount[1] == 0 and catergoryCount[2] == 0 and catergoryCount[0] != 0:
            colors = ['#ff0000', '#ff0000']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        elif catergoryCount[2] == 0 and catergoryCount[0] == 0 and catergoryCount[1] != 0:
            colors = ['#008000', '#008000']
            # hard-coded the dimensions for the colorbar
            plot_colorbar(dataGenes, colors, "colorbar.png",
                          900, 35, catergoryCount)
        else:
            # hard-coded the dimensions for the colorbar
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
