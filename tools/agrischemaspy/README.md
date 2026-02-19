# AgriSchemas-Py

A set of generic Python utilities to deal with biological data, ETLs, RDF manipulation, graph database utilities, and all that jazz.

**Note**: some aspects of this package are still messy and needs to be reviewed. Despite it, it is being actively used in AgriSchmas and KnetMiner projects, so we consider it reliable enough.

## Contents

See [the tests](tests/agrischemas_test/) for examples and details.

* `etltools`: general utilities for ETL operations, including:
  * `XNamespaceManagerTest`, extends the rdflib namespace manager
	* A SPARQL rule-based data mapper
	* Virtuoso utilities, such as a basic [Lucene-to-bif:contains converter](tests/agrischemas_test/etltools/virtuoso_test.py)
	* Various I/O utilities
	* RDF test utilities, such as `sparql_ask`
* `biotools`: utilities to process biological data. At the moment, it mainly contains `BioPortal`/`AgroPortal` simple clients.
* `kpyutils`: generic utilities, such as URL processing functions.


## Usage

Include it in your project by using the github URL. For instance:

```.ini
[tool.poetry.dependencies]
agrischemaspy = {
	git = "https://github.com/Rothamsted/agri-schemas.git",
	rev = "master", 
	subdirectory = "tools/agrischemaspy"
}
```

We plan to eventually migrate this project to [knetminer-etl](https://github.com/KnetMiner/knetminer-etl), the framework we are building to build large knowledge graphs in the domain of life sciences and beyond. Due to this, we for the moment, we aren't publishing it on PyPI and instead, we show how to import the library straight from GitHub.

