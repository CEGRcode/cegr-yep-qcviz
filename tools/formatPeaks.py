#!/usr/bin/python

"""
Program that takes chexmix peaks and formats them to UCSC specifications
Removes 2-micron if present
Expands the peaks to certain bp if needed (for better browser visualization)
"""
from __future__ import division
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
        'peakFile', help='Peak bed file from chexmix')
    parser.add_argument(
        'expandWindow', help="expandWindow in bp, expands on both sides if non-zero")
    args = parser.parse_args()

    data = []  # used to store the file contents as a list of lists
    filecontents = []
    header = []  # contains 2-microns and other wrongly formated lines

    # reading the genomeCoverageBed output file
    openfile = open(args.peakFile, 'r').readlines()

    # reading each line and converting the chromosome numbers to ROMAN equivalents
    for line in openfile:
        if line.startswith("chr"):
            temp = line.strip().split("\t")

            if temp[0][3:] != '2-micron':
                # checking the strand information
                if int(args.expandWindow) > 0:
                    #  checking if it is chrM
                    if temp[0][3:] != 'M':
                        # getting the chr number and converting to romans
                        romanValue = write_roman(int(temp[0][3:]))
                        temp[0] = "chr" + str(romanValue)

                        # calculating the new start and end
                        mid = int((int(temp[1]) + int(temp[2])) // 2)
                        ns = mid - int(args.expandWindow)
                        ne = mid + int(args.expandWindow)

                        temp[1] = ns
                        temp[2] = ne

                        filecontents.append(temp)
                    else:
                        filecontents.append(temp)
                else:
                    #  checking if it is chrM
                    if temp[0][3:] != 'M':
                        # getting the chr number and converting to romans
                        romanValue = write_roman(int(temp[0][3:]))
                        temp[0] = "chr" + str(romanValue)
                        filecontents.append(temp)
                    else:
                        filecontents.append(temp)

            # removing 2-microns, which is not recognized by the UCSC browser
            else:
                if line.startswith("2-micron") is False:
                    header.append(line)

    data = pd.DataFrame(filecontents)
    print data[0:10]
    data.to_csv('formatedPeaks.bed', sep='\t', header=False, index=False)
