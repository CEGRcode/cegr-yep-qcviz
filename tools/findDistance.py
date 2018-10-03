#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 11th June, 2018
#
# last modified : 3rd October, 2018
#

"""
Finds the closest feature from the reference bedfile for each peak in input bedfile
and sorts the features from most upstream to downstream. (chooses the nearest distance as the smallest absolute distance in case there is more than one region)
"""

from __future__ import division
import argparse
import os
import sys
import pprint
import pandas as pd


def getMidPoints(peakfile, refFeature):
    """
    function to calculate the midpoint for both the peaks and refFeature
    """
    pfile = open(peakfile, 'r').readlines()
    if pfile[0].startswith('chr') is not True:
        pfile.pop(0)
        # pprint.pprint(pfile.pop(0)) # removing the first line from the peaks bed file

    peaks = []
    for line in pfile:
        line = line.strip()
        temp = line.split("\t")

        # calculating mid point
        mid = int((int(temp[1]) + int(temp[2])) / 2)
        # print "{}\t{}\t{}\t{}\t{}\t{}".format(temp[0],temp[1],temp[2],mid,temp[3],temp[4])
        peaks.append([temp[0], temp[1], temp[2], mid, temp[3], temp[4]])

    # #DEBUG
    # pprint.pprint(peaks)

    features = []
    rfile = open(refFeature, 'r').readlines()
    for line in rfile:
        line = line.strip()
        temp = line.split("\t")
        mid = int((int(temp[1]) + int(temp[2])) / 2)
        # print "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(temp[0],temp[1],temp[2],mid,temp[3],temp[4],temp[5])
        features.append([temp[0], temp[1], temp[2],
                         mid, temp[3], temp[4], temp[5]])

    return [peaks, features]


def findDistance(peaks, features, feat):
    """
    Function to find the distance between Features and peaks
    """
    print "No of Bound Features : "
    pprint.pprint(len(features))
    print "No of PEAKS : "
    pprint.pprint(len(peaks))

    # calculating the distance between each region, using strand information also
    Closest = []
    for r in features:
        # pprint.pprint(r)
        for p in peaks:
            if r[0] == p[0]:  # checking for same chromosome
                if r[6] == '+':  # checking for strand of the feature
                    # pprint.pprint(r)
                    dist = r[3] - p[3]
                    Closest.append([r[0], r[1], r[2], r[3], r[4], r[5],
                                    r[6], p[0], p[1], p[2], p[3], p[4], p[5], dist])
                else:
                    dist = p[3] - r[3]
                    Closest.append([r[0], r[1], r[2], r[3], r[4], r[5],
                                    r[6], p[0], p[1], p[2], p[3], p[4], p[5], dist])
    # #DEBUG
    # print "Closest\n"
    # pprint.pprint(len(Closest))
    # pprint.pprint(Closest[0:5])
    # pprint.pprint(Closest)
    data = pd.DataFrame(Closest, columns=['chrom1', 'str1', 'stp1', 'mid1', 'r1',
                                          'l1', 'strand', 'chrom2', 'str2', 'stp2', 'mid2', 'r2', 'l2', 'distance'])
    # print data[0:4]

    # removing the duplicates
    # sdata = pd.DataFrame(data.sort_values(by='distance',ascending=False,na_position='first'))
    # print sdata[0:5]

    # dictionary to store the multiple distances for each id
    idDict = {}

    # dictionary to store the absolute distance values for each of the id.
    abdIdDict = {}

    # Iterating through the DataFrame to choose the closest
    for index, row in data.iterrows():
        # print "{}\t{}\n".format(row['id'],row['distance'])
        if row['r1'] not in idDict.keys():
            idDict[row['r1']] = []
            idDict[row['r1']].append(row['distance'])
        else:
            idDict[row['r1']].append(row['distance'])
        # absolute dictionary
        if row['r1'] not in abdIdDict.keys():
            abdIdDict[row['r1']] = []
            abdIdDict[row['r1']].append(abs(row['distance']))
        else:
            abdIdDict[row['r1']].append(abs(row['distance']))

    # Removing duplicates, choosing the nearest distance as the smallest absolute distance (in case there is more than one match)
    for k, v in abdIdDict.items():
        # print "{}\t{}".format(k,min(v))
        value = min(v)
        if value in idDict[k]:
            idDict[k] = value
        elif -value in idDict[k]:
            idDict[k] = -value

    # pprint.pprint(idDict[0:5])
    print " No of regions after choosing the smallest absolute distance : "
    pprint.pprint(len(idDict.keys()))
    # pprint.pprint(len(abdIdDict.keys()))
    # pprint.pprint(idDict)

    # creating a dataframe from dictionary, so that it can be sorted based on distance
    iddata = pd.DataFrame(idDict.items(), columns=['id', 'distance'])
    # print iddata.loc[0:10]

    # sorting the bed file based on distance (+ values) to (- values)
    sdata = pd.DataFrame(iddata.sort_values(
        by='distance', ascending=True, na_position='first'))
    # print sdata[0:10]
    print " Snapshot of the data : "
    print sdata

    # to store the bedfile regions to create the final sorted bedfile.
    featureDict = {}
    # reading the features file and creating a dict to write the bedfile
    featureFile = open(feat, 'r').readlines()
    for f in featureFile:
        # pprint.pprint(f.split("\t"))
        temp = f.split("\t")
        featureDict[temp[3]] = f
    # pprint.pprint()

    # creating the final bedfile to make the heatmap
    outfile = open("finalDist.bed", 'w')
    for index, row in sdata.iterrows():
        # print "{}\t{}\n".format(row['id'],row['distance'])
        value = str(row['id']).strip()
        if value in featureDict.keys():
            outfile.write(featureDict[value])
        else:
            print "NOT FOUND :{}".format(row['id'])
    outfile.flush()
    outfile.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('peakFile', help='multiGPS peak file in bed format')
    parser.add_argument(
        'boundFeatures', help='boundFeatures that are handPicked')
    parser.add_argument(
        'refFeature', help='Main bedfile to pick regions to make the final bedfile to plot')
    args = parser.parse_args()

    # reading the files for feature count
    boundData = open(args.boundFeatures,'r').readlines()
    refData = open(args.refFeature,'r').readlines()


    if len(boundData) == len(refData):
        print "Bound Features are EQUAL to the REFERENCE FEATURE, returning the REFERENCE BED to plot"
        # creating the final bedfile to make the heatmap
        outfile = open("finalDist.bed", 'w')
        for line in refData:
            outfile.write(line)
        outfile.flush()
        outfile.close()

    else:
        print "Bound Features are Less than the REFERENCE FEATUREs, calculating the distance "
        # retrieve the mid points before calculating distances.
        [peaks, features] = getMidPoints(args.peakFile, args.boundFeatures)
        # calculate distance and create the final file
        findDistance(peaks, features, args.refFeature)
