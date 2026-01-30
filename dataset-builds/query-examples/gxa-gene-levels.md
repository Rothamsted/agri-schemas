# GXA Gene expression levels

Shows genes and conditions in which they're expressed, plus links to the studies on which this is based. Significance figures are reported too, considering what they are for differential expression or absolute expression analysis (i.e., p-values, fold changes vs TPMs).

[See it live](https://tinyurl.com/26ccsdk8)

**WARNING**: The SPARQL Query editor has a "Strict checking of void variables" option, which is set by default. This query **does not work** until you disable that option (they don't comply with SPARQL 1.1 by default, welcome to the Semantic Web world...).


```sql
PREFIX bk: <http://knetminer.org/data/rdf/terms/biokno/>
PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
PREFIX bkg: <http://knetminer.org/data/rdf/resources/graphs/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX agri: <http://agrischemas.org/>
PREFIX bioschema: <https://bioschemas.org/>
PREFIX schema: <https://schema.org/>


SELECT ?gene ?geneAcc ?condLabel ?studyTitle ?study ?condTerm ?scoreStr
WHERE {
 ?gene a bioschema:Gene;
    schema:identifier ?geneAcc.

  # Let''s focus on a few genes
  FILTER ( UCASE (STR ( ?geneAcc ) ) IN ( 
    'TRAESCS2D02G242700','TRAESCSU02G073600','TRAESCS7D02G050400',
    'TRAESCS6D02G393900','TRAESCS7D02G503700','TRAESCS7D02G431500',
    'TRAESCS1D02G090100','TRAESCS1D02G156000','TRAESCS2B02G046700',
    'TRAESCS4A02G318000','TRAESCS1A02G443400','TRAESCS7D02G241300',
    'TRAESCS6D02G107700','TRAESCS5D02G247200'
  ))  


  ?gene bioschema:expressedIn ?condition.

  ?expStatement a rdf:Statement;
    rdf:subject ?gene;
    rdf:predicate bioschema:expressedIn;
    rdf:object ?condition;
    agri:evidence ?study.


  # Getting the significance scores
  {
    # Differential expression analysis
    ?expStatement agri:pvalue ?pvalue; agri:log2FoldChange ?foldChange. 
    FILTER ( ?pvalue < 1e-3 && ABS ( ?foldChange ) > 1.5 )
    BIND ( CONCAT ( "p-value: ", ?pvalue, ", log2 FC: ", ?foldChange ) AS ?scoreStr )
  }
  UNION {
    # Baseline expression analysis
    ?expStatement agri:ordinalTpm ?ordinalTpm; agri:tpmCount ?tpm.
    # According to GXA docs low/medium/high is defined by TPM thresholds
    # (<=10, <=1000, <oo)
    FILTER ( ?ordinalTpm in ('medium', 'high') ) 
    BIND ( CONCAT ( ?tpm, " TPM" ) AS ?scoreStr )
  }


  # Condition and study attributes
  #
  ?condition schema:name ?condLabel.
  OPTIONAL { ?condition dc:type ?condTerm. }

  ?study 
    dc:title ?studyTitle

}
ORDER BY ?study ?gene
LIMIT 1000
```