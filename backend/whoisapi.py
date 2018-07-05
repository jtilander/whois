from flask import Flask, send_file, abort
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
import requests
import config
import json
import os
import sys
import ops
import datetime
import logging

app = Flask("whoisapi")
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()

DEBUG = int(os.environ.get('DEBUG', '0'))
MAX_RESULTS = int(os.environ.get('MAX_RESULTS', '100'))
DEFAULT_CACHE_TIMEOUT = int(os.environ.get('DEFAULT_CACHE_TIMEOUT', '3600'))


class UserList(Resource):

    def get(self):
        url = config.es_base_url['users'] + '/_search'
        query = {
            "query": {
                "match_all": {}
            },
            "size": MAX_RESULTS
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        users = []
        for hit in data['hits']['hits']:
            user = hit['_source']
            user['id'] = hit['_id']
            users.append(user)
        return users

    def post(self):
        return None


class User(Resource):

    def get(self, user_id):
        url = config.es_base_url['users'] + '/user/' + user_id
        resp = requests.get(url)
        data = resp.json()
        user = data['_source']
        return user

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class Search(Resource):

    def get(self):
        if DEBUG:
            print >> sys.stderr, "Call for GET /search with max results %d" % MAX_RESULTS
        parser.add_argument('q')
        query_string = parser.parse_args()
        url = config.es_base_url['users'] + '/_search'
        query = {
            "query": {
                "multi_match": {
                    "fields": ["username", "fullname", "title", "email", "company", "office", "address", "description"],
                    "query": query_string['q'],
                    "type": "cross_fields",
                    "use_dis_max": False
                }
            },
            "size": MAX_RESULTS
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        users = []
        for hit in data['hits']['hits']:
            user = hit['_source']
            user['id'] = hit['_id']
            users.append(user)
        return users


class Populate(Resource):

    def post(self):
        parser.add_argument('dump')
        query_string = parser.parse_args()

        dump = False
        dumpstr = query_string.get('dump', 'no')
        if dumpstr is None:
            dump = False
        elif dumpstr.lower() == 'yes':
            dump = True
        elif dumpstr == '1':
            dump = True

        print >> sys.stderr, "Populating index (Pull raw LDAP data: %s)" % dump
        ops.populate(dump)

        return {"result": "enqueued"}


class Health(Resource):

    def get(self):
        url = config.es_base_url['users'] + '/user/_count'
        resp = requests.post(url)
        data = resp.json()

        result = dict()
        result['users'] = data['count']

        result['controller'] = os.environ.get('LDAP_SERVER', '')
        result['domain'] = os.environ.get('LDAP_BASE_DN', '')

        updated = ''
        if os.path.isfile('/data/users.pkl'):
            updated = datetime.datetime.fromtimestamp(os.path.getmtime('/data/users.pkl')).strftime('%Y-%m-%d %H:%M')
        result['refreshed'] = updated

        return result


@app.route(config.api_base_url + "/flat")
def getflatfile():
    try:
        return send_file("/data/users.flat", mimetype="text/plain", cache_timeout=DEFAULT_CACHE_TIMEOUT)
    except Exception as e:
        logging.exception("Failed to serve flat file: %s" % str(e))
        abort(500)


@app.route(config.api_base_url + "/json")
def getjsonfile():
    try:
        return send_file("/data/users.json", mimetype="application/json", cache_timeout=DEFAULT_CACHE_TIMEOUT)
    except Exception as e:
        logging.exception("Failed to serve json file: %s" % str(e))
        abort(500)


api.add_resource(User, config.api_base_url + '/users/<user_id>')
api.add_resource(UserList, config.api_base_url + '/users')
api.add_resource(Search, config.api_base_url + '/search')
api.add_resource(Populate, config.api_base_url + '/populate')
api.add_resource(Health, config.api_base_url + '/health')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
