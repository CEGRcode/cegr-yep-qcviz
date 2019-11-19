#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 12th July, 2018
#


"""
Program to read a config file and WorkflowInvokeFile
to download all the required heatmaps and composites
for each sample in yepQcViz pipeline.

NOTES:
-----
TERMINAL colors

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

"""

import sys
import os
import argparse
import pprint
import configparser
from bioblend import galaxy

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'configFile', help='yepQcViz.conf file that has galaxy url and apikey information.')
    parser.add_argument(
        'workflowInvokeFile', help='workflowInfo.csv file that was generated by runYepQcViz.py')
    parser.add_argument(
        'chrSizeFile', help='sacCer3.chrom.sizes for bigWig and bigBed')
    parser.add_argument(
        'outputPath', help='Absolute path to the Output directory')
    args = parser.parse_args()

    if os.path.isdir(args.outputPath):
        resultsFolder = args.outputPath + "/Results"
    else:
        print("\033[91m WARNING ! Specified Output folder doesn't exist !  creating a results folder in the current directory \033[0m")
        resultsFolder = os.getcwd() + "/Results"

    # config parser to take necessary options
    config = configparser.ConfigParser()
    try:
        config.read(args.configFile)
        galaxyUrl = config['BASIC']['GALAXY_URL']
        apiKey = config['BASIC']['API_KEY']
        # list of labels to check in order to download the corresponding png
        pngList = config['DOWNLOADS']['PNG_LIST']
    except:
        print("\033[91m ERROR ! Unable to read config file or Missing the required Configuration fields or file not found ! \033[0m")
        # not so clear, so have an option to create a dummy config file with date.
        # transfer all the print statements to a log file.
        exit()

    # create the results folder that has all the images.
    try:
        if os.path.exists(resultsFolder):
            print(
                "\033[95m   Results folder exists, Using the existing folder to store images ! \033[0m")
        else:
            print("\033[95m   Creating the results folder \033[0m")
            os.mkdir(resultsFolder)
    except:
        print("\033[91m ERROR !  Unable to Create the Results folder ! \033[0m")
        # not so clear, so have an option to create a dummy config file with date.
        # transfer all the print statements to a log file.
        exit()

    # parsing through the config file and creating a galaxy instance
    gi = galaxy.GalaxyInstance(url=galaxyUrl, key=apiKey)
    print("\033[94m  \033[1m Connected to GALAXY at : {}  \033[0m \033[0m ".format(
        galaxyUrl))

    # parsing the workflowInfoFile and processing each line.
    openfile = open(args.workflowInvokeFile, 'r').readlines()
    for i in range(1, len(openfile)):
        print(" \n\n")
        # #DEBUG
        # pprint.pprint(openfile[i].split(','))
        data = openfile[i].split(',')

        # generating the path for the run folder
        runPath = resultsFolder + "/" + str(data[0])

        # generating the path for the sample folder
        samplePath = resultsFolder + "/" + \
            str(data[0]) + "/" + str(data[1]) + "_" + str(data[2])

        # Sample Details
        runNo = str(data[0])
        sampleNo = str(data[1])
        proteinName = str(data[2]).upper()

        # creating the prefix that will be added to all the downloaded files
        prefixName = sampleNo + "_"

        # to keep track of Motif specific 4colorplots,Merged heatmaps etc
        count = [0, 0, 0, 0, 0, 0, 0, 0]

        # checking if the run folder exists
        if os.path.exists(runPath):
            print("\033[94m   Run folder exists for {} \033[0m".format(data[0]))
        else:
            print("\033[95m   Creating the run folder : {} \n   {} \033[0m".format(
                data[0], runPath))
            os.mkdir(runPath)

        # checking if the sample folder exists
        if os.path.exists(samplePath):
            print("\033[94m   Sample folder exists for {} \033[0m".format(
                data[1] + "_" + data[2]))
        else:
            print("\033[95m   Creating the sample folder : {} \n   {} \033[0m".format(
                data[1] + "_" + data[2], samplePath))
            os.mkdir(samplePath)

        # retrieve the history for each line
        hist = gi.histories.show_history(data[3])
        # pprint.pprint(hist)

        # checking if the history is ok, queued and errors (downloads whatever datasets are 'ok', for all history categories)
        if hist['state'] == 'ok' or hist['state'] == 'queued' or hist['state'] == 'error':
            # retrieve the ok datasets
            datasets = hist['state_ids']['ok']

            # iterating through datasets to find the required images.
            for dsid in datasets:
                # get the dataset information
                ds = gi.datasets.show_dataset(dsid)

                # DEBUG
                if ds['state'] == 'ok':
                    print("\033[95m NAME: {}, EXT : {} \033[0m".format(
                        ds['name'], ds['file_ext']))

                # downloading the experimental_bam
                if ds['file_ext'] == 'bam' and ds['name'].endswith('filtered.bam'):
                    downloadFilename = "_".join(ds['name'].split('_'))
                    downloadFilePath = samplePath + "/" + downloadFilename
                    gi.datasets.download_dataset(
                        ds['id'], file_path=downloadFilePath, use_default_filename=False, wait_for_completion=True, maxwait=12000)
                    print("\033[92m \033[1m SUCCESS ! \033[0m \033[0m file_name: {} \t  ext : {} \t dataset_id: {}".format(
                        ds['name'], ds['file_ext'], ds['id']))

                # downloading the FIMO files
                if ds['name'].split(' ')[0].startswith('FIMO') and ds['file_ext'] == 'tabular':
                    downloadFilename = "_".join(ds['name'].split(' '))
                    downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                    gi.datasets.download_dataset(
                        ds['id'], file_path=downloadFilePath, use_default_filename=False, wait_for_completion=True, maxwait=12000)
                    print("\033[92m \033[1m SUCCESS ! \033[0m \033[0m file_name: {} \t  ext : {} \t dataset_id: {}".format(
                        ds['name'], ds['file_ext'], ds['id']))

                # check if the dataset is in the pngList before downloading
                if ds['state'] == 'ok' and ds['name'].split(' ')[0] in pngList:

                    # check MergedMotifHeatmap | MotifComposite | 4colorplots | Other (.png)
                    if ds['file_ext'] == 'png':
                        if ds['name'].split(' ')[0] == 'Merge':
                            count[0] = count[0] + 1
                            downloadFilename = downloadFilename = "Motif_" + \
                                str(count[0]) + "_Heatmap.png"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        elif ds['name'].split(' ')[0] == 'Create':
                            count[1] = count[1] + 1
                            downloadFilename = "Motif_" + \
                                str(count[1]) + "_composite.png"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        elif ds['name'].split(' ')[0] == 'Fasta':
                            count[2] = count[2] + 1
                            downloadFilename = "Motif_" + \
                                str(count[2]) + "_fourcolor.png"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        else:
                            downloadFilename = "_".join(
                                ds['name'].split(' ')[0:2]) + ".png"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename

                    # checking for bedfiles MotifHeatmap | MotifFourColor | other
                    elif ds['file_ext'] == 'bed':
                        if ds['name'].split(' ')[0] == 'Expand':
                            count[4] = count[4] + 1
                            downloadFilename = "Motif_" + \
                                str(count[4]) + "_bound.bed"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        elif ds['name'].split(' ')[0] == 'FourColor':
                            count[3] = count[3] + 1
                            downloadFilename = "Motif_" + \
                                str(count[3]) + "_FourColor.bed"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        else:
                            downloadFilename = "_".join(
                                ds['name'].split(' ')[0:2]) + ".bed"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename

                    # checking for Motif text files
                    elif ds['file_ext'] == 'txt':
                        if ds['name'].split(' ')[0] == 'Create':
                            count[5] = count[5] + 1
                            downloadFilename = "_".join(ds['name'].split(
                                ' ')[0:2]) + "_" + str(count[5]) + ".txt"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename
                        else:
                            downloadFilename = "_".join(
                                ds['name'].split(' ')[0:2]) + ".txt"
                            downloadFilePath = samplePath + "/" + prefixName + downloadFilename

                    else:
                        # creating the file path for remaining files
                        downloadFilename = "_".join(ds['name'].split(
                            ' ')[0:2]) + "." + str(ds['file_ext'])
                        downloadFilePath = samplePath + "/" + prefixName + downloadFilename

                    # downloading the dataset
                    gi.datasets.download_dataset(
                        ds['id'], file_path=downloadFilePath, use_default_filename=False, wait_for_completion=True, maxwait=12000)
                    print("\033[92m \033[1m SUCCESS ! \033[0m \033[0m file_name: {} \t  ext : {} \t dataset_id: {}".format(
                        ds['name'], ds['file_ext'], ds['id']))

                    # creating the motif logos using meme2images
                    if downloadFilename == "MEME_Motifs.txt":
                        memeLogoPath = downloadFilePath.split('/')[:-1]
                        memeLogoPath.append('memelogos')

                        command = 'meme2images -png -rc ' + \
                            downloadFilePath + " " + "/".join(memeLogoPath)
                        print(command)
                        os.system(command)

                    # creating the bigWig files
                    if downloadFilename == "reverseStrand.bedgraph":
                        # retrieve the destination folder path
                        destination = "/".join(downloadFilePath.split("/")
                                               [:-1]) + "/"

                        # forming the sort command to create sorted bedGraph
                        sortCommand = "sort -k1,1 -k2,2n " + os.path.abspath(downloadFilePath) + " > " + os.path.abspath(
                            destination) + "/" + prefixName.upper() + "sortedReverseStrand.bedGraph"
                        # sorting the bedGraph
                        print(sortCommand)
                        os.system(sortCommand)

                        # Creating the command for bigWig generation
                        command = 'bedGraphToBigWig ' + destination + prefixName.upper() + "sortedReverseStrand.bedGraph" + \
                            " " + os.path.abspath(args.chrSizeFile) + " " + \
                            destination + prefixName.upper() + "reverseStrand.bw"
                        print(command)
                        os.system(command)

                    if downloadFilename == "forwardStrand.bedgraph":
                        # retrieve the destination folder path
                        destination = "/".join(downloadFilePath.split("/")
                                               [:-1]) + "/"

                        # forming the sort command to create sorted bedGraph
                        sortCommand = "sort -k1,1 -k2,2n " + os.path.abspath(downloadFilePath) + " > " + os.path.abspath(
                            destination) + "/" + prefixName.upper() + "sortedForwardStrand.bedGraph"
                        # sorting the bedGraph
                        print(sortCommand)
                        os.system(sortCommand)

                        # Creating the command for bigWig generation
                        command = 'bedGraphToBigWig ' + destination + prefixName.upper() + "sortedForwardStrand.bedGraph" + \
                            " " + os.path.abspath(args.chrSizeFile) + " " + \
                            destination + prefixName.upper() + "forwardStrand.bw"
                        print(command)
                        os.system(command)

                    # creating the bigBed files
                    if downloadFilename == "Format_Peaks.bed":
                        # retrieve the destination folder path
                        destination = "/".join(downloadFilePath.split("/")
                                               [:-1]) + "/"

                        # forming the sort command to create sorted bed
                        sortCommand = "sort -k1,1 -k2,2n " + os.path.abspath(downloadFilePath) + " > " + os.path.abspath(
                            destination) + "/" + prefixName.upper() + "sortedPeaks.bed"
                        # sorting the bedGraph
                        print(sortCommand)
                        os.system(sortCommand)

                        # Creating the command for bigWig generation
                        command = 'bedToBigBed ' + destination + prefixName.upper() + "sortedPeaks.bed" + " " + \
                            os.path.abspath(
                                args.chrSizeFile) + " " + destination + prefixName.upper() + "Peaks.bb"
                        print(command)
                        os.system(command)

        else:
            print("\033[91m  ERROR ! HISTORY is {} : {}, Skipping \n   {},{} \033[0m".format(
                hist['state'], data[3], data[0], data[1]))
            continue
