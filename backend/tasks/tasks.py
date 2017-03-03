from config import huey
import sys
import filelock
import os
import json
from elasticsearch import Elasticsearch

USER_JSON_FILENAME = '/data/users.json'
INDEX_NAME = 'users'
DOC_TYPE = 'user'


@huey.task()
def update_from_ldap(server, username, password, schema, pull):
    pid = os.getpid()

    print >> sys.stderr, '[%5d] Aquire lock...' % pid

    lock = filelock.FileLock("/tmp/ldap_update.lock")

    try:
        with lock.acquire(timeout=10):
            print >> sys.stderr, '[%5d] Got lock, now running ldap update...' % pid
            print >> sys.stderr, '[%5d] Server: %s, Username: %s, Schema: %s' % (pid, server, username, schema)

            if pull:
                os.environ['LDAP_USERNAME'] = username
                os.environ['LDAP_PASSWORD'] = password
                os.environ['LDAP_SERVER'] = server
                os.environ['LDAP_BASE_DN'] = schema

                command = '/usr/bin/python /app/scripts/ldapdump.py'

                print >> sys.stderr, '[%5d] Execute: %s' % (pid, command)

                ret = os.system(command)

                os.environ['LDAP_USERNAME'] = ''
                os.environ['LDAP_PASSWORD'] = ''
                os.environ['LDAP_SERVER'] = ''
                os.environ['LDAP_BASE_DN'] = ''

                if ret != 0:
                    print >> sys.stderr, '[%5d] Dump failed, aborting' % (pid)
                    return None

            command = '/usr/bin/python /app/scripts/ldapmunge.py'
            print >> sys.stderr, '[%5d] Execute: %s' % (pid, command)
            if 0 != os.system(command):
                print >> sys.stderr, '[%5d] Munge failed, aborting' % (pid)
                return None

            records = json.load(open(USER_JSON_FILENAME))
            total_records = len(records)

            es = Elasticsearch("http://elasticsearch:9200")

            print >> sys.stderr, "[%5d] Deleting index %s" % (pid, INDEX_NAME)
            es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

            print >> sys.stderr, "[%5d] Creating new mapping for index %s" % (pid, INDEX_NAME)
            # es.indices.create(index=INDEX_NAME, ignore=400, body=INDEX_MAPPING)
            command = '''curl -Ss -XPUT 'http://elasticsearch:9200/users' -H 'Content-Type: application/json' -d "@/app/scripts/index.json"'''
            if 0 != os.system(command):
                print >> sys.stderr, '[%5d] Upload of index failed, aborting' % (pid)
                return None

            print >> sys.stderr, "[%5d] Uploading %d indices to elasticsearch..." % (pid, total_records)
            for record in records:
                username = record['username']
                es.create(index=INDEX_NAME, doc_type=DOC_TYPE, body=record, id=username)

            print >> sys.stderr, '[%5d] Done.' % pid
    except filelock.Timeout:
        print >> sys.stderr, '[%5d] Failed to aquire lock, skipping task.' % pid

    return None
