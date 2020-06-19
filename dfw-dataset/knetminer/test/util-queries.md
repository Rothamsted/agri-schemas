# Utility Queries

## Relevant classes

```sql
PREFIX schema: <http://schema.org/>
prefix bioschema: <http://bioschemas.org/>
prefix agri:  <http://agrischemas.org/>

select ?C (COUNT (?o) AS ?ct) {
  ?o a ?C

  FILTER ( 
    strstarts ( STR (?C), STR ( agri: ) ) 
    || strstarts ( STR (?C), STR ( schema: ) ) 
    || strstarts ( STR (?C), STR ( bioschema: ) ) 
  )
}
GROUP BY ?C
ORDER BY DESC ( ?ct )
LIMIT 10
```

