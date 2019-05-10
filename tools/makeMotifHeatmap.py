#!/usr/bin/python

from __future__ import division
import pandas as pd
import argparse
import pprint

"""
Program to make the Motif heatmaps.
"""


def sortData(sense, anti):
    """
    Function to read, calculate total tag count, sort data based on the total tag count and finally create the new CDT tabular files for Motif Heatmaps.
    """

    # reading the sense Heatmap frequencies
    sdata = pd.read_csv(sense, sep="\t")

    # reading the antisense heatmap frequencies
    adata = pd.read_csv(anti, sep="\t")

    # creating a combined dataframe to find total tag count.
    combined = pd.concat([sdata, adata[adata.columns[2:]]], axis=1)
    combined['sum'] = combined[combined.columns[2:]].sum(
        axis=1)  # summing each row

    # sort in the descending order of the sum for each row.
    combinedSort = combined.sort_values(
        by='sum', ascending=False, na_position='first')

    # removing the sum column after sorting, so that data can be written into new tabular file.
    data = combinedSort.drop(['sum'], axis=1)

    # basic DEBUG
    # print combinedSort[0:10]
    # print combinedSort['sum']
    # print combinedSort.columns
    # print str(sdata.loc[42].sum() + adata.loc[42].sum())
    # print combinedSort.index

    # adding a dummy header
    header = "YORF\tNAME\tthis_is_a_dummy_header_ignore_when_reading_this_file"

    # converting the values in the data frame to string and writing the data to file in sorted order for sense strand.
    data = sdata.applymap(str)
    outfile = open('senseData.tabular', 'w')
    outfile.write(header + "\n")
    customRankOrder = []  # to store the total tag count order
    for index, row in combinedSort.iterrows():
        # pprint.pprint("\t".join(list(data.loc[index])))
        customRankOrder.append(list(data.loc[index])[1])
        string = "\t".join(list(data.loc[index]))
        outfile.write(string + "\n")
    outfile.flush()
    outfile.close()

    # #DEBUG
    pprint.pprint(customRankOrder)

    # creating the csv that stores the rankOrder to be used in FourColorplot
    outfile = open('totalTagOrder.txt', 'w')
    string = ",".join(customRankOrder)
    outfile.write(string + "\n")
    outfile.flush()
    outfile.close()

    # converting the values in the data frame to string and writing the data to file in sorted order for anti-sense strand.
    data = adata.applymap(str)
    outfile = open('antisenseData.tabular', 'w')
    outfile.write(header + "\n")
    for index, row in combinedSort.iterrows():
        # pprint.pprint("\t".join(list(data.loc[index])))
        string = "\t".join(list(data.loc[index]))
        outfile.write(string + "\n")
    outfile.flush()
    outfile.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'firstCatergory', help='Catergory of input (sense/anti), used to do head on data')
    parser.add_argument('sense', help='sense tabular')
    parser.add_argument(
        'secondCatergory', help='Catergory of input (sense/anti), used to do head on data')
    parser.add_argument('antisense', help='anti-sense tabular')
    args = parser.parse_args()

    pprint.pprint(args)

    print "First Category : {}".format(args.firstCatergory)
    print "Second Category : {}".format(args.secondCatergory)
    sortData(args.sense, args.antisense)
