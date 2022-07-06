# ElasticSearchAPI

**ELastic** : A timesries DB primarily use to fetch the KPI and insites from large data set.

### Objective:

1. Functionality to load the data in the system:
    * Bulk indexing the data (from file)
      - file should be of `csv`or `json` data file.
    * Inserting a single document

2. Functionality to search the data:
    * Search on the basis of unique id.
    * Search on the basis of any specific key value.
    * Search and fetch the records in the time range given as input.
    * Keyword-based search or full-text search capability.
    * Aggregated info my data.

3. Index creation
   * Create Indices
   * Assign ID-s

### Required tools / info

1. Elasic end-point and credentials.
2. Code environment
3. Desired Mapping of the index 
    - Timestamp is mandatory in the document that are indexed.


#### Refer to [this](https://elasticsearch-dsl.readthedocs.io/en/latest/index.html) for help
