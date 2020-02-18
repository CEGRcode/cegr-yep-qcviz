#!/usr/bin/python

"""
Returns a pre-determined bedfile if #peaks "called" by ChExMix
are less than or equal to the peakThreshold o/w returns the peaks.
"""

import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'peaks', help='bedfile output from ChExMix or any peak caller')
    parser.add_argument(
        'refFeature', help='pre-determined bedfile that will be returned in case of peaks < threshold')
    parser.add_argument('peakThreshold', type=int,
                        help='Threshold to determine the output')
    args = parser.parse_args()

    # reading the number of lines in the input peak file
    openfile = open(args.peaks, 'r').readlines()

    peakList = []  # to remove 2-micron from called peaks
    for line in openfile:
        temp = line.split("\t")
        if temp[0] != "chr2-micron":
            peakList.append(line)

    # checking the threshold for peaks
    if len(peakList) <= args.peakThreshold or peakList[0] == '\n' or len(peakList) == 0:
        print(" The number of peaks found : {}  <= to the requested peakThreshold of {} \n Returning the pre-determined bedfile".format(len(peakList), args.peakThreshold))

        if len(peakList) <= 10:
            print("\n INPUT PEAK FILE CONTAINS !\n")
            for line in openfile:
                print(line.strip())

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

        print(" Creating the bedfile for 'calledPeaks'  !")
        for line in peakList:
            outfile.write(line)
        outfile.flush()
        outfile.close()
