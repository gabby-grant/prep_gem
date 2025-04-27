# Gene Expression Matrix Builder
Python script that prepares a GEM from the GDC Portal for differential gene expression for transcriptome profiling.


## Description
A python tool that parses gene names and expression levels from gene expression files. By default it parses out the stranded_second column from the available expression column. Then the script will identify all sample folders in directory, gathers all subdirectories and creates a list or identify samples within one folder.


Then a dictionary is created to store the combined data and convert the combined data to a Data Frame and saves the combined data to an output file. 
## Installation
- Python 3.6
- Python Libraries (os, glob, pandas, argparse, sys)
- gdc-client v. 1.6.1


## Data Preprocessing
1. Access the GDC data portal https://portal.gdc.cancer.gov/
2. Find data to analyze. 
3. Navigate to repository and download manifest. 
4. Create directory for downloaded sample files.

```Bash
gdc-client download -m gdc_manifest_file.txt —-dir path/to/desired/directory
```
This code is specific to certain filters available from the GDC portal
- Data Category: transcriptome profiling
- Workflow Type: STAR - Count
- Experimental Strategy: RNA Seq

## Usage
### Command Line Arguments;
- `-i` : input directory
- `-o` : output file name
- `-c` : expression column
	- Default is `stranded_second`
	- Other options:  `unstranded` ,     `stranded_first  `,  `tpm_unstranded`,  `fpkm_unstranded`,` fpkm_uq_unstranded`
- `-e`:  filter by file extension
## Output
This script will create a TSV file with the gene name as rows and the sample ID as the column headers. It uses NA for missing values.

