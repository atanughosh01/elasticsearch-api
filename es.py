"""Sample ElasticSearch Simulation"""

from datetime import datetime
from elasticsearch import Elasticsearch

HOST = "http://localhost"
PORT = "9200"

# Connect to 'http://localhost:9200'
es = Elasticsearch(HOST + ":" + PORT)

query = {
    "any": "data",
    "timestamp": datetime.now()
}

# Datetimes will be serialized:
es.index(
    index="my_index_001",
    id="mi_001",
    document=query
)

# ...but not deserialized
test1 = es.get(
    index="my_index_001",
    id="mi_001",
)

# ...but not deserialized
test2 = es.get(
    index="my_index_001",
    id="mi_001",
)['_source']


print("--------------------------------------------")
print(test1)
print("--------------------------------------------")
print(test2)
print("--------------------------------------------")
