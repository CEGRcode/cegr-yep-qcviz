#!/usr/bin/python

import pandas as pd
import argparse

"""
Program to sort the tagpileup heatmap frequencies based on totalTagCount
"""


def sortData(sense):
    """
    Function to read, calculate total tag count, sort data based on the total tag count and finally create the new CDT tabular files for Heatmaps.
    """

    # reading the sense Heatmap frequencies
    sdata = pd.read_csv(sense, sep="\t")

    # creating a combined dataframe to find total tag count.
    combined = sdata
    combined['sum'] = combined[combined.columns[2:]].sum(
        axis=1)  # summing each row

    # sort in the descending order of the sum for each row.
    combinedSort = combined.sort_values(
        by='sum', ascending=False, na_position='first')

    print combinedSort[0:10]
    # removing the sum column after sorting, so that data can be written into new tabular file.
    data = combinedSort.drop(['sum'], axis=1)

    # basic DEBUG
    # print combinedSort[0:10]
    # print combinedSort['sum']
    # print combinedSort.columns
    # print str(sdata.loc[42].sum() + adata.loc[42].sum())
    # print combinedSort.index

    data.to_csv('totalTagSorted.tabular', sep='\t', header=True, index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('heatmapTabular', help='Heatmap tabular file')
    args = parser.parse_args()

    # creating the totaltag sorted tabular
    sortData(args.heatmapTabular)
