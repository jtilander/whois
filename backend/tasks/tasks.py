from config import huey
import sys
import filelock
import os
import json
from elasticsearch import Elasticsearch

USER_JSON_FILENAME = '/data/users.json'
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


@huey.task()
def update_from_ldap(server, username, password, schema):
    pid = os.getpid()

    print >> sys.stderr, '[%5d] Aquire lock...' % pid

    lock = filelock.FileLock("/tmp/ldap_update.lock")

    try:
        with lock.acquire(timeout=10):
            print >> sys.stderr, '[%5d] Got lock, now running ldap update...' % pid
            print >> sys.stderr, '[%5d] Server: %s, Username: %s, Schema: %s' % (pid, server, username, schema)

            os.environ['LDAP_USERNAME'] = username
            os.environ['LDAP_PASSWORD'] = password
            os.environ['LDAP_SERVER'] = server
            os.environ['LDAP_BASE_DN'] = schema

            command = '/usr/bin/python /app/scripts/ldapdump.py'

            print >> sys.stderr, '[%5d] Execute: %s' % (pid, command)

            os.system(command)

            os.environ['LDAP_USERNAME'] = ''
            os.environ['LDAP_PASSWORD'] = ''
            os.environ['LDAP_SERVER'] = ''
            os.environ['LDAP_BASE_DN'] = ''

            command = '/usr/bin/python /app/scripts/ldapmunge.py'
            print >> sys.stderr, '[%5d] Execute: %s' % (pid, command)
            os.system(command)

            records = json.load(open(USER_JSON_FILENAME))
            total_records = len(records)

            es = Elasticsearch("http://elasticsearch:9200")

            print >> sys.stderr, "[%5d] Deleting index %s" % (pid, INDEX_NAME)
            es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

            print >> sys.stderr, "[%5d] Creating new mapping for index %s" % (pid, INDEX_NAME)
            es.indices.create(index=INDEX_NAME, ignore=400, body=INDEX_MAPPING)

            print >> sys.stderr, "[%5d] Uploading %d indices to elasticsearch..." % (pid, total_records)
            for record in records:
                username = record['username']
                es.create(index=INDEX_NAME, doc_type=DOC_TYPE, body=record, id=username)

            print >> sys.stderr, '[%5d] Done.' % pid
    except filelock.Timeout:
        print >> sys.stderr, '[%5d] Failed to aquire lock, skipping task.' % pid

    return None
