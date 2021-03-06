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

_Installing Anaconda usually satisfies all the dependencies for most of the python scripts. pip is used to install bioblend, these scripts are using bioblend version(0.13.0). Make sure you have them installed before you run any of the scripts._

> Meme-suite and UCSC utilities are used by downloadResults.py to create required datasets. Make sure these are available in the PATH. Read the entire scripts documentation before running them, dependencies and expected config files are explained in detail.

<p align="center">
  <img src="./examples/images/yepQcViz_flowchart.png" width="550" alt="YEP flowchart">
</p>

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

# these three values are renamed with actual dataset during run-time.
experimental_bam = filtered.bam
control_bam = masterNoTag_20180928.bam
background_model = sacCer3_background_model.txt
exclude_regions = yepChexmixExclude_190115.bed
intersection_region = Merged_sectors_for_MEME_924.bed
blacklist = ChexMix_Peak_Filter_List_190612.bed
x_element_bedfile = XELEMENT_25_2019-07-20.bed
centromere_bedfile = Cbf1_motif_at_Centromere_SORT_1000bp.bed
genemidpoint_bedfile = GENEMID_5538_2019-07-20.bed
tes_bedfile = TES_5538_2019-07-20.bed
tss_bedfile = TSS_5538_2019-07-20.bed
nfr_bedfile = NFR_5538_2019-07-20.bed
ars_bedfile = 10_Eaton_ARS_Orc6_Sort.bed
trna_bedfile = TRNA_269_2019-07-20.bed
xut_bedfile = XUT_1647_2019-07-20.bed
sut_bedfile = SUT_845_2019-07-20.bed
cut_bedfile = CUT_921_2019-07-20.bed
srna_bedfile = SRNA_97_2019-07-20.bed
ltr_bedfile = LTR_357_2019-07-20.bed
all_sectors = SECTORS_5538_2019-07-23.bed
all_genes_bedfile = ALLGENES_5538_2019-07-20.bed
noncoding_sectors = NONCODINGSECTORS_4499_2019-07-20.bed


# SUBSECTOR ANALYSIS Inputs :

subsector_file = subsectors.txt
yep_features = subsector_yep_features_190720.txt
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
# These names are entered within the 'configure output' section in your GALAXY workflow editor.

PNG_LIST = ['NFR','TSS','TES','GENEMID','EnrichedNFR','EnrichedTSS','EnrichedTES','CUT','SUT','XUT','EnrichedCUT','EnrichedSUT','EnrichedXUT','EnrichedSRNA','EnrichedFeatures','Format','Subsector','TRNA','X-ELEMENT','LTR','SRNA''BoundFeatures','AllFeatures','ARS','MEME','Nucleosome','Transcription','CENTROMERE','Merge','Fasta','Create','Peaks_filtered','ChExMix','Expand','FourColor','forwardStrand','reverseStrand']

```

- `yepRunInfo.csv` is used to look up the `CORE PIPELINE` GALAXY history associated with a particular sample, so that the de-duplicated bam file can be copied into a new library, before running the yepQCVIZ workflow. This is made `WET LAB FRIENDLY`, so that they can view it in MS-EXCEL and save it as CSV.

```
yepRunInfo file contents:

    #RUN,SAMPLE,TARGET,HISTORYID,NOTAG,GENOME,TREATMENT
    271,15215,Ssl1,d12d5b60519b3ffd,masterNoTag_20180928.bam,sacCer3_cegr,
    271,15216,Pho2,4ec1b03254ee8680,masterNoTag_20180928.bam,sacCer3_cegr,
    271,15217,Rpt6,9f071edfc9cf1e78,masterNoTag_20180928.bam,sacCer3_cegr,
    350,21070,Reb1,e8b9714067972508,masterNoTagHS_181126.bam,sacCer3_cegr,HS6
    367,22525,Reb1,cafc28259219a486,masterNoTagHS_181126.bam,sacCer3_cegr,HS6
    331,19390,Reb1,bed4667625c6c086,masterNoTagOX6_190513.bam,sacCer3_cegr,H2O2_6min
    367,22540,Reb1,3453e4f78002fa33,masterNoTagOX6_190513.bam,sacCer3_cegr,OX

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
