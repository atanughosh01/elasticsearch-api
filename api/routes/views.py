""" Module cantaining the app and routes for hitting the respective APIs """

# library imports
from datetime import datetime
from flask import jsonify
from flask import request
from flask import Blueprint
from elasticsearch import Elasticsearch

# module imports
from api.service import elk
from api.auth import creds
from api.utils import const
from api.utils import status as sc


# credentials
ES_ENDPOINT = creds.ES_ENDPOINT
PASSWORD = creds.PASSWORD
USERNAME = creds.USERNAME

# constants
RECORDS = const.RECORDS
REQUEST_TIMEOUT = const.REQUEST_TIMEOUT
ES_CONNECT_TIMEOUT = const.ES_CONNECT_TIMEOUT
ES_CONNECT_MAX_RETRIES = const.ES_CONNECT_MAX_RETRIES


# elasticsearch instance
es = Elasticsearch(
    [ES_ENDPOINT],
    basic_auth=(USERNAME, PASSWORD),
    verify_certs=False,
    ssl_show_warn=False,
    timeout=ES_CONNECT_TIMEOUT,
    max_retries=ES_CONNECT_MAX_RETRIES
)


# blueprint instance
# to be registered to the Flask app
bp = Blueprint("views", __name__)


# ----------------------------------------- INDEXING ----------------------------------------- #


# http://127.0.0.1:5000/create_index?index=idx
@bp.route("/create_index", methods=["POST"])
def create_index():

    try:
        idx_name: str = request.args.get("index")
        res = elk.create_a_single_index(es, idx_name)
        return res
    except Exception as ex:
        print(f"\nException in /create_index api: {ex}\n")
        return {"message": f"Caught Exception: {ex}",
                "status": sc.HTTP_404_NOT_FOUND}


# http://127.0.0.1:5000/delete_index?index=idx
@bp.route("/delete_index", methods=["POST"])
def delete_index():

    try:
        idx_name: str = request.args.get("index")
        res = elk.delete_a_single_index(es, idx_name)
        return res
    except Exception as ex:
        print(f"\nException in /delete_index api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# http://127.0.0.1:5000/add_single/into?index=idx
@bp.route("/add_single/into", methods=["POST"])
def single_insert():

    try:
        idx_name: str = request.args.get("index")
        req_arg = request.get_json()
        _emp_id: str = req_arg.get("empId")
        _first_name: str = req_arg.get("firstName")
        _last_name: str = req_arg.get("lastName")
        _dept: str = req_arg.get("dept")
        _phn_num: str = req_arg.get("phnNum")
        _email_addr: str = req_arg.get("emailAddr")
        _join_date: str = req_arg.get("joinDate")
        doc_id: str = "100" + _emp_id
        doc = {
            "empId": _emp_id,
            "firstName": _first_name,
            "lastName": _last_name,
            "dept": _dept,
            "phnNum": _phn_num,
            "emailAddr": _email_addr,
            "joinDate": _join_date,
            "@timestamp": str(datetime.now())
        }
    except Exception as exc:
        print(f"\nException in /single_insert api while fetching args: {exc}\n")
        return {"message": f"Caught Exception while fetching args: {exc}", "status": 404}

    try:
        res = elk.insert_a_single_doc(es, idx_name, doc_id, doc)
        return res
    except Exception as ex:
        print(f"\nException in /single_insert api: {ex}\n")
        return {"message": f"Caught Exception: {ex}", "status": 404}


# http://127.0.0.1:5000/add_multiple/into?index=idx_csv&file=csv/emp.csv
@bp.route("/add_multiple/into", methods=["POST"])
def bulk_insert():

    try:
        idx_name: str = request.args.get("index")
        file_name: str = request.args.get("file")
        res = elk.insert_multiple_docs_from_csv(es, idx_name, file_name)
    except Exception as ex:
        print(f"\nException in /bulk_insert api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# ----------------------------------------- SEARCHING ----------------------------------------- #


# http://127.0.0.1:5000/get?index=tdp_idx&id=100
@bp.route("/get", methods=["GET"])
def get():

    try:
        _index: str = request.args.get("index")
        _doc_id: str = request.args.get("id")
        res = es.get(
            index=_index,
            id=_doc_id,
            refresh=True
        )["_source"]
    except Exception as ex:
        print(f"\nException in /get api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search?index=tdp_idx&id=100
@bp.route("/search", methods=["POST"])
def search_by_id():

    try:
        idx_name: str = request.args.get("index")
        doc_id: str = request.args.get("id")
        res = elk.search_record_from_index_by_given_id(es, idx_name, doc_id)
        return res
    except Exception as ex:
        print(f"\nException in /search_by_id api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_all
@bp.route("/search_all", methods=["POST"])
def search_all_by_key_value():

    try:
        req_arg = request.get_json()
        idx_name: str = req_arg.get("index")
        key: str = req_arg.get("key")
        val: str = req_arg.get("value")
        res = elk.search_records_from_index_by_given_key_and_value(es, idx_name, key, val)
    except Exception as ex:
        print(f"\nException in /search_all_by_key_value api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_field
@bp.route("/search_field", methods=["POST"])
def search_field_by_key_val():

    try:
        req_arg = request.get_json()
        idx_name: str = req_arg.get("index")
        field: str = req_arg.get("field")
        key: str = req_arg.get("key")
        val: str = req_arg.get("value")
        res = elk.search_field_from_index_by_given_key_and_value(es, idx_name, field, key, val)
    except Exception as ex:
        print(f"\nException in /search_field_by_key_val api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_range
@bp.route("/search_range", methods=["POST"])
def search_all_by_time_range():

    try:
        req_arg = request.get_json()
        idx_name: str = req_arg.get("index")
        range_of: str = req_arg.get("range_of")
        start: str = req_arg.get("from")
        end: str = req_arg.get("upto")
        res = elk.search_records_from_index_by_time_range(es, idx_name, range_of, start, end)
    except Exception as ex:
        print(f"\nException in /search_all_by_time_range api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_field_range
@bp.route("/search_field_range", methods=["POST"])
def search_field_by_time_range():

    try:
        req_arg = request.get_json()
        idx_name: str = req_arg.get("index")
        range_of: str = req_arg.get("range_of")
        field: str = req_arg.get("field")
        start: str = req_arg.get("from")
        end: str = req_arg.get("upto")
        res = elk.search_field_from_index_by_time_range(es, idx_name, range_of, field, start, end)
    except Exception as ex:
        print(f"\nException in /search_field_range api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_keyword?index=tdp_idx&keyword=Developer
@bp.route("/search_keyword", methods=["POST"])
def search_by_keyword():

    try:
        idx_name: str = request.args.get("index")
        keyword: str = request.args.get("keyword")
        res = elk.search_all_occurances_of_keyword_in_index(es, idx_name, keyword)
    except Exception as ex:
        print(f"\nException in /search_keyword api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)


# http://127.0.0.1:5000/search_fulltext?index=tdp_idx&text=ger
@bp.route("/search_fulltext", methods=["POST"])
def search_by_full_text():

    try:
        idx_name: str = request.args.get("index")
        text: str = request.args.get("text")
        res = elk.search_all_occurances_of_text_in_index(es, idx_name, text)
    except Exception as ex:
        print(f"\nException in /search_fulltext api: {ex}\n")
        res = {"message": f"Caught Exception: {ex}", "status": 404}
    return jsonify(res)
