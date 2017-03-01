from flask import Flask
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
import requests
import config
import json
from pprint import pprint
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()


class UserList(Resource):

    def get(self):
        print("Call for: GET /users")
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
        print("Call for: GET /users/%s" % user_id)
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
                    "fields": ["username", "fullname", "description", "title", "email", "company", "office", "address"],
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
        for record in records:
            username = record['username']
            es.index(index="users", doc_type='user', body=record, id=username)
            print "Indexed user %s" % username

        return {"Records": total_records}


api.add_resource(User, config.api_base_url + '/users/<user_id>')
api.add_resource(UserList, config.api_base_url + '/users')
api.add_resource(Search, config.api_base_url + '/search')
api.add_resource(Reload, config.api_base_url + '/reload')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

