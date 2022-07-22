""" Module containing the fucntions for CRUD operation in the ES-Cluster """

# library imports
import csv
from inspect import currentframe
from inspect import getframeinfo
from elasticsearch import helpers
from elasticsearch import Elasticsearch
from elastic_transport import ConnectionTimeout

# module imports
from api.auth import creds
from api.utils import const
from api.utils import status as sc


# credentials
ES_ENDPOINT = creds.ES_ENDPOINT
PASSWORD = creds.PASSWORD
USERNAME = creds.USERNAME

# constants
RECORDS = const.RECORDS
SPECIAL_CHARS = const.SPECIAL_CHARS
REQUEST_TIMEOUT = const.REQUEST_TIMEOUT
INDEX_NAME_PREFIX = const.INDEX_NAME_PREFIX
MAX_IDX_LIM = const.MAX_IDX_LIM


# --------------------------------- no of existing valid indices --------------------------------- #

def no_of_tdp_idx(_es: Elasticsearch) -> int:
    """ Returns count of total indices currently available on es-cluster """

    idx_list: list = _es.cat.indices(
        index=(INDEX_NAME_PREFIX + '*'),
        h='index',
        s='index:desc'
    ).split()
    return len(idx_list)


# ----------------------------------------- create single ---------------------------------------- #

def create_a_single_index(_es: Elasticsearch, _index: str) -> dict:
    """ Creates a new index in elastic cluster provided the ES instance and name of index """

    # condition-1 | if the limit has been reached, discard creation
    if no_of_tdp_idx(_es) >= MAX_IDX_LIM:
        return {"message": f"Maximum limit(={MAX_IDX_LIM}) of indices has already been reached," +
                " not allowed to create anymore indices unless you delete some",
                "status": sc.HTTP_406_NOT_ACCEPTABLE}

    # condition-2 | if index name contains special characters, discard creation
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', index '{_index}' couldn't be created",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-3 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-4 | if no such previously created index already esists, create index
    if not _es.indices.exists(index=_index):
        f_info = getframeinfo(currentframe())
        try:
            _es.indices.create(
                index=_index,
                settings={
                    "index": {
                        "number_of_shards": "1",
                        "number_of_replicas": 0
                    }
                }
            )
            return {"message": f"Successfully created index: {_index}", "status": sc.HTTP_200_OK}
        except Exception as ex:
            print(f"\nError in file: {f_info.filename}, line: {f_info.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to create index: {_index}", "status": sc.HTTP_404_NOT_FOUND}

    # if none of the conditions are met
    return {"message": f"Not created, index '{_index}' already exists",
            "status": sc.HTTP_208_ALREADY_REPORTED}


# ----------------------------------------- delete single ---------------------------------------- #

def delete_a_single_index(_es: Elasticsearch, _index: str) -> dict:
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
    if _es.indices.exists(index=_index):
        f_info = getframeinfo(currentframe())
        try:
            _es.indices.delete(index=_index)
            return {"message": f"Successfully deleted index: {_index}", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {f_info.filename}, line: {f_info.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to delete index: {_index}", "status": 404}

    # if none of the conditions are met
    return {"message": f"Index '{_index}' does not exist, nothing to delete",
            "status": sc.HTTP_400_BAD_REQUEST}


# ---------------------------------------- insert single ----------------------------------------- #

def insert_a_single_doc(_es: Elasticsearch, _index: str, _doc_id: str, _doc: dict) -> dict:
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
    if _es.indices.exists(index=_index):
        f_info = getframeinfo(currentframe())
        try:
            _es.index(
                index=_index,
                document=_doc,
                id=_doc_id,
                error_trace=True,
                timeout="30s"
            )
            return {"message": f"Record successfully loaded into index '{_index}'", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {f_info.filename}, line: {f_info.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to load record into index '{_index}'", "status": 404}

    # if none of the conditions are met
    return {"message": f"'{_index} doesn't exist, create this index to insert records'",
            "status": sc.HTTP_400_BAD_REQUEST}


# --------------------------------------- insert multiple ---------------------------------------- #

def insert_multiple_docs_from_csv(_es: Elasticsearch, _index: str, _filename: str) -> dict:
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
    if not _es.indices.exists(index=_index):
        create_a_single_index(_es, _index)

    with open(file=_filename, mode='r', encoding='utf-8') as _file:
        f_info = getframeinfo(currentframe())
        try:
            reader = csv.DictReader(_file)
            helpers.bulk(
                client=_es,
                actions=reader,
                index=_index
            )
            return {"message": f"Records successfully loaded into index '{_index}'", "status": 200}
        except Exception as ex:
            print(f"\nError in file: {f_info.filename}, line: {f_info.lineno},\nDesc: {ex}\n")
            return {"message": f"Failed to load records into index '{_index}'", "status": 404}


# --------------------------------------- search by id ---------------------------------------- #

def search_record_from_index_by_given_id(_es: Elasticsearch, _index: str, _doc_id: str) -> dict:
    """ searches by id """

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                body={
                    "query": {
                        "match": {
                            "_id": _doc_id
                        }
                    }
                },
                request_timeout=REQUEST_TIMEOUT
            )
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record with id={_doc_id} exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return res["hits"]["hits"][0]["_source"]

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# ----------------------------------- search all by key-value ------------------------------------ #

def search_records_from_index_by_given_key_and_value(_es: Elasticsearch, _index: str, _key: str, _val: str):
    """ Searches records by given key and value """

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        record_list = []
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "match": {
                        _key: _val
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                record_list.append(arr["_source"])
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record with key='{_key}' and value='{_val}' exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return record_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# ---------------------------------- search field by key-value ----------------------------------- #

def search_field_from_index_by_given_key_and_value(_es: Elasticsearch, _index: str, _field: str, _key: str, _val: str):
    """ Searches specific field from records in an index where given key matches given value """

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        field_list = []
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "match": {
                        _key: _val
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                # field_list.append(arr["_source"][_field])
                field_list.append(arr["_source"].get(_field))
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record with key='{_key}' and value='{_val}' exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return field_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# ---------------------------------- search all by time-range ------------------------------------ #

def search_records_from_index_by_time_range(_es: Elasticsearch, _index: str, _date_field: str, _start: str, _end: str):
    """ Searches all records that are in betwwen the specified time-range of certain date-field """

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        record_list = []
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "range": {
                        _date_field: {
                            "gte": _start,
                            "lte": _end
                        }
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                record_list.append(arr["_source"])
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record in given time-range exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return record_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# --------------------------------- search field by time-range ----------------------------------- #

def search_field_from_index_by_time_range(_es: Elasticsearch, _index: str, _date_field: str, _field: str, _start: str, _end: str):
    """ Searches specific field from records that are in the time-range of certain date-field """

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        data_list = []
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "range": {
                        _date_field: {
                            "gte": _start,
                            "lte": _end
                        }
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                # data_list.append(arr["_source"][_field])
                data_list.append(arr["_source"].get(_field))
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record in given time-range exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return data_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# ----------------------------------- search by keyword ------------------------------------ #

def search_all_occurances_of_keyword_in_index(_es: Elasticsearch, _index: str, _keyword: str):
    """Searches and returns all records where the specified keyword occurrs"""

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        record_list = []
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "query_string": {
                        "query": _keyword
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                record_list.append(arr["_source"])
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record in given time-range exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return record_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}


# ----------------------------------- full text search ------------------------------------ #

def search_all_occurances_of_text_in_index(_es: Elasticsearch, _index: str, _text: str):
    """Searches and returns all records where the text or sub-string
    of the text occurrs (partial-search/similar to google search)"""

    # condition-1 | if index name contains special characters, discard search
    allowed = True
    for char in SPECIAL_CHARS:
        if char in _index:
            allowed = False
    if not allowed:
        return {"message": "IndexName must not contain any special chars other than" +
                f" '_' or '-', couldn't find any record from index '{_index}'",
                "status": sc.HTTP_405_METHOD_NOT_ALLOWED}

    # condition-2 | if indexname does not follow the defined rules, set the indexname accordingly
    if not _index.startswith(INDEX_NAME_PREFIX):
        _index = INDEX_NAME_PREFIX + _index

    # condition-3 | if that index esists, perform the search operation
    if _es.indices.exists(index=_index):
        record_list = []
        _str = '*' + _text + '*'
        f_info = getframeinfo(currentframe())
        try:
            res = _es.search(
                index=_index,
                query={
                    "query_string": {
                        "query": _str
                    }
                },
                size=RECORDS,
                request_timeout=REQUEST_TIMEOUT
            )
            for arr in res["hits"]["hits"]:
                record_list.append(arr["_source"])
        except ConnectionTimeout as _c:
            print(f"Error in file: {f_info.filename}, line: {f_info.lineno + 1}, Desc: {_c}")
            return {"message": "Request timed out", "status": sc.HTTP_408_REQUEST_TIMEOUT}

        # if the response body is empty
        if res["hits"]["hits"] == []:
            return {"message": f"No record in given time-range exists in index '{_index}'",
                    "status": sc.HTTP_404_NOT_FOUND}

        # success, return the json data
        return record_list

    # if none of the conditions are met
    return {"message": f"Index '{_index}' doesn't exist", "status": sc.HTTP_404_NOT_FOUND}
