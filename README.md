# Prep_GEM
Python script that prepares GEM script for differential gene expression
## Prometheus Prompt:
I need to write a code that takes the input files that are .tsv and parses out gene name and expression levels. It should be similar to this command `for i in ; do echo $i; head $i/.tsv | awk '{print $2,$6}'; done`  and should be a python script that creates one output file and add NA if there isn't any gene expression.. It needs to remove the first 6 rows. The code needs to be able to open the folder or file in the directory and fine the gene expression files.

- These are the headers `gene_id gene_name gene_type unstranded stranded_first stranded_second tpm_unstranded fpkm_unstranded fpkm_uq_unstranded` 

