"""Sample ElasticSearch Simulation"""

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, index, response

HOST = "http://localhost"
PORT = "9200"

# Connect to 'http://localhost:9200'
es = Elasticsearch()

query = {
    "any": "data",
    "timestamp": datetime.now()
}

# Datetimes will be serialized:
# es.index(
#     index="my_index_001",
#     id="mi_001",
#     document=query
# )
es.index(
    index="my_index_001",
    doc_type="_doc",
    id="mi_001",
    body=query
)

# ...but not deserialized
test1 = es.get(
    index="my_index_001",
    doc_type="_doc",
    id="mi_001",
)

# ...but not deserialized
test2 = es.get(
    index="my_index_001",
    doc_type="_doc",
    id="mi_001",
)['_source']


print("--------------------------------------------")
print(test1)
print("--------------------------------------------")
print(test2)
print("--------------------------------------------")


s = Search(using=es, index="my_index_001")
sq = s.query(
    "match",
    any="data"
)
res = sq.execute()
for hit in res:
    print(f"Score : {hit.meta.score}, Source : {hit.any, hit.timestamp}")
