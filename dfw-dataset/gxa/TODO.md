# TODO
## We need to redo everything :-(
* [GXA API](https://www.ebi.ac.uk/gxa/json/experiments) that is the equivalent of the experiments table
  * Unfortunately, seems to be ignoring any filter (specie, baseline/diff, etc), so you get all from this 
    URL, then you've to filter the JSON
* To speed-up things, the experiments above must be cross-compared to the 
  [AE API](https://www.ebi.ac.uk/arrayexpress/json/v3/experiments?gxa=true&species=%22arabidopsis%20thaliana%22)
  * And this API must also be used for the experiment's RDF, NOT the IDF
* TPM/DEX details can be downloaded without EBI throttling concerns, since single downloads are pretty slow.
  This also means they can be done in parallel
    