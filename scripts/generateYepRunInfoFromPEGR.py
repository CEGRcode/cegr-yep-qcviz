#!/usr/bin/python
#
# author : prashant kumar kuntala
# date   : 17th July, 2018


"""
Program to generate the yepQcViz runinfo file using PEGR API.
This program creates a runInfo file based on runNO and user defined inputs.
Genome is embedded in the script to be : sacCer3_cegr

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

def fetchSequenceRunData(apiKey,query,outfilename):
    """
    function to make the api request to francline
    """
    print "\n \033[94m  \033[95m Making the API CALL to FRANCLINE !  \033[0m \033[0m "
    url = "http://francline.vmhost.psu.edu:8080/pegr/api/fetchSequenceRunData?apiKey="+apiKey
    r = requests.post(url, json=query)
    results = r.json()
    # pprint.pprint(len(results['data']))

    print " \033[94m  \033[94m INFO : {} \033[0m \033[0m ".format(results['message'])
    print " \033[94m  \033[94m Total no of samples : {} \033[0m \033[0m ".format(len(results['data']))
    # pprint.pprint(results['data'])

    # parsing the results to create a csv file
    outfile = open(outfilename,'w')
    header = "#RUN,SAMPLE,TARGET,HISTORYID,NOTAG,GENOME\n"
    outfile.write(header)
    print " \033[94m  \033[94m Creating the yepQcViz run info file ! \033[0m \033[0m "
    yepSampleCount = 0
    for sample in results['data']:

        # #DEBUG
        # print " runNO: {} sample ID: {} target:{} history_id: {}".format(sample['experiments'][0]['runId'],sample['id'],sample['target'],sample['histories'][0])
        # pprint.pprint(sample['experiments'][0]['alignments'][0]['genome'])

        # retrieve only the YEP project sample histories.
        if sample['experiments'][0]['alignments'][0]['genome'] == 'sacCer3_cegr':
            yepSampleCount = yepSampleCount + 1
            outfile.write("{},{},{},{},{},{}\n".format(sample['experiments'][0]['runId'],sample['id'],sample['target'],sample['histories'][0],'masterNoTags_29_sorted_dedup.bam',sample['experiments'][0]['alignments'][0]['genome']))
    outfile.flush()
    outfile.close()
    print "\n \033[94m  \033[95m Run Info File has {} yeast samples !  \033[0m \033[0m ".format(yepSampleCount)
    print " \033[94m  \033[95m DONE !  \033[0m \033[0m "

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('runNumber',help='Run number in PEGR , example: 299')
    args = parser.parse_args()

    # This is the cegr@psu.edu service accounts original APIkey for PEGR.
    API_KEY=''

    # parameter dictionary for the fetchSequenceRunData
    query = {"userEmail": "cegr@psu.edu", "runId": str(args.runNumber), "preferredOnly": "true"}

    outfilename = args.runNumber+"_yepqcRunInfo.csv"
    # making an API request to francline
    fetchSequenceRunData(API_KEY,query,outfilename)
