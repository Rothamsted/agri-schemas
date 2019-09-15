# Translating GXA data to agrischemas

## AgriSchema Model

For the moment, we give a simple, proof-of-concept model about GXA data.

### Experiment, general description

```java
bkr:exp_E-MTAB-3103 a bioschema:Study;
	agri:accession "E-MTAB-3103";
	dc:title "Tissue layers from developing wheat grain at 12 days post-anthesis";
	schema:description "Inner pericarp, outer pericarp and endosperm layers from...";
	schema:datePublished "2015-04-24";
	schema:about bkr:pmid_26044828;
	schema:additionalProperty <http://purl.bioontology.org/ontology/NCBITAXON/4565>;
.

bkr:pmid_26044828 a agri:ScholarlyPublication;
	dc:title "Heterologous expression and transcript analysis of gibberellin biosynthetic genes..."
	agri:pmedId "26044828";
	agri:authorList "Pearce S, Huttly AK, Prosser IM, Li YD, Vaughan SP, ...";
.
```

This is similar to the [MIAPPE use case](../miappe-use-case/README.md).

### Gene expression levels

```json
# Description of gene and condition in which it is expressed
#
bkr:gene_traescs1a02g030900 a bioschema:Gene;
	agri:accession "TRAESCS1A02G030900";
.

bkr:cond_outer_pericarp a agri:StudyFactor; 
  schema:prefName "outer pericarp";
  # These can come from eg, manual curation or auto-annotation
  # (of course multiple terms are possible)
  schema:additionalType
    <http://purl.obolibrary.org/obo/PO_0009084>
.

# expression statement
#

# For quick access, you might redundantly state it without attributes
bkr:gene_traescs1a02g030900 bioschema:expressedIn bkr:cond_outer_pericarp.

# Then, add attributes via reification
bkr:gxaexp_E-MTAB-3103_traescs1a02g030900_outer_pericarp a rdfs:Statement;
	agri:score "low"; # agri:score accomodates any type of score and can have subclasses (eg, pvalue)
	rdf:subject bkr:gene_traescs1a02g030900;
	rdf:predicate bioschema:expressedIn;
	rdf:object bkr:cond_outer_pericarp;
	agri:evidence bkr:exp_E-MTAB-3103 # experiment is linked as the entity that provides evidence for it
.
```

## Conversion realisation and workflow

GXA doesn't seem to have a complete API to get all the information we wanted for the modelling reported below. So we had to mix manual operations, script-automated steps and API/download services.  

Details are:
1. We started from web browsing all the experiments about an organism of interest, eg, Triticum. This is an option available in the [home page of their web site](https://www.ebi.ac.uk/gxa/home). We repeated all the hereby steps for Arabidopsis too.
   * For the moment, we picked baseline experiments only (ie, NGS).
2. We copy-pasted the corresponding [experiment list](https://www.ebi.ac.uk/gxa/experiments?species=triticum%20aestivum&experimentType=baseline) into Excel and manually cleaned it, keeping the "Experiment" column only (ie, title and link to the experiment page). We saved that as [gxa-exps.xlsm](gxa-exps.xlsm). This file also contains a macro function to extract URLs from hypertext, which we used to obtain a second column with URLs.
3. We exported the resulting two columns sheet as TSV: [wheat](gxa-wheat-exps.tsv), [arabidopsis](gxa-arabidopsis-exps.tsv)
4. We wrote the [ae-download](ae-download.py) script (and linked modules), which uses the TSVs above (one at a time) to extract the experiment accession and then a known location, from which we could fetch the experiment's metadata file (which is available as [IDF/MAGETAB](https://www.ebi.ac.uk/arrayexpress/help/magetab_spec.html)). The script uses such raw data to build RDF descriptions `data/*-exp.ttl` ([arabidopsis](data/arabidopsis-exp.ttl), [wheat](data/wheat-exp.ttl))
5. We wrote and run the [gxa-download](ae-download.py), to process the same TSV and download GXA results from known URLs. Such results were used to build RDF about gene/condition expression levels.
6. Conditions available as strings were annotated using the [annotator service from AgroPortal](http://agroportal.lirmm.fr/annotator). This is done by the [gxa-conditions-download](gxa-conditions-download.py) script, which, again, uses the experiment list's TSV.
   * Annotations [were saved as RDF](data/gxa-conditions.ttl), using the same string-minted URIs generated by the other scripts, which ensures the automatic merge of the final results.
   * This step is provisional. GXA has links from condition labels and samples, plus their own (manually curated and automatic) annotations, which we want to use in future.
7. Generated RDF files in [data/](data) were uploaded into our Knetminer SPARQL endpoint (TODO: link).

The whole pipeline (except the last point), or part of it, can be re-ran for both the species considered via the [download-all](download-all.sh) script.