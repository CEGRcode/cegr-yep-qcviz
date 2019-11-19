#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 5th July, 2018
#


"""
Program to read a config file and runInfoFile
to start the yepQC & Viz pipeline.
This script assumes that all the files needed
to run the workflow are already in the data library.

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


def createDataLibrariesAndHistories(gi, libList, sampleList, libPrefix):
    """
    Function to create libraries and subfolders for each sample and returns the data structure for the entire run_info_file
    """

    # to store {run:[ library_id, {sample:[folder_id,history_id,dataset_id]} ]}
    libs = {}
    hlibs = {}  # to store {run:{sample:[folder_id,history_id,dataset_id]}}

    # iterate the liblist to create libraries based on run and subfolders for samples
    for run, samples in libList.items():
        # creating a data library for each run
        libname = libPrefix + str(run)
        mylib = gi.libraries.create_library(
            libname, description=None, synopsis=None)
        print(
            " \n\033[94m  \033[94m  Created Library : {} \033[0m \033[0m ".format(libname))

        # storing the library id for future use.
        libs[run] = [mylib['id']]
        hlibs[run] = {}
        sampleDict = {}

        # create sample folders and histories
        for i in range(0, len(samples)):
            # creating sample folders within each run, into the data library
            folderName = samples[i]
            folder = gi.libraries.create_folder(
                mylib['id'], folder_name=folderName, description=None, base_folder_id=None)
            print(
                "\033[94m  \033[94m  Created Folder : {} \033[0m \033[0m ".format(folderName))

            # creating the history for each sample/folder
            historyName = libPrefix + run + "-" + samples[i] + ".001"
            history = gi.histories.create_history(name=historyName)
            print("\033[94m  \033[94m  Created History : {} with id {} \033[0m \033[0m ".format(
                historyName, history['id']))

            # store the folder id and history id for future use.
            sampleDict[samples[i]] = [folder[0]['id'], history['id']]

        # data structures containing all the basic info for future use.
        libs[run].append(sampleDict)
        hlibs[run] = sampleDict

    # #DEBUG
    # pprint.pprint(libs)
    # pprint.pprint(hlibs)
    return libs, hlibs


def getLibraryDatasetsToUpload(gi, libraries):
    """
    Function that return the library ids for the libraries that are uploaded to each yepQC history.
    """
    # retrieve the generic libraries to upload
    libsToUpload = libraries.split(',')
    # pprint.pprint(libsToUpload)

    uploadLibs = []  # to store the library ids for the libsToUpload
    # to store the dataset ids after uploading into each history.
    uploadLibDatasets = []

    # retrieve all the existing libraries in this galaxy instance.
    glibs = gi.libraries.get_libraries()

    # searching for the data libraries that needs to be uploaded into each history
    print(" \033[94m  \033[94m Searching for generic libraries \033[0m \033[0m ")
    for i in range(0, len(glibs)):
        if glibs[i]['deleted'] == False:
            if glibs[i]['name'] in libsToUpload:
                print(" \033[94m  \033[94m Found library : {},  id: {} \033[0m \033[0m ".format(
                    glibs[i]['name'], glibs[i]['id']))
                if glibs[i]['id'] not in uploadLibs:
                    uploadLibs.append(glibs[i]['id'])
    # DEBUG
    # pprint.pprint(uploadLibs)

    # retrieve the contents of each library using their library ids
    for j in range(0, len(uploadLibs)):
        datasets = gi.libraries.show_library(uploadLibs[j], contents=True)
        # retrieve the dataset id's from the library for uploading
        for i in range(0, len(datasets)):
            if datasets[i]['type'] == 'file':
                if datasets[i]['id'] not in uploadLibDatasets:
                    # print datasets[i]['name']
                    uploadLibDatasets.append(datasets[i]['id'])
    print(" \033[94m  \033[94m Datasets Found within library : {} \033[0m \033[0m ".format(
        len(uploadLibDatasets)))

    return uploadLibDatasets


def uploadDataToHistories(gi, libs, sampleList):
    """
    Function to upload required datasets to each sample history
    """
    uploadInfo = {}  # to store metainfo for the uploaded dataset.
    libIdToDelete = []  # to store the shared data library ids that will be deleted

    # upload the BAM file dataset into each sample history
    for run, data in libs.items():
        if run not in uploadInfo.keys():
            uploadInfo[run] = {}
            libIdToDelete.append(data[0])  # adding the lib id
        for sample, idList in data[1].items():
            if sample not in uploadInfo[run].keys():
                uploadInfo[run][sample] = []
                datasetName = sample + "_" + \
                    sampleList[sample][1] + "_filtered.bam"

                print(
                    "\n\033[94m  \033[94m  Uploading DE-DUP BAM for the sample : {} \033[0m \033[0m".format(sample))
                upload_data = gi.histories.upload_dataset_from_library(
                    history_id=idList[1], lib_dataset_id=idList[2])

                # pprint.pprint(upload_data)
                # print upload_data['name']

                # rename the de-dup bam file based on the run and sample ID
                updateDataset = gi.histories.update_dataset(
                    history_id=idList[1], dataset_id=upload_data['id'], name=datasetName)

                upload_data['name'] = datasetName
                # print upload_data['name']
                # print upload_data['id']

                # store the metainfo
                uploadInfo[run][sample].append(upload_data)

                # checking if the dataset is successfully renamed
                if updateDataset == 200:
                    print(
                        "\033[94m  \033[94m  DE-DUP BAM Name Changed to : {} \033[0m \033[0m".format(datasetName))
                else:
                    print(
                        "\033[94m  \033[91m  FAILED TO CHANGE THE DE-DUP BAM Name within the history \033[0m \033[0m")
                    exit()  # exiting if unable to change the dataset name

                print(
                    "\n\033[94m  \033[94m  Uploading GENERIC data for the sample : {} \033[0m \033[0m".format(sample))

                # Uploading the datasets from generic libraries.
                for i in range(0, len(uploadLibDatasets)):
                    upload_data = gi.histories.upload_dataset_from_library(
                        history_id=idList[1], lib_dataset_id=uploadLibDatasets[i])
                    uploadInfo[run][sample].append(upload_data)
                    # print "run : {} sample :{} uploaddatasetid : {} upload dataset source: {} upload dataset name: {} history id: {}".format(run,sample,upload_data['id'],upload_data['hda_ldda'],upload_data['name'],idList[1])
                print(
                    "\033[94m  \033[94m  Uploaded generic datasets for sample : {} \033[0m \033[0m".format(sample))

    print(
        "\n\033[94m  \033[95m  Deleting Shared Libraries once uploaded to histories  \033[0m \033[0m")
    for libDeleteId in libIdToDelete:
        # deleting the library since the dataset (DE dup BAM) is uploaded into the history
        gi.libraries.delete_library(libDeleteId)
        print("\033[94m  \033[94m  Deleted the Library with id : {} \033[0m \033[0m".format(
            libDeleteId))

    return uploadInfo


def findDeDupBAM(gi, libList, sampleList, libs, hlibs):
    """
    Function to find the de-duplicated bam for each sample from the core pipeline history
    """
    # #DEBUG
    # print "\nLIBS"
    # pprint.pprint(libs)
    # print "\nhlibs"
    # pprint.pprint(hlibs)
    # print "\nsampleList"
    # pprint.pprint(sampleList)
    # print "\nlibList"
    # pprint.pprint(libList)

    # iterating the sample corePipelineHistories
    for sampleNo, data in sampleList.items():
        run = data[0]
        folder = sampleNo
        datasetName = run + "_" + data[1] + "_filtered.bam"
        sampleHistory = gi.histories.get_histories(
            history_id=data[2], deleted=False)
        # checking if only one history is returned
        if len(sampleHistory) == 1:
            # iterating through each history
            hist = gi.histories.show_history(data[2])
            datasetList = hist['state_ids']['ok']
            # looping through each dataset to find the BAM file.
            for i in range(0, len(datasetList)):
                ds = gi.datasets.show_dataset(datasetList[i])
                # pprint.pprint([ds['name'],ds['id'],ds['extension']])
                if ds['name'].startswith('Filter') and ds['extension'] == 'bam':
                    print(
                        "\033[94m  \033[94m  FOUND BAM file: {} \033[0m \033[0m".format(ds['name']))
                    dataset = gi.libraries.copy_from_dataset(
                        library_id=libs[run][0], dataset_id=ds['id'], folder_id=libs[run][1][folder][0])
                    print(
                        "\033[94m  \033[94m  Finished Copying De-Dup BAM file into the data library : {}, {} \n \033[0m \033[0m".format(run, folder))

                    # append the uploaded dataset id for each sample to upload into history.
                    libs[run][1][folder].append(dataset['id'])
        else:
            print("There is more than one Histories for this sample. Skipping\n {}\t{}\t{}".format(
                sampleNo, data, sampleHistory[0]['name']))
            continue

    # DEBUG
    # pprint.pprint(libs)
    # pprint.pprint(hlibs)
    return libs, hlibs


def getInputsAndParams(gi, uploadInfo, libs, workflowID, confInputs, confParams, sampleList):
    """
    Function that creates the input dictionary and params dict for each yepqc sample
    """
    show_workflow = gi.workflows.show_workflow(workflowID['id'])
    raw_inputs = show_workflow.get('inputs')
    raw_params = show_workflow.get('steps')
    print("\033[94m  \033[94m  Extracted the RAW INPUT DICT and PARAMS DICT for : {} \033[0m \033[0m".format(
        workflowID['name']))

    # #DEBUG
    # pprint.pprint(raw_inputs)
    # print "\n\n"
    # print "RAW PARAMS"
    # pprint.pprint(raw_params)
    # print "\n\n"
    # print "Inputs from Config file \n"
    # pprint.pprint(confInputs.items())
    # print "\n\n"

    # To store the final data structure to run the workflow.
    # {run:{sample:[input_dict,param_dict,workflow_id,history_id]}}
    ginputs = {}

    for run, data in uploadInfo.items():
        print(
            "\n\033[94m  \033[94m  Creating INPUTS and PARAMS for run : {} \033[0m \033[0m".format(run))
        if run not in ginputs.keys():
            ginputs[run] = {}
        for sample, datasets in data.items():
            print(
                "\033[94m  \033[94m  sample : {} \033[0m \033[0m".format(sample))
            if sample not in ginputs[run].keys():
                ginputs[run][sample] = []

            # creating the input dictionary for each sample
            inputDict = {}  # temp
            for i in range(0, len(datasets)):
                inputDict[datasets[i]['name']] = {
                    'id': datasets[i]['id'], 'src': datasets[i]['hda_ldda']}

            # #DEBUG
            # pprint.pprint(inputDict)
            # print "\n\n"

            inputs = {}  # temp dict to hold the values
            # iterate through the raw_inputs
            for k, v in raw_inputs.items():
                # print "run :{} sample: {} K: {} , v :{}".format(run,sample,k,v)
                # pprint.pprint(confInputs.keys())
                if raw_inputs[k]['label'] in confInputs.keys():
                    label = raw_inputs[k]['label']
                    # Creating the correct input for experimental_bam for each protein
                    if label == 'experimental_bam':
                        datasetName = sample + "_" + \
                            sampleList[sample][1] + "_filtered.bam"
                        # print datasetName
                        inputs[k] = inputDict[datasetName]
                    # Using the custom masterNoTag assigned based on the treatments in runInfoFile
                    elif label == 'control_bam':
                        datasetName = sampleList[sample][3]
                        # print datasetName
                        inputs[k] = inputDict[datasetName]
                        # print inputs[k]
                    else:
                        inputs[k] = inputDict[confInputs[label]]

            params = {}  # temp dict to hold the values

            # creating the params dictionary for each sample
            for toolid, tooldict in raw_params.items():
                # print toolid,tooldict
                tool_inputs = tooldict
                if tooldict['tool_id'] in confParams.keys():
                    print("\033[94m  \033[94m  Creating the param dict for : {} \033[0m \033[0m".format(
                        tooldict['tool_id']))
                    # print "CHANGING tool : {}, id :{} ".format(tooldict['tool_id'],toolid)
                    configParams = confParams[tooldict['tool_id']].split(',')
                    if len(configParams) == 2:
                        if configParams[1] == 'prot':
                            tool_inputs = {
                                'param': configParams[0], 'value': sampleList[sample][1]}

                params[toolid] = tool_inputs

            # appending the input dict for each sample
            ginputs[run][sample].append(inputs)
            # print "Inputs"
            # pprint.pprint(inputs)
            # print "\n"

            ginputs[run][sample].append(params)
            # print "PARAMS"
            # pprint.pprint(params.get('26'))
            # pprint.pprint(params.get('10'))
            ginputs[run][sample].append(workflowID['id'])
            ginputs[run][sample].append(libs[run][sample][1])
        print("\033[94m  \033[94m  DONE ! \033[0m \033[0m")
    # print " FINAL GINPUTS"
    # pprint.pprint(ginputs)
    return ginputs


def createWorkflowInvokeFile(invokeInfo, sampleList):
    """
    Function that takes in the invokeInfo data structure and creates a csv file containing details about the history_id, workflow_id, invokation_id and other for each sample processed through this pipeline.
    """
    workflowInfoFile = open('workflowInfo.csv', 'w')
    header = '#run,sample,protein,history_id,workflow_id,invoke_id,time'
    workflowInfoFile.write(header + "\n")
    for run, data in invokeInfo.items():
        for sample, inputList in data.items():
            for il in inputList:
                workflowInfoFile.write("{},{},{},{},{},{},{}\n".format(
                    run, sample, sampleList[sample][1], il['history_id'], il['workflow_id'], il['id'], il['update_time']))

    workflowInfoFile.flush()
    workflowInfoFile.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'configFile', help='yepQcViz.conf file that has galaxy url and apikey information.')
    parser.add_argument(
        'runInfo', help='yepqcRunInfo.csv file that has the sample information')
    args = parser.parse_args()

    # to store the samples from runInfo file, stores a list with sample numbers as keys.
    sampleList = {}
    libList = {}  # toGenerate library folders
    # to hold all the upload data, once you upload the datasets to individual sample histories.
    uploadInfo = {}
    invokeInfo = {}  # to store the info returned after invoking the workflow one each sample

    # config parser to take necessary options
    config = configparser.ConfigParser()
    try:
        config.read(args.configFile)
        galaxyUrl = config['BASIC']['GALAXY_URL']
        apiKey = config['BASIC']['API_KEY']
    except:
        print("\033[91m ERROR ! Unable to read config file or Missing the required Configuration fields or file not found ! \033[0m")
        exit()

    # parsing the run Info file for yepQC
    try:
        runinfo = open(args.runInfo, 'r').readlines()
        if len(runinfo) <= 0:
            print(
                "\033[91m ERROR ! yepqcRunInfo.csv doesn't have any samples ! EXITING \033[0m")
            exit()
        else:
            for line in runinfo:
                if line.startswith('#'):
                    pass
                else:
                    line = line.strip()
                    temp = line.split(',')
                    if temp[1] not in sampleList.keys():
                        sampleList[temp[1]] = [
                            temp[0], temp[2], temp[3], temp[4]]
                    else:
                        print(
                            "\n \033[91m WARNING ! SAMPLE number is repeated in the yepqcRunInfo.csv, not including {} \033[0m".format(line))

                    if temp[0] not in libList.keys():
                        libList[temp[0]] = [temp[1]]
                    else:
                        libList[temp[0]].append(temp[1])
    except:
        print(
            "\033[91m ERROR ! Unable to read yepqcRunInfo.csv file or file not found ! \033[0m")
        exit()

    # parsing through the config file and creating a galaxy instance
    gi = galaxy.GalaxyInstance(url=galaxyUrl, key=apiKey)
    print("\033[94m  \033[1m Connected to GALAXY at : {}  \033[0m \033[0m ".format(
        galaxyUrl))

    # # DEBUG
    # pprint.pprint(sampleList)
    # print "\n\n"
    # pprint.pprint(libList)
    # DEBUG SAMPLE OUTPUT
    # sampleList => {'17114': ['300', 'Lsm1','2612d619c2a0e1ab']}
    # libList => {'300': ['17114']}

    # create all libraries, sample subfolders and sample histories
    print(
        "\n\033[94m  \033[95m  Creating Libraries and histories : \033[0m \033[0m ")
    libs, hlibs = createDataLibrariesAndHistories(
        gi, libList, sampleList, config['BASIC']['LIB_PREFIX'])

    # finding the de-duplicated bam for each sample and add it to the sample folder.
    print("\n\033[94m  \033[95m  Searching for the Filterd BAM file from Core Pipeline History : \033[0m \033[0m ")
    libs, hlibs = findDeDupBAM(gi, libList, sampleList, libs, hlibs)

    # get the generic library ids that needs to be uploaded.
    print(
        "\n\033[94m  \033[95m  Retrieve dataset ids from libraries before uploading \033[0m \033[0m ")
    uploadLibDatasets = getLibraryDatasetsToUpload(
        gi, config['BASIC']['DATA_LIBRARIES'])

    # upload the necessary datasets to each history
    print(
        "\n\033[94m  \033[95m  Uploading datasets into each sample history \033[0m \033[0m")
    uploadInfo = uploadDataToHistories(gi, libs, sampleList)

    # invoke the workflow.
    myWorkflow = config['BASIC']['RUN_WORKFLOW']
    print("\n\033[94m  \033[95m  Retrieving the workflow : {} \033[0m \033[0m".format(
        myWorkflow))
    workflowID = gi.workflows.get_workflows(name=myWorkflow)[0]
    print("\033[94m  \033[94m  Workflow details : \033[0m \033[0m")
    pprint.pprint(workflowID)

    # get input dict, param dict, workfowid and historyid for each sample.
    print("\n\033[94m  \033[95m  Retrieving the inputs and parameters for the Workflow : {} \033[0m \033[0m".format(
        workflowID['name']))
    workflowInputs = getInputsAndParams(
        gi, uploadInfo, hlibs, workflowID, config['INPUTS'], config['PARAMS'], sampleList)

    print(
        "\n\033[95m  \033[95m  Starting Workflow invokations !  \033[0m \033[0m")
    for run, data in workflowInputs.items():
        print(
            "\033[95m  \033[94m  Starting Workflow for run : {} \033[0m \033[0m".format(run))
        if run not in invokeInfo.keys():
            invokeInfo[run] = {}
        for sample, inputList in data.items():
            if sample not in invokeInfo[run].keys():
                invokeInfo[run][sample] = []

                # #DEBUG
                # pprint.pprint(inputList[1].get('26'))
                # pprint.pprint(inputList[1].get('10'))

            invoked_workflow = gi.workflows.invoke_workflow(
                workflow_id=inputList[2], inputs=inputList[0], params=inputList[1], history_id=inputList[3])
            invokeInfo[run][sample].append(invoked_workflow)
            # pprint.pprint(invoked_workflow)
            print(
                "\033[95m  \033[94m  Invoked Workflow for sample : {} \033[0m \033[0m".format(sample))
            print("\033[95m  \033[94m  worflow_id : {} \n    history_id : {} \n    invoke_id : {} \n    update_time : {} \033[0m \033[0m\n".format(
                invoked_workflow['workflow_id'], invoked_workflow['history_id'], invoked_workflow['id'], invoked_workflow['update_time']))

    print(
        "\033[95m  \033[95m  Creating the WorkflowInvokeFile (CSV) \033[0m \033[0m")
    createWorkflowInvokeFile(invokeInfo, sampleList)
