"""Sample ElasticSearch Simulation"""

from datetime import datetime
from elasticsearch import Elasticsearch

HOST = "http://localhost"
PORT = "9200"

# Connect to 'http://localhost:9200'
es = Elasticsearch()

query = {
    "any": "data",
    "timestamp": datetime.now()
}


es.index(
    index="my_index_001",
    id="mi_001",
    document=None
)

test1 = es.get(
    index="my_index_001",
    id="mi_001"
)

test2 = es.get(
    index="my_index_001",
    id="mi_001"
)['_source']


print("--------------------------------------------")
print(test1)
print("--------------------------------------------")
print(test2)
print("--------------------------------------------")


s = es.search(index="my_index_001")
sq = s.query(
    "match",
    any="data"
)
res = sq.execute()
for hit in res:
    print(f"Score : {hit.meta.score}, Source : {hit.any, hit.timestamp}")
