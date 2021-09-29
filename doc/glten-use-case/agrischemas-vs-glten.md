## Notes about GLTen and MILAX

## Initial mappings to AgriSchemas
<table>
    <tr>
        <td>GLTen</td>
        <td>AgriSchemas</td>
    </tr>
    <tr>
        <td>Objective, Description, Farm Operation Data, Sample Archive, Samples Available</td>
        <td>Study and its properties. Design object requires further investigation: is it a treatment?
        Do we need a protocol type/application flag?</td>
    </tr>
    <tr>
        <td>Design Period (Design Type, Description, Factor)</td>
        <td>A Study which is part of the top-level Investigation (might be something like Study type = Period Study)</td>
    </tr>
    <tr>
        <td>Design Period (Measurments)</td>
        <td>A combination of Data and ObservedValue, to reflect what data you achieved from a field/sample</td>
    </tr>
    <tr>
        <td>Design Period (No of plots/blocks/replicates/etc)</td>
        <td>According to MIAPPE, it's the "Observation unit level hierarchy" field, associated to Study. 
        But probably requires further Study qualifiers. Or, some protocol qualifier (ISA-Tab put these 
        into Sampling Protocol, maybe something like "Design Protocol" would be more appropriate)</td>
    </tr>
    <tr>
        <td>Publications</td>
        <td>Linked to the studies, or the top investigation</td>
    </tr>
    <tr>
        <td>Crops</td>
        <td>Sample, Source organisms</td>
    </tr>
    <tr>
        <td>Crop Rotations</td>
        <td>It's a specialisation of Treatment, describes how things are cultivated in the field</td>
    </tr>
    <tr>
        <td>Rotation Phase</td>
        <td>It's a step in the rotations/treatment</td>
    </tr>
    <tr>
        <td>Factors</td>
        <td>Like MIAPPE factors, with the type+role(eg, ferrtiliser) properties. Factor levels are factor 
        values, factor combinations are composite (partOf) factors. Application is a factor property 
        (which should match a possible link with field/plots)</td>
    </tr>
    <tr>
        <td>Funding Grants</td>
        <td>TODO, probably something similar to iao:information content entity</td>
    </tr>
</table>

A [draft](glten-miappe-mappings.pdf) is available regarding more details and aligment between GLTen, MIAPPE, bioschemas/schema


## Notes (about field trials in general, to be moved upwards)

The most general model between this and MIAPPE could be:  

  1. Initial components (Site, Soil, Cultivated Crops) as source samples
  1. Design or treatment, including sampling (which might have multiple steps)
  1. Other events (eg, weather)
  1. Measurements (associated to factor values)
  1. Data


## Links
  * [GLTen Metadata Portal](https://www.glten.org/)
  * [GLTen GitHub](https://github.com/GLTEN)