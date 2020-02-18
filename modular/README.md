### Modular YEP Qc & Viz pipeline

**Basic idea**

Run `ChExMix` on the samples to call peaks. Then create a datalibrary in galaxy containing all the `ChExMix-peaks.bed` and `ChExMix-Allevents.tabular` files. Each of these files should follow a naming standard, for example, `sampleID_chexmix_peaks.bed` and `sampleID_chexmix_allevents.tabular`. Now create a `datasetInfo.csv` containing three values `sampleId,filename,datasetid`. The datasetid can be obtained using bioblend api. Use this `datasetInfo.csv` with the modular config and `runYepQCVIZ.py` script to start workflows.

**_Hope you already have the modular pipeline available on the galaxy and the feature files in another datalibrary. An example for the `datasetInfo.csv` is available for reference._**

---
### Running the modular pipeline

> below scripts are executed on the files provided in the `../examples` folder

- Create the `yepqcRunInfo.csv`
    - `python scripts/createRunInfoFromSampleId.py examples/example_sampleList.txt`

- Configure the `yepQcViz_modular.cfg`
    - you need to add the values for `API_KEY`, `DATA_LIBRARIES`, `RUN_WORKFLOW` in the config file. These are case-sensitive.
    - you can change the `LIB_PREFIX` to anything you like, this will be used for history names within galaxy.

- Run the workflow
    - `python modular/runYepQCVIZ.py yepQcViz_modular.cfg yepqcRunInfo.csv datasetInfo.csv`

The last step generates a `workflowInfo.csv` upon success. You can use this file, `yepQcViz_modular.cfg` and `downloadResults.py` to download the required datasets, images and assets. Use `processResults.py` to rename and reorganize the assets into individual folders.
