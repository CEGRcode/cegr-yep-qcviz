#!/usr/bin/python

"""
Program that takes the output from bedtools genomecov and removes 2-micron regions
and also adds a unique name to each bedGraph file.

Then creates the bigWig file utilizing the binary provided by UCSC.

references:
-----------
Reference to covert decimal to roman
https://stackoverflow.com/questions/28777219/basic-program-to-convert-integer-to-roman-numerals

genomeCoverage : https://bedtools.readthedocs.io/en/latest/content/tools/genomecov.html
To create the bedgraph style output, you can do stand specific, fragment size and stuff

"""

from collections import OrderedDict
import pandas as pd
import argparse


def write_roman(num):

    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'genomeCoverageBed', help='bedtools genomeCoverageBed output file using (-bga) (strand) options')
    parser.add_argument(
        'strand', help="Strand information takes + or - , by default assumes + ")
    args = parser.parse_args()

    data = []  # used to store the file contents as a list of lists
    filecontents = []
    header = []  # contains 2-microns and other wrongly formated lines

    # reading the genomeCoverageBed output file
    openfile = open(args.genomeCoverageBed, 'r').readlines()

    # reading each line and converting the chromosome numbers to ROMAN equivalents
    for line in openfile:
        if line.startswith("chr"):
            temp = line.strip().split("\t")

            # checking the strand information
            if args.strand == '-':
                #  checking if it is chrM
                if temp[0][3:] != 'M':
                    # getting the chr number and converting to romans
                    romanValue = write_roman(int(temp[0][3:]))
                    temp[0] = "chr" + str(romanValue)
                    if temp[3] > 0:
                        temp[3] = str(-int(temp[3]))
                    # print temp
                    filecontents.append(temp)
                else:
                    filecontents.append(temp)
            # In the case of reverse strand
            else:
                if temp[0][3:] != 'M':
                    # getting the chr number and converting to romans
                    romanValue = write_roman(int(temp[0][3:]))
                    temp[0] = "chr" + str(romanValue)
                    # print temp
                    filecontents.append(temp)
                else:
                    filecontents.append(temp)

        # removing 2-microns, which is not recognized by the UCSC browser
        else:
            if line.startswith("2-micron") is False:
                header.append(line)

    data = pd.DataFrame(filecontents, columns=(
        'chr', 'start', 'end', 'genome_coverage'))
    print data[0:10]
    data.to_csv('processed.bedGraph', sep='\t', header=False, index=False)
