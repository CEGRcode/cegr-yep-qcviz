#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 3rd October, 2018
#


"""
Program to generate the yepQcViz runinfo file using PEGR API.
This program creates a runInfo file based on input sample list

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
import requests
import pprint,argparse

def fetchSampleData(apiKey,query):
    """
    function to make the api request to francline
    """

    url = "http://francline.vmhost.psu.edu:8080/pegr/api/fetchSampleData?apiKey="+apiKey
    r = requests.post(url, json=query)
    results = r.json()
    # pprint.pprint(len(results['data']))

    print " \033[94m  \033[94m INFO : \n{} \033[0m \033[0m ".format(results['message'])
    # pprint.pprint(results['data'])

    for sample in results['data']:

        # #DEBUG
        # print " runNO: {} sample ID: {} target:{} history_id: {}".format(sample['experiments'][0]['runId'],sample['id'],sample['target'],sample['histories'][0])
        # pprint.pprint(sample['experiments'][0]['alignments'][0]['genome'])

        # retrieve only the YEP project sample histories.
        if sample['experiments'][0]['alignments'][0]['genome'] == 'sacCer3_cegr':
            # yepSampleCount = yepSampleCount + 1
            string = "{},{},{},{},{},{}\n".format(sample['experiments'][0]['runId'],sample['id'],sample['target'],sample['histories'][0],'masterNoTags_29_sorted_dedup.bam',sample['experiments'][0]['alignments'][0]['genome'])

    return string


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('sampleList',help='File containing sampleIds, one per line')
    args = parser.parse_args()

    samples = open(args.sampleList,'r').readlines() # reading the samples
    runInfoContent = [] # to store the data

    # This is the cegr@psu.edu service accounts original APIkey for PEGR.
    API_KEY=''

    print "\n \033[94m  \033[95m Making the API CALL to FRANCLINE per sample !  \033[0m \033[0m "
    for sampleId in samples:
        # parameter dictionary for the fetchSampleData
        query = {"userEmail": "cegr@psu.edu","id":sampleId,"preferredOnly": "true"}
        # making an API request to francline
        runInfoContent.append(fetchSampleData(API_KEY,query))

    # creating the runInfoFile
    outfile = open("yepqcRunInfo.csv",'w')
    header = "#RUN,SAMPLE,TARGET,HISTORYID,NOTAG,GENOME\n"
    outfile.write(header)
    print " \033[94m  \033[94m Creating the yepQcViz run info file ! \033[0m \033[0m "
    for line in runInfoContent:
        outfile.write(line)
    outfile.flush()
    outfile.close()

    print "\n \033[94m  \033[95m Run Info File has {} yeast samples !  \033[0m \033[0m ".format(len(runInfoContent))
    print " \033[94m  \033[95m DONE !  \033[0m \033[0m "
