from flask import Flask
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
import requests
import config
import json
from pprint import pprint
from elasticsearch import Elasticsearch
import os
import sys

app = Flask("whoisapi")
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()

DEBUG = int(os.environ.get('DEBUG', '0'))
INDEX_NAME = 'users'
DOC_TYPE = 'user'

INDEX_MAPPING = '''{
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15
                }
            },
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter"
                    ]
                }
            }
        }
    },
    "mappings": {
        "users": {
            "properties": {
                "fullname": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "address": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "company": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "eid": {
                    "type": "string",
                    "index_analyzer": "not_analyzed",
                },
                "email": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "manager": {
                    "type": "string",
                    "index_analyzer": "not_analyzed",
                },
                "managername": {
                    "type": "string",
                    "index_analyzer": "not_analyzed",
                },
                "office": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "path": {
                    "type": "string",
                    "index_analyzer": "not_analyzed",
                },
                "reports": {
                    "type": "nested",
                    "index_analyzer": "not_analyzed",
                },
                "tags": {
                    "type": "nested",
                    "index_analyzer": "not_analyzed",
                },
                "notes": {
                    "type": "string",
                    "index_analyzer": "not_analyzed",
                },
                "title": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "username": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                },
                "description": {
                    "type": "string",
                    "index_analyzer": "autocomplete",
                    "search_analyzer": "standard"
                }
            }
        }
    }
}'''


class UserList(Resource):

    def get(self):
        url = config.es_base_url['users'] + '/_search'
        query = {
            "query": {
                "match_all": {}
            },
            "size": 100
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
        print("Call for: POST /users")
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
        print("Call for GET /search")
        parser.add_argument('q')
        query_string = parser.parse_args()
        url = config.es_base_url['users'] + '/_search'
        query = {
            "query": {
                "multi_match": {
                    "fields": ["username", "fullname", "title", "email", "company", "office", "address"],
                    "query": query_string['q'],
                    "type": "cross_fields",
                    "use_dis_max": False
                }
            },
            "size": 100
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        users = []
        # pprint(data)
        for hit in data['hits']['hits']:
            user = hit['_source']
            user['id'] = hit['_id']
            users.append(user)
        return users


class Reload(Resource):

    def post(self):
        records = json.load(open(config.user_json_filename))
        total_records = len(records)

        es = Elasticsearch("http://elasticsearch:9200")

        print >> sys.stderr, "Deleting index %s" % INDEX_NAME
        es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

        print >> sys.stderr, "Creating new mapping for index %s" % INDEX_NAME
        es.indices.create(index=INDEX_NAME, ignore=400, body=INDEX_MAPPING)

        print >> sys.stderr, "Uploading %d indices to elasticsearch..." % total_records
        for record in records:
            username = record['username']
            es.create(index=INDEX_NAME, doc_type=DOC_TYPE, body=record, id=username)

        print >> sys.stderr, "Done."
        return {"Records": total_records}


api.add_resource(User, config.api_base_url + '/users/<user_id>')
api.add_resource(UserList, config.api_base_url + '/users')
api.add_resource(Search, config.api_base_url + '/search')
api.add_resource(Reload, config.api_base_url + '/reload')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
