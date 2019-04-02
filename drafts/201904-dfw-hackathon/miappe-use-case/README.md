# Modelling MIAPPE

## General Notes
  * MIAPPE was mapped to ISA, and this is used in eg, http://cropnet.pl/plantphenodb/
    * We took *Wisniewska et al, 2017* from there as an example.
  * MIAPPE docs:
    * [MIAPPE Diagram](https://github.com/MIAPPE/MIAPPE/tree/master/MIAPPE_Checklist-Data-Model-v1.1)
    * [MIAPPE checklist](https://github.com/MIAPPE/MIAPPE/blob/master/MIAPPE_Checklist-Data-Model-v1.1/MIAPPE_Checklist-Data-Model-v1.1.pdf)
    * [Mappings in ISA-Tab Phenotyping](https://github.com/MIAPPE/ISA-Tab-for-plant-phenotyping/blob/master/MIAPPE-ISATab%20mapping.pdf) 


## Modelling with in agrischemas
  * `bioschema:Study`, as in MIAPPE
    * an Investigation is an `bioschema:Study` with the investiation `schema:additionalType`, which points to other `bioschema:Study`(es), via `schema:hasPart`/`schema:isPartOf`
	* we need a new `schema:PropertyValue` subclass to track MIAPPE Environment Param (which can be linked to `bioschema:Study` via `schema:additionalProperty`)
	* `agri:StudyFactor`(s) can be linked to each of studies, samples, data file, observed value.
  * `bioschema:Sample`, includes MIAPPE sample, ISA-Tab source. The latter includes MIAPPE biological material, observational unit values
  * Samples can be linked one each-other by an `schema:Action`. This might include:
    * `bioschema:LabProtocol` (which, in the case of MIAPPE has subtypes rooting, growth, treatement, etc. These protocols have variables like watering, pesticide, etc).
      * So, we need LabProtocol as subclass of action.
		* Other events (MIAPPE/Event)
  * Samples can be linked to `schema:DataDownload`, which in turn can be linked to `schema:variableMeasured`. Target value is `agri:ObservedValue` (to be modelled).
    * an `agri:ObservedValue` can be `schema:additionalProperty` of Study
    * There isn't much need for assay. Could be an event like data collection from samples
  

Here it is a diagram (made with [yED](https://www.yworks.com/products/yed), 
[original file here](agrischema-miappe-modelling.graphmlz)):

![MIAPPE modelling](agrischema-miappe-modelling.png)
