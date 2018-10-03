#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 10th August,2018
#
# last modified : 1st October, 2018
#
"""
Returns a pre-determined bedfile if #peaks "called" by multiGPS
are less than or equal to the peakThreshold o/w returns the peaks.
"""

import argparse
import pprint


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'multigpsPeaks', help='peak bedfile output from multiGPS')
    parser.add_argument(
        'refFeature', help='pre-determined bedfile that will be returned in case of peaks < threshold')
    parser.add_argument('peakThreshold', type=int,
                        help='Threshold to determine the output')
    args = parser.parse_args()

    # reading the number of lines in the input peak file
    openfile = open(args.multigpsPeaks, 'r').readlines()

    peakList = [] # to remove 2-micron from called peaks
    for line in openfile:
        temp = line.split("\t")
        if temp[0] != "chr2-micron":
            peakList.append(line)

    #print len(peakList)
    #pprint.pprint(peakList)

    # checking the threshold for peaks
    if len(peakList) <= args.peakThreshold or peakList[0] == '\n' or len(peakList) == 0:
        print " The number of peaks found : {} is less or equal to the requested peakThreshold : {} \n Returning the pre-determined bedfile".format(len(peakList), args.peakThreshold)

        if len(peakList) <= 10:
            print "\n INPUT PEAK FILE CONTAINS !\n"
            for line in openfile:
                print line

        # creating the pre-determined bedfile
        ffeatures = open(args.refFeature, 'r').readlines()
        outfile = open("peaks.bed", 'w')
        for line in ffeatures:
            outfile.write(line)
        outfile.flush()
        outfile.close()
    else:
        # returning the "called" peak file
        outfile = open("peaks.bed", 'w')

        print " Creating the bedfile for 'calledPeaks'  !"
        for line in peakList:
            outfile.write(line)
        outfile.flush()
        outfile.close()
