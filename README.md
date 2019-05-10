# cegr-yep-qcviz
The Yeast Epigenome Project Quality Control &amp; Visualization GALAXY workflow.

## Running the YEP QC & VIZ pipeline on GALAXY

:sparkles: Below are required for automatic workflow invocation on GALAXY :sparkles:

:zap:**_Scripts_**
- `generateYepRunInfoFromPEGR.py`
- `createRunInfoFromSampleId.py`
- `runYepQCVIZ.py`
- `downloadResults.py`
- `processResults.py`

:exclamation:**_Config Files_**

- `yepQcViz.cfg`
- `yepRunInfo.csv`
- `workflowInfo.csv`

##### :fire: Dependencies

- Anaconda (https://www.anaconda.com/)
- pip  (can be installed using conda, once Anaconda is installed.)
- bioblend (https://bioblend.readthedocs.io/en/latest/#installation/)
- Meme-suite (http://meme-suite.org/doc/download.html)
- bedGraphToBigWig and bedToBigBed (http://hgdownload.soe.ucsc.edu/admin/exe/)

_Installing Anaconda usually satisfies all the dependencies for most of the python scripts. pip is used to install bioblend, these scripts are using bioblend version(0.7.0). Make sure you have them installed before you run any of the scripts._

> Meme-suite and UCSC utilities are used by downloadResults.py to create required datasets. Make sure these are available in the PATH. Read the entire scripts documentation before running them, dependencies and expected config files are explained in detail.

## Scripts Documentation

- `generateYepRunInfoFromPEGR.py` creates the `yepRunInfo.csv` file by using PEGR API for FRANCLINE. It takes the `runNO` as input to generate the run info file. you can use `#` to comment any sample in the run info file. The commented samples will not be processed by the workflow. Currently the script screens for `sacCer3_cegr` before making the run info file.

```
Usage:

    python generateYepRunInfoFromPEGR.py 300

Terminal Output:

    Making the API CALL to FRANCLINE !    
    INFO : Success fetching data from Run 300!   
    Total no of samples : 48   
    Creating the yepQcViz run info file !   

    Run Info File has 48 yeast samples !    
    DONE !

```

- `createRunInfoFromSampleId.py` is an alternative to create the `yepRunInfo.csv` file for yepQcViz pipeline. It takes a text file containing PEGR sample ids as input (one per each line). It uses PEGR API for FRANCLINE, to retrieve required data. Currently the script screens for `sacCer3_cegr` before making the run info file.

```
Usage:

    python createRunInfoFromSampleId.py samplelist.txt

Terminal Output:

    Making the API CALL to FRANCLINE per sample !    
    INFO :
    Success! Accepted filters:
    preferredOnly: true
    id: 15215

    INFO :
    Success! Accepted filters:
    preferredOnly: true
    id: 15216

    INFO :
    Success! Accepted filters:
    preferredOnly: true
    id: 15217

    Creating the yepQcViz run info file !   

    Run Info File has 3 yeast samples !    
    DONE !    

```


- `runYepQCVIZ.py` is the primary script that does all the heavy lifting. It parses the `yepQcViz.cfg` and `yepRunInfo.csv` to create necessary libraries, histories and loads each sample history with appropriate datasets. Once all the datasets are loaded, it invokes the GALAXY workflow using the GALAXY API key for your GALAXY admin user. Assuming that the workflow is set up with all the required tools on your GALAXY server. After invoking the workflow on all samples in the `yepRunInfo.csv` file, it creates a `workflowInfo.csv` file which can be used for downloading pre-defined datasets from the sample histories using `downloadResults.py`.


```
Usage:

    python runYepQCVIZ yepQcViz.cfg yepRunInfo.csv

Terminal Output:

   Connected to GALAXY at : http://chipexo-gw.aci.ics.psu.edu:8080    

    Creating Libraries and histories :   

    Created Library : yepqc_viz-216   
    Created Folder : 11758   
    Created History : yepqc_viz-216-11758.001 with id 1cbd94dc2671daa5   

    Searching for the Filterd BAM file from Core Pipeline History :   
    FOUND BAM file: Filter SAM or BAM on data 14: bam  
    Finished Copying De-Dup BAM file into the data library : 216, 11758


    Retrieve dataset ids from libraries before uploading   
    Searching for generic libraries   
    Found library : yepQCVIZ_generic,  id: 7acb88de7eaf251a   
    Datasets Found within library : 23   

    Uploading datasets into each sample history  

    Uploading DE-DUP BAM for the sample : 11758  
    DE-DUP BAM Name Changed to : 11758_Hht2_filtered.bam  

    Uploading GENERIC data for the sample : 11758  
    Uploaded generic datasets for sample : 11758  

    Deleting Shared Libraries once copied to histories   
    Deleted the Library with id : b4a9efd5c50010ba  

    Retrieving the workflow : yepQCVIZ  
    Workflow details :  
{u'deleted': False,
 u'id': u'3f5830403180d620',
 u'latest_workflow_uuid': u'b134cc18-741c-48c5-9590-af9912507913',
 u'model_class': u'StoredWorkflow',
 u'name': u'yepQCVIZ',
 u'owner': u'svc-chipexo',
 u'published': False,
 u'tags': [],
 u'url': u'/api/workflows/3f5830403180d620'}

    Retrieving the inputs and parameters for the Workflow : yepQCVIZ  
    Extracted the RAW INPUT DICT and PARAMS DICT for : yepQCVIZ  

    Creating INPUTS and PARAMS for run : 216  
    sample : 11758  
    DONE !  

    Starting Workflow invokations !   
    Starting Workflow for run : 216  
    Invoked Workflow for sample : 11758  
    worflow_id : 9fc1c2078b8ee907
    history_id : 1cbd94dc2671daa5
    invoke_id : 80f182b731e2cf36
    update_time : 2018-10-03T17:16:16.751203  

    Creating the WorkflowInvokeFile (CSV)


```

- `downloadResults.py` is the script that uses the `workflowInfo.csv` file to create the required folder structure and download the datasets into their respective sample folders. You should see `Results` folder appear in the directory where this script was run. All sample sub-folders are contained within it. Currently this script does not move the files to `/pass`, which need to be done manually. Dataset download for failed histories is skipped by default. Make sure you have `MEME-suite` installed and is in the `PATH`, so that motif logos can be generated. The `chrSizeFile` is the textfile containing the sacCer3.chrom.sizes for bigWig and bigBed.

```
Usage:

    python downloadResults.py yepQcViz.cfg workflowInfo.csv chrSizeFile outputPath
```

- `processResults.py` is the script that uses the `workflowInfo.csv` file to create separate folders for each dataset category. `srcPath` is the `Results` folder generated by `downloadResults.py` and `destPath` need to be an empty directory, so that category folders can be created within it.

```
Usage:

    python processResults.py workflowInvokeFile srcPath destPath
```

## Config files Documentation

- `yepQcViz.cfg` is the main config file that controls which generic datasets need to be loaded and which workflow needs to be run for the samples in `yepRunInfo.csv`. Each section has some basic placeholders for changing the config parameters. Make sure you enter proper API keys and GALAXY Server URL.

```
# SHIVA configuration using svc-chipexo@psu.edu
# example for GALAXY_URL = http://chipexo-gw.aci.ics.psu.edu:8080 , give the port number too.

[BASIC]

GALAXY_URL = [ GALAXY SERVER URL ]
API_KEY =  [ YOUR_GALAXY_API_KEY ]

# Prefix for the yepQCVIZ libraries and histories created by this script.
LIB_PREFIX = yepqc_viz-

# List of pre-curated libraries to be loaded along with the BAM file. [CASE-SENSITIVE]
# Separate each library name using commas(,) do not put trailing commas.
DATA_LIBRARIES = yepQCVIZ_generic

# name of the workflow that need to be run on each sample [CASE-SENSITIVE]
RUN_WORKFLOW = yepQCVIZ


[INPUTS]
# list of input labels and corresponding library filenames for easy creation of input dict.

# Below are (key=value) corresponds to (inputLabel:datasetNameInHistory) for the workflow.
# Hence these values are [CASE-SENSITIVE]

# the experimental_bam (value) below is a place holder and it will be replaced with sample specific dataset name within the script before executing the workflow.

experimental_bam = filtered.bam
control_bam = masterNoTag_20180928.bam
background_model = sacCer3_background_model.txt
exclude_regions = chexmix_exclude_180928.bed
intersection_region = Merged_sectors_for_MEME_924.bed
blacklist = guray_blacklist_yep_final.bed
x_element_bedfile = XELEMENT_32_2018-07-31.bed
centromere_bedfile = Cbf1_motif_at_Centromere_SORT_1000bp.bed
genemidpoint_bedfile = GENEMID_5335_2018-07-31.bed
tes_bedfile = TES_5335_2018-07-31.bed
tss_bedfile = TSS_5335_2018-07-31.bed
nfr_bedfile = NFR_5335_2018-07-31.bed
ars_bedfile = ARS_ORC_SORT_325_1000bp.bed
trna_bedfile = TRNA_275_2018-07-31.bed
xut_bedfile = XUT_1658_2018-07-31.bed
sut_bedfile = SUT_847_2018-07-31.bed
cut_bedfile = CUT_925_2018-07-31.bed
all_sectors = SECTORS_5335_2018-07-31.bed
noncoding_sectors = NONCODINGSECTORS_4673_2018-07-31.bed

# SUBSECTOR ANALYSIS Inputs :

subsector_file = subsectors.txt
yep_features = subsector_yep_features.txt
cegr_chr_length = cegr_sacCer3_chr_lengths.txt
padjust_script = adjustPValue.r

[PARAMS]
# list of tool name and [param_name,value] that need to be set.
# use 'prot' as value for those tools that need the protein name as value, the protein name is retrieved for each sample from run-info file. otherwise , the value mentioned is set.
# the keys are toolid from the tool xml wrapper.
# this configuration is for specific tools. for example, the tools whose input depends on the protein name, other parameters need to be pre-initialized within the workflow for simplicity
process_stamp = Target,prot
go_pol2_expression = Target,prot

[DOWNLOADS]
# list of galaxy history labels to check in order to download the corresponding png and datasets
# These names are entered with the 'configure output' section in your GALAXY workflow editor.

PNG_LIST = ['NFR','TSS','TES','GENEMID','EnrichedNFR','EnrichedTSS','EnrichedTES','CUT','SUT','XUT','EnrichedCUT','EnrichedSUT','EnrichedXUT','EnrichedFeatures','Format','Subsector','TRNA','X-ELEMENT','BoundFeatures','AllFeatures','ARS','MEME','Nucleosome','Transcription','CENTROMERE','Merge','Fasta','Create','Peaks_filtered','ChExMix','Expand','FourColor','forwardStrand','reverseStrand']

```

- `yepRunInfo.csv` is used to look up the `CORE PIPELINE` GALAXY history associated with a particular sample, so that the de-duplicated bam file can be copied into a new library, before running the yepQCVIZ workflow. This is made `WET LAB FRIENDLY`, so that they can view it in MS-EXCEL and save it as CSV.

```
yepRunInfo file contents:

    #RUN,SAMPLE,TARGET,HISTORYID,NOTAG,GENOME
    300,17114,Lsm1,38c0950fb6b21ce5,masterNotag_20161128.bam,sacCer3_cegr
    300,17115,Mbf1,23a1ee6b9374c61a,masterNotag_20161128.bam,sacCer3_cegr
    300,17116,Asg1,2387d03a336686ee,masterNotag_20161128.bam,sacCer3_cegr
    300,17117,Rif1,4326e44612443a1a,masterNotag_20161128.bam,sacCer3_cegr
    300,17118,Nab2,b5357255c274b4c0,masterNotag_20161128.bam,sacCer3_cegr
    300,17119,Rfa1,a890d357826ac24a,masterNotag_20161128.bam,sacCer3_cegr

```
- `workflowInfo.csv` is created by the `runYepQCVIZ.py` after invoking the workflow on all the samples. This is crucial for downloading the datasets.

```
workflowInfo.csv file contents:

    run,sample,protein,history_id,workflow_id,invoke_id,time
    310,17924,BY4741,4ea3a19da14bc9bc,32ff5cf1b96c1df7,71322db9def13f52,2018-10-01T16:20:19.519642
    218,11900,Nrd1,6039f54791d74153,32ff5cf1b96c1df7,3e12c52fba77c1a0,2018-10-01T16:20:20.309681
    271,15215,Ssl1,9172305476dea1d1,32ff5cf1b96c1df7,735529bbd6abc84a,2018-10-01T16:20:21.071535
    238,13145,Brf1,adb7d44294f7d110,32ff5cf1b96c1df7,de5e0c3b1bc79836,2018-10-01T16:20:22.251258
    275,14534,Orc6,577b6a30c6f86c77,32ff5cf1b96c1df7,d3162ea8b820c592,2018-10-01T16:20:23.060538
    227,12274,Reb1,70480a3dba658b94,32ff5cf1b96c1df7,4e3fedd2923453cb,2018-10-01T16:20:23.839428
    282,14997,Mcm16,b23b7fab22bd927c,32ff5cf1b96c1df7,21bd2ef7825d73b7,2018-10-01T16:20:24.647642
    231,12467,Reb1,cd6983c944889ccb,32ff5cf1b96c1df7,56934338248d413c,2018-10-01T16:20:25.424694
    231,12443,Set1,256e3d6ee6dba701,32ff5cf1b96c1df7,bd35cef64e08c312,2018-10-01T16:20:26.459122
    231,12427,Cft1,49bcaf11835f551f,32ff5cf1b96c1df7,c96aed0e7522be59,2018-10-01T16:20:27.457153
    216,11758,Hht2,adc308b17f770fb6,32ff5cf1b96c1df7,a329ebfe718e1bd5,2018-10-01T15:32:51.232822
    217,11796,Gal4,6799b97f386feaf5,32ff5cf1b96c1df7,5d3597f40db5e6ea,2018-10-01T15:32:52.133285


```
