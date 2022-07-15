""" Module cantaining the app and routes for hitting the respective APIs """

# library imports
import warnings
from datetime import datetime
from inspect import currentframe, getframeinfo
from requests import Response
from flask import Flask, jsonify, request
# from elastic_transport import ConnectionTimeout
from elasticsearch import Elasticsearch

# module imports
import elk
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
REQUEST_TIMEOUT = const.REQUEST_TIMEOUT
ES_CONNECT_TIMEOUT = const.ES_CONNECT_TIMEOUT
ES_CONNECT_MAX_RETRIES = const.ES_CONNECT_MAX_RETRIES

# ----------------------------------------------------------------------------------------- #

# elasticsearch instance
es = Elasticsearch(
    [ES_ENDPOINT],
    basic_auth=(USERNAME, PASSWORD),
    verify_certs=False,
    ssl_show_warn=False,
    timeout=ES_CONNECT_TIMEOUT,
    max_retries=ES_CONNECT_MAX_RETRIES
)


# flask app instance
app = Flask(__name__)


# homepage- http://127.0.0.1:5000/
@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return "Hello Elastic!"


# ----------------------------------------- INDEXING ----------------------------------------- #


# http://127.0.0.1:5000/create_index?index=idx
@app.route("/create_index", methods=["POST"])
def create_index():
    """Creates a new index"""

    try:
        idx_name: str = request.args.get("index")
        res = elk.create_a_single_index(es, idx_name)
        return res
    except Exception as ex:
        print(f"\nException in /create_index api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# http://127.0.0.1:5000/delete_index?index=idx
@app.route("/delete_index", methods=["POST"])
def delete_index():
    """Deletes a single index"""

    try:
        idx_name: str = request.args.get("index")
        res = elk.delete_a_single_index(es, idx_name)
        return res
    except Exception as ex:
        print(f"\nException in /delete_index api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# http://127.0.0.1:5000/add_single/into/idx
@app.route("/add_single/into/<idx_name>", methods=["POST"])
def single_insert(idx_name: str):
    """Inserts a single record into an index"""

    try:
        req_arg = request.get_json()
        _empId: str = req_arg.get("empId")
        _firstName: str = req_arg.get("firstName")
        _lastName: str = req_arg.get("lastName")
        _dept: str = req_arg.get("dept")
        _phnNum: str = req_arg.get("phnNum")
        _emailAddr: str = req_arg.get("emailAddr")
        _joinDate: str = req_arg.get("joinDate")
        docID: str = "100" + _empId
        doc = {
            "empId": _empId,
            "firstName": _firstName,
            "lastName": _lastName,
            "dept": _dept,
            "phnNum": _phnNum,
            "emailAddr": _emailAddr,
            "joinDate": _joinDate,
            "@timestamp": str(datetime.now())
        }
    except Exception as exc:
        print(
            f"\nException in /single_insert api while fetching args: {exc}\n")
        return {"message": f"Caught Exception while fetching args: {exc}", "status": 404}

    try:
        res = elk.insert_a_single_doc(es, idx_name, docID, doc)
        return res
    except Exception as ex:
        print(f"\nException in /single_insert api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# http://127.0.0.1:5000/add_multiple?index=idx_csv&file=csv/emp.csv
@app.route("/add_multiple", methods=["POST"])
def bulk_insert():
    """Inserts multiple documents in bulk into an index"""

    try:
        idx_name: str = request.args.get("index")
        file_name: str = request.args.get("file")
        res = elk.insert_multiple_docs_from_csv(es, idx_name, file_name)
        return res
    except Exception as ex:
        print(f"\nException in /single_insert api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# ----------------------------------------- SEARCHING ----------------------------------------- #


# http://127.0.0.1:5000/get?index=tdp_idx&id=100
@app.route('/get', methods=['GET'])
def get() -> Response:
    """Get document by id"""

    _index = request.args.get('index')
    _doc_id = request.args.get('id')
    res = es.get(
        index=_index,
        id=_doc_id
    )
    return jsonify(res['_source'])


# http://127.0.0.1:5000/search/index=tdp_idx&id=100
@app.route('/search/index=<_index>&id=<_doc_id>', methods=['POST'])
def search_by_id(_index: str, _doc_id: str):
    """Searches"""

    res = es.search(
        index=_index,
        query={
            "match": {
                "_id": _doc_id
            }
        },
        timeout="1ms"
    )
    return jsonify(res["hits"]["hits"][0]["_source"])


# http://127.0.0.1:5000/search_all
@app.route('/search_all', methods=['POST'])
def search_all_by_key_val():
    """Searches"""

    req_arg = request.get_json()
    _index: str = req_arg.get("index")
    _key: str = req_arg.get("key")
    _val: str = req_arg.get("val")
    res = es.search(
        index=_index,
        query={
            "match": {
                _key: _val
            }
        },
        size=RECORDS
    )
    record_list = []
    for arr in res["hits"]["hits"]:
        # To-Do : process
        record_list.append(arr['_source'])
    return jsonify(record_list)


# http://127.0.0.1:5000/search/fName/where/index=tdp_idx&key=dept&val=Manager
@app.route('/search_data', methods=['POST'])
def search_data_by_key_val():
    """Searches"""

    req_arg = request.get_json()
    _index: str = req_arg.get("index")
    _data: str = req_arg.get("data")
    _key: str = req_arg.get("key")
    _val: str = req_arg.get("val")
    res = es.search(
        index=_index,
        query={
            "match": {
                _key: _val
            }
        },
        size=RECORDS
    )
    data_list = []
    print(res["hits"]["hits"])
    for arr in res["hits"]["hits"]:
        data_list.append(arr['_source'][_data])
        # data_list.append(arr['_source'].get(_data))
    return jsonify(data_list)


# http://127.0.0.1:5000/search/index=tdp_idx/time_range/from=2020-05-10&upto=2021-03-25
@app.route('/search/index=<_index>/time_range/from=<_start>&upto=<_end>', methods=['POST'])
def search_all_by_time_range(_index: str, _start: str, _end: str):
    """Searches"""

    _query = {
        "range": {
            "jDt": {
                "gte": _start,
                "lte": _end
            }
        }
    }
    res = es.search(
        index=_index,
        query=_query,
        size=RECORDS
    )
    record_list = []
    for arr in res["hits"]["hits"]:
        record_list.append(arr['_source'])
    return jsonify(record_list)


# http://127.0.0.1:5000/search/jDt/where/index=tdp_idx/range/from=2020-05-10&upto=2021-03-25
@app.route('/search/<_data>/where/index=<_index>/range/from=<_start>&upto=<_end>', methods=['POST'])
def search_data_by_time_range(_index: str, _start: str, _end: str, _data: str):
    """Searches"""

    _query = {
        "range": {
            "jDt": {
                "gte": _start,
                "lte": _end
            }
        }
    }
    res = es.search(
        index=_index,
        query=_query,
        size=RECORDS
    )
    data_list = []
    for arr in res["hits"]["hits"]:
        data_list.append(arr['_source'].get(_data))
    return jsonify(data_list)


# http://127.0.0.1:5000/search/tdp_idx/eve
@app.route('/search/<string:_index>/<string:_value>', methods=['POST'])
def key_value_term(_index, _value):
    """Searches"""

    _str = '*' + _value + '*'
    ans = es.search(
        index=_index,
        query={
            "query_string": {
                "query": _str
            }
        },
        size=RECORDS
        # request_timeout=REQUEST_TIMEOUT
    )
    record_list = []
    for arr in ans['hits']['hits']:
        record_list.append(arr['_source'])
    return jsonify(record_list)
