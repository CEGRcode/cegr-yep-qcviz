#!/usr/bin/python

"""
creates the sorted bed file for 4 color plots
"""

import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'fimoBed', help='Bed file generated from FIMO interval file.')
    parser.add_argument(
        'totalTagRankOrder', help='totalTagRankOrder.txt file generated from makeMotifHeatmap script')
    args = parser.parse_args()

    # reading the fimo bed.
    openfile = open(args.fimoBed, 'r').readlines()
    dataDict = {}  # dictionary to store the data based on rankOrder
    for line in openfile:
        temp = line.split("\t")
        if str(temp[3]) not in dataDict.keys():
            dataDict[str(temp[3])] = line
        else:
            print(" Skipping : {}".format(line))

    # reading the rankOrder
    rankOrder = open(args.totalTagRankOrder, 'r').readlines()[
        0].strip().split(",")
    # pprint.pprint(rankOrder)

    outfile = open('fourcolor.bed', 'w')
    for i in rankOrder:
        outfile.write(dataDict[i])
    outfile.flush()
    outfile.close()
