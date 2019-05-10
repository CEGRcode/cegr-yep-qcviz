#!/usr/bin/python

"""
Program to Create a subsector bound bedfile before doing tag pileup
"""
import pandas as pd
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'sectorRankorder', help='File containing the rank order for genes')
    parser.add_argument(
        'refFeature', help='Bed file to pick the regions based on the rank order in sector file')
    parser.add_argument(
        'sectorThreshold', help='minimum sectors that need to be found for further steps')
    args = parser.parse_args()

    # list containing the gene rank_orders that will be extracted from refFeature
    extractOrder = []

    # reading the subsector rank_orders
    sectorfile = open(args.sectorRankorder, 'r').readlines()

    # reading the referenceFeature
    refData = pd.read_csv(args.refFeature, sep='\t', names=[
                          'chrom', 'str', 'stp', 'Rank_Order', 'experimentLength', 'strand'])

    # checking for duplicates and removing trailing newline characters
    for line in sectorfile:
        if line.strip() not in extractOrder:
            extractOrder.append(line.strip())
        else:
            print "EXISTS : {}".format(line)

    # #DEBUG
    print "\n Subsector Rank Order :\n {}".format(extractOrder[0:10])

    print "\n Reference Feature Data :\n {} ".format(refData[0:10])

    # extracting the features in the same order
    boundFeatures = refData.loc[refData['Rank_Order'].isin(extractOrder)]
    print "\n Bound Feature Data :\n {} ".format(boundFeatures[0:10])

    # checking if there are any boundFeatures found
    if len(boundFeatures) > int(args.sectorThreshold):
        # creating the boundSectors bedfile
        bfFile = open("boundSubSectors.bed", 'w')
        print "\n Creating the boundFeatures file ! "
        for index, row in boundFeatures.iterrows():
            # print "{}\t{}\t{}\t{}\t{}\t{}".format(row['chrom'],row['str'],row['stp'],row['Rank_Order'],row['category'],row['strand'])
            bfFile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                row['chrom'], row['str'], row['stp'], row['Rank_Order'], row['experimentLength'], row['strand']))
        bfFile.flush()
        bfFile.close()
    else:
        # returning the reference bedfile, since there are zero bound features
        bfFile = open("boundSubSectors.bed", 'w')
        print "\n Zero bound features found ! returning Reference feature file ! "
        for index, row in refData.iterrows():
            # print "{}\t{}\t{}\t{}\t{}\t{}".format(row['chrom'],row['str'],row['stp'],row['Rank_Order'],row['category'],row['strand'])
            bfFile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                row['chrom'], row['str'], row['stp'], row['Rank_Order'], row['experimentLength'], row['strand']))
        bfFile.flush()
        bfFile.close()
