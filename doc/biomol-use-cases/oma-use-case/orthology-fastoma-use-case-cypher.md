# Homology/FastOMA modelling for Labelled Property Graphs

This is a translation from the [RDF model](orthology-fastoma-use-case.ttl) to systems
using simpler LPGs, like Neo4j. The example has some internal KnetMiner terminology, 
but we mention how to generalise it where applicable.

## Homology Trees

As discussed in the [main README](README.md), a homology tree is a synthetic view of a subtree of HOGs (or alike) which omits the topological details and instead assigns genes or proteins directly to the tree.

```cypher
/* 
 * Homology Tree node
 */
(hom_tree_0:HomologyTree:Concept{ 
	// We still use this, in future it will become something like id or knetId
	ondexId: "1234",
	// Current way to represent accessions. Currently, it also needs identifier->Accession 
	// relationships (ie, Ondex accessions), in future it will be a list of strings
	// In principle, this could be the same as the identifier of the root HOG
	identifier: "HOGTree:E0284567",
	// Representative of the usual name, description, etc, add if any
	prefName: "FastOMA Tree 1234"
})

// Gene/Proteins can be linked either with hasPart or, in the opposite direction, with partOf.
- [ :hasPart{
	// You can report all the OMA properties if you want, we recommend to identify them by prefix
  `OMA:hoglevel`: "Arabidopsis",
	`OMA:family_p`: 505.34177514375125,
	...
	// This is still the way it works with imports from Ondex. If you define a FastOMA Evidence object,
	// you'll get these links as string properties. In future, we will want to switch to simpler 
	// strings.
	evidence: "http://knetminer.org/data/rdf/terms/biokno/FastOMA"
} ]

// The usual Gene nodes
-> (gene_hsa1:Gene:Concept{
	ondexId: "5678",
	identifier: "ATG1G01010",
	prefName: "HSA1",
	// In the future, it should be taxonomicRange, as per Bioschemas
	taxId: "3702"
})

// 1-n hasPart relationships (or n-1 partOf) can be added to map multiple genes/proteins to a tree
// Shared container
(hom_tree_0)
- [ :hasPart{ 
	`OMA:hoglevel`: "Arabidopsis",
	`OMA:family_p`: 871.8216225627258,
	...
} ] -> (gene_hsa1:Gene:Concept{
	ondexId: "9012",
	identifier: "ATG1G01020",
	prefName: "PTR1",
	taxId: "3702"
})
```

## Tree details

As said above, we forsee Homology trees as the primary structure to use to navigate homology links between genes or proteins. However, the following is what it could be used if we decide to include tree details.

```cypher
// The tree->root link
(hom_tree_0:HomologyTree:Concept)

- [:hasTreeRoot] ->

// HierarchicalParalogGroup is a possible alternative
(hog_0:HierarchicalOrthologyGroup:Concept{
	ondexId: "667678",
	// As said above, the tree ID could be the same as its root ID
	identifier: "HOG:E0284567",
	prefName: "HOG E0284567"
})

// The tree structure. As said elsewhere, this is example 4 at https://orthoxml.org/0.4/orthoxml_doc_v0.4.html

(hog_0:HierarchicalOrthologyGroup:Concept{
	ondexId: "667678",
	identifier: "HOG:E0284567",
	prefName: "HOG E0284567"
})

// A direct child
- [:hasPart] -> 

(hog_0_0:HierarchicalOrthologyGroup:Concept{
	ondexId: "667679",
	identifier: "HOG:E0284567.0.1",
	prefName: "HOG E0284567.0.1"
})

// And another child
(hog0) - [:hasPart] ->

// Note this is a paralogous group
(pag_0_1:ParalogousGroup:Concept{
	ondexId: "667680",
	identifier: "HOG:E0284567.0.2",
	prefName: "HOG E0284567.0.2"
})

// And then a child of a child
- [:hasPart] ->

(hog_0_1_0:HierarchicalOrthologyGroup:Concept{
	ondexId: "667681",
	identifier: "HOG:E0284567.0.1.0",
	prefName: "HOG E0284567.0.1.0"
})

// And the genes at leaf nodes

(hog_0_0) -> [:hasPart] -> (gene_hsa1) // gene node, as mentioned above
(hog_0_0) -> [:hasPart] -> (gene_ptr1) 

(hog_0_1_0) - [:hasPart] -> (gene_rno1)
(hog_0_1_0) - [:hasPart] -> (gene_mmu1)

// And so on for the rest of the tree
(pag_0_1) - [:hasPart] -> (hog_0_1_1:HierarchicalOrthologyGroup:Concept{...})

(hog_0_1_1) - [:hasPart] -> (gene_rno2)
(hog_0_1_1) - [:hasPart] -> (gene_mmu2)
```