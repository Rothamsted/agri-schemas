# Modelling links between field trials, markers, genotypes, phenotypes, cultivars

## EBI gene Expression Atlas

We have drafted a [modelling example](ebi-gxa-use-case/README.md) of data coming from the [EBI Gene Expression Atlas](https://www.ebi.ac.uk/gxa), which contains NGS and microarray experiments and reports
computed results about differentially expressed genes (eg, computed via ANOVA) or sequence counts (eg, using TPM).  

While there aren't many agriculture-related experiments in GXA, it provides data that are easy to compare across experiments and are associated to experiment and sample metadata.  

The modelling done so far is very simple and provisional. For instance, we reports the conditions in which every gene is expressed in an experiment, but we omit to link the samples used to compute such results (ie, the evidence). This information is available in GXA and will be modelled using agri-schemas
in future.  

More details in the [README](ebi-gxa-use-case/README.md)

## Other Resources
  * AHDB
  * CerealsDB
  * [Grain Genes](https://wheat.pw.usda.gov/GG3/)
  * [T3/Wheat](https://triticeaetoolbox.org/wheat/)
