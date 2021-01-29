* Continue DEX
* Test
  * OK test_accessions_filter
* Work on DEX experiments
	* Download links: https://www.ebi.ac.uk/gxa/experiments-content/E-MTAB-4289/resources/ExperimentDownloadSupplier.RnaSeqDifferential/tsv
	* This version has reasonable cutoffs for fold-change and pvalue, which seem to need further filtering 
		(eg, pvalue < 0.05, |log2FC| > 1)
	* Conditions are all given in the header in the forms:
		* 'Blumeria graminis; 24 hour' vs 'control' .foldChange
		* 'Blumeria graminis; 24 hour' vs 'control'.pValue
		* which means they need separated annotations for the expr statement, onto-annotated separately.
	*