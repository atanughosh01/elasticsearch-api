""" Module containing the fucntions for CRUD operation in the ES-Cluster """

# library imports
import csv
import warnings
# from typing import Any
# from requests import Response
# from datetime import datetime
from inspect import currentframe, getframeinfo
from flask import jsonify
# from elastic_transport import ConnectionTimeout
from elasticsearch import Elasticsearch, helpers

# module imports
import auth.creds as creds
import utils.const as const

frameinfo = getframeinfo(currentframe())
warnings.filterwarnings(action='ignore')

# credentials
ES_ENDPOINT = creds.ES_ENDPOINT
PASSWORD = creds.PASSWORD
USERNAME = creds.USERNAME

# constants
RECORDS = const.RECORDS
SPECIAL_CHARS = const.SPECIAL_CHARS
REQUEST_TIMEOUT = const.REQUEST_TIMEOUT
INDEX_NAME_PREFIX = const.INDEX_NAME_PREFIX
MAX_ACCESSABLE_IDX_LIM = const.MAX_ACCESSABLE_IDX_LIM

# ----------------------------------------------------------------------------------------- #


###################################### read & write operation ######################################

# def write_to_file(file_name: str, text: str):
#     debug_file = open(file_name, 'w', 'utf-8')
#     debug_file.write(text)
#     return debug_file


# def read_from_file(file_name: str) -> None:
#     debug_file = open(file_name, 'r', 'utf-8')
#     for line in debug_file.readlines():
#         print(line)
#     print()

####################################### Indexing functions #######################################


# --------------------------------- no of existing valid indices --------------------------------- #


def no_of_tdp_idx(es_obj: Elasticsearch) -> int:
    """ Returns the number of indices in the given Elasticsearch object"""

    idx_list: list = es_obj.cat.indices(
        index=(INDEX_NAME_PREFIX + '*'),
        h='index',
        s='index:desc'
    ).split()
    return len(idx_list)


# ---------------------------------------- create single --------------------------------------- #


def create_a_single_index(es_obj: Elasticsearch, _index: str) -> dict:
    """ Creates a new index in elastic cluster provided the ES instance and name of index """

    # condition-1 | if the limit has been reached, discard creation
    if no_of_tdp_idx(es_obj) >= MAX_ACCESSABLE_IDX_LIM:
        return {"message": f"Maximum limit(={MAX_ACCESSABLE_IDX_LIM}) has already been reached," +
                " Not allowed to create anymore indices unless you delete some", "status": 405}

    # condition-2 | if index name contains special characters, discard creation
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', index '{_index}' couldn't be created", "status": 405}

    # condition-3 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-4 | if no such previously created index already esists, create index
    if not es_obj.indices.exists(index=_index):
        try:
            es_obj.indices.create(
                index=_index,
                settings={
                    "index": {
                        "number_of_shards": "1",
                        "number_of_replicas": 0
                    }
                }
            )
            return {"message": f"Successfully created index: {_index}", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {frameinfo.filename}, line: {frameinfo.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to create index: {_index}", "status": 404}

    # if none of the conditions are met
    return {"message": f"Not created, index '{_index}' already exists", "status": 200}


# ---------------------------------------- delete single ---------------------------------------- #


def delete_a_single_index(es_obj: Elasticsearch, _index: str) -> dict:
    """ Deletes an existing index in elastic cluster provided the ES instance and name of index """

    # condition-1 | if index name contains special characters, discard deletion
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', index '{_index}' couldn't be deleted", "status": 405}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, delete it
    if es_obj.indices.exists(index=_index):
        try:
            es_obj.indices.delete(index=_index)
            return {"message": f"Successfully deleted index: {_index}", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {frameinfo.filename}, line: {frameinfo.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to delete index: {_index}", "status": 404}

    # if none of the conditions are met
    return {"message": f"Index '{_index}' does not exist, nothing to delete", "status": 200}


# ---------------------------------------- insert single ----------------------------------------- #


def insert_a_single_doc(es_obj: Elasticsearch, _index: str, _doc_id: str, _doc: dict) -> dict:
    """ Inserts a single document into an existing index in elastic cluster
    provided the ES instance, name of index and the document that is to be added """

    # condition-1 | if index name contains special characters, discard deletion
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', index '{_index}' couldn't index any record", "status": 405}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, insert into it
    if es_obj.indices.exists(index=_index):
        try:
            es_obj.index(
                index=_index,
                document=_doc,
                id=_doc_id,
                error_trace=True,
                timeout="30s"
            )
            return {"message": f"Record successfully loaded into index '{_index}'", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {frameinfo.filename}, line: {frameinfo.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to load record into index '{_index}'", "status": 404}

    # if none of the conditions are met
    return {"message": f"'{_index}' doesn't exist, create this index first", "status": 200}


# --------------------------------------- insert multiple ---------------------------------------- #


def insert_multiple_docs_from_csv(es_obj: str, _index: str, _filename: str) -> dict:
    """ Inserts documents in bulk (in one go) into an existing index in elastic cluster
    provided the ES instance, name of index and the filname that is to be added """

    # condition-1 | if index name contains special characters, discard deletion
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', index '{_index}' couldn't index any record", "status": 405}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

   # condition-3 | if that index does not esist, create it
    if not es_obj.indices.exists(index=_index):
        create_a_single_index(es_obj, _index)

    with open(_filename, 'r') as _file:
        try:
            reader = csv.DictReader(_file)
            helpers.bulk(
                client=es_obj,
                actions=reader,
                index=_index
            )
            return {"message": f"Records successfully loaded into index '{_index}'", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {frameinfo.filename}, line: {frameinfo.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to load records into index '{_index}'", "status": 404}



####################################### Searching functions #######################################

def search_by_id(es_obj, index_name, doc_id):
    """Searches the index for a given document id"""

    res = es_obj.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    "_id": doc_id
                }
            }
        }
    )
    return jsonify(res)


def search_by_key_val():
    """Searches"""


def search_by_time_range():
    """Searches"""


def search_by_keyword():
    """Searches"""


def search_by_full_text():
    """Searches"""
