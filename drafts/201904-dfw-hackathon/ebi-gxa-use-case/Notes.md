# GXA Notes

# How we could use the ENA API

1. Get [all the wheat experiments](https://www.ebi.ac.uk/fg/rnaseq/api/tsv/0/getRunsByOrganism/triticum_aestivum)
  * This will yield study IDs
2. For each study, get the corresponding [GXA Result](https://www.ebi.ac.uk/gxa/experiments-content/E-MTAB-4401/resources/ExperimentDownloadSupplier.RnaSeqBaseline/tpms.tsv), which contains gene/condition/score values.