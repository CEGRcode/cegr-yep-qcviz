#!/usr/bin/python

from __future__ import division
import pandas as pd
import argparse

"""
Program to expand the bed file based on user input.
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'expandlength', help='The length in base pairs added to mid point on both directions.')
    parser.add_argument('bedFile', help='anti-sense tabular')
    args = parser.parse_args()

    expandlength = int(args.expandlength)
    data = pd.read_csv(args.bedFile, sep="\t", names=[
                       'chr', 'start', 'stop', 'category', 'score', 'strand'])

    outfile = open("Motif_expanded.bed", 'w')
    for index, row in data.iterrows():
        mid = int(int(row['start'] + row['stop']) // 2)
        newS = mid - expandlength
        newE = mid + expandlength
        outfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
            row['chr'], newS, newE, row['category'], row['score'], row['strand']))
    outfile.flush()
    outfile.close()
