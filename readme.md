# elasticsearch-api

**ELastic** : A timesries DB primarily use to fetch the KPI and insites from large data set.

## Supports

1. Index creation
    * Create Indices
    * Assign ID-s
    * Timestamp is mandatory in the document that are indexed.
   
2. Functionality to load the data in the system:
    * Bulk indexing the data (from file)
    * file should be of `csv` or `json` data file.
    * Inserting a single document

2. Functionality to search the data:
    * Search on the basis of unique id.
    * Search on the basis of any specific key value.
    * Search and fetch the records in the time range given as input.
    * Keyword-based search or full-text search capability.
    * Aggregated info my data.
