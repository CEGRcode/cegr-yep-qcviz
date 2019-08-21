#!/usr/bin/python

"""
Program to convert the FIMO (interval) output to BED file for each motif that was discovered.

NOTES
-----
Converts below text file output from FIMO

#chr	start	end	pattern name	score	strand	matched sequence	p-value	   q-value
chr16	260987	261003	2	           +	    +	0.000292	         23.2065	7.03e-10
chr5	394966	394982	2	           +	    +	0.000292	         23.2065	7.03e-10
chr12	704452	704468	2	           +	    +	0.000292	         23.2065	7.03e-10
chr11	237418	237434	2	           -	    +	0.000292	         23.2065	7.03e-10
chr4	332979	332995	2	           -	    +	0.000292	         23.2065	7.03e-10
chr14	359577	359593	2	           -	    +	0.000292	         23.2065	7.03e-10
chr2	452268	452284	2	           -	    +	0.000292	         23.2065	7.03e-10
chr13	852304	852320	2	           -	    +	0.000292	         23.2065	7.03e-10
chr7	982253	982269	2	           -	    +	0.000292	         23.2065	7.03e-10

TO

chrom   start   end     name    p-value   strand
chr16	260983	261007	2	23.2065	+
chr5	394962	394986	2	23.2065	+
chr12	704448	704472	2	23.2065	+
chr11	237414	237438	2	23.2065	-
chr4	332975	332999	2	23.2065	-
chr14	359573	359597	2	23.2065	-
chr2	452264	452288	2	23.2065	-
chr13	852300	852324	2	23.2065	-
chr7	982249	982273	2	23.2065	-
chr2	36503	36527	2	22.9239	+

"""
from __future__ import division
import pandas as pd
import argparse
import os


def processText(fimoFile):
    """
    Function to convert the fimo text file to a bed file
    """
    # reading the fimo text file
    Fdata = pd.read_csv(fimoFile, sep="\t", index_col=False)

    # checking for unique motif names, usually [1,2,3...so on]
    for i in Fdata['pattern name'].unique():
        data = Fdata.loc[Fdata['pattern name'] == i]
        # print data[0:10]
        customRankOrder = 0
        # Creating individual bedfiles
        outfile = open('./output/Motif_' + str(i) + '.bed', 'w')
        for index, row in data.iterrows():
            # remove 2-micron
            if row['#chr'] != '2-micron':
                # Check if the length of the motif is (even/odd)
                if (int(row['start'] + row['end']) % 2 == 0):
                    mid = int(int(row['start'] + row['end']) // 2)
                    newS = mid - 20
                    newE = mid + 20
                    if newS <= 0 or newE <= 0:
                        continue
                    else:
                        customRankOrder = customRankOrder + 1
                        outfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                            row['#chr'], newS, newE, customRankOrder, row['p-value'], row['score']))
                else:
                    # Strand of the motif is (+/-) strand
                    if row['score'] == '+':
                        # print "POSITIVE"
                        mid = int(int(row['start'] + row['end']) // 2)
                        newS = mid - 20
                        newE = mid + 20
                        if newS <= 0 or newE <= 0:
                            continue
                        else:
                            customRankOrder = customRankOrder + 1
                            outfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                                row['#chr'], newS, newE, customRankOrder, row['p-value'], row['score']))
                    else:
                        # print "NEGATIVE"
                        mid = int(int(row['start'] + row['end']) // 2)
                        newS = mid - 19
                        newE = mid + 21
                        if newS <= 0 or newE <= 0:
                            continue
                        else:
                            customRankOrder = customRankOrder + 1
                            outfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                                row['#chr'], newS, newE, customRankOrder, row['p-value'], row['score']))
        outfile.flush()
        outfile.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('fimoText', help='FIMO text output File')

    args = parser.parse_args()

    # create the output folder if it doesn't exist
    if os.path.exists("./output"):
        print "Using the existing output directory"
        # pass
    else:
        print "creating the output directory"
        os.mkdir("./output")

    processText(args.fimoText)
