# -*- coding: utf-8 -*-

import datetime

import prometheus_client
from flask import Flask, request, Response
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime

from helpers.middleware import setup_metrics
from utils.auth import authorization
from utils.config import SQLALCHEMY_DATABASE_URI
from utils.log import log

app = Flask(__name__)
setup_metrics(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# api = Blueprint('api', 'api', url_prefix='/api/v1')
# app.register_blueprint(api)

# db/table creation
db = SQLAlchemy(app)


class keys(db.Model):
    """
    key-value model
    """
    key = db.Column('key', db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(100))
    created_at = db.Column(DateTime, default=datetime.datetime.now)
    expire_in = db.Column(db.Integer)

    def __init__(self, value, expire_in):
        self.value = value
        self.expire_in = expire_in


# api route endpoint
@app.route('/keys')
@app.route('/keys/<id>')
@authorization
def getKeys(id=None):
    """
    GET operations API endpoint
        1. get a value (GET /keys/{id})
        2. get all keys and values (GET /keys)
        3. support wildcard keys when getting all values (GET /keys?filter=wo$d)

    :param id: keyId
    :parameter: filter: wildcard filter on values
    :return: value
    """
    try:
        log.info("GET request")
        filter = request.args.get("filter", None)
        id = id

        resp = get_query_result(id, filter)

        log.info("Found keys : {}".format(resp))

        if len(resp):
            return jsonify(resp), 200
        else:
            return jsonify("Not found"), 404

    except Exception as e:
        log.error("backend processing error {}".format(e))
        return jsonify({
            "Status": "Failed",
            "message": "Internal server error"
        }), 500


@app.route('/keys', methods=['PUT'])
@authorization
def putKeys():
    """
    PUT operations API endpoint
        1. set a value (PUT /keys)
           raw data "value"
        2. set an expiry time when adding a value (PUT /keys?expire_in=60)
    :return: added keys
    """
    try:
        log.info("PUT request")
        value = request.data
        expire_in = request.args.get("expire_in", 60)
        log.info("value recieved : {}, expire_in: {}".format(value, expire_in))

        kobj = keys(value.decode(), expire_in)
        db.session.add(kobj)
        db.session.commit()
        return jsonify("record added")

    except Exception as e:
        log.error("failed to put operation : {}".format(e))
        return jsonify({
            "Status": "Failed",
            "message": "Internal server error"
        }), 500


@app.route('/keys', methods=['DELETE'])
@app.route('/keys/<id>', methods=['DELETE'])
@authorization
def deleteKeys(id=None):
    """
    PUT operations API endpoint
        1. delete a value (DELETE /keys/{id})
        2. delete all values (DELETE /keys)
    :return:  number of rows deleted
    """
    try:
        log.info("DELETE request")
        log.info("key recieved : {}".format(id))

        def delete(id):
            try:
                if id:
                    res = db.session.query(keys).filter(keys.key == id).delete()  # single id
                else:
                    res = db.session.query(keys).delete()  # all row

                db.session.commit()
                return res
            except Exception as e:
                log.error("delete operation failed with {}".format(e))
                db.session.rollback()

        res = delete(id)

        return jsonify({
            "row_affected": res
        })

    except Exception as e:
        log.error("failed to put operation : {}".format(e))
        return jsonify({
            "Status": "Failed",
            "message": "Internal server error"
        }), 500


def get_query_result(id, filter):
    if not id and not filter:
        log.info("select * from keys")
        query_res_obj = keys.query.all()

    if id and not filter:
        log.info("select * from keys where kyes.key == {}".format(id))
        query_res_obj = keys.query.filter(keys.key == id).all()

    if filter and not id:
        log.info("select * from keys where kyes.key like {}".format(filter))
        query_res_obj = keys.query.filter(keys.value.like(filter))

    resp = [{row.key: {'value': row.value, 'expire_in': row.expire_in, 'created_at': row.created_at}} for row in
            query_res_obj]
    return resp


# prometheous integration /metrics endpoint

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')


@app.route('/metrics')
def metrics():
    log.info("Inside prometheus metrics endpoint")
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)
