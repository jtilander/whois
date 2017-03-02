from tasks.config import huey
from tasks.tasks import update_from_ldap
import os


def populate():
    username = os.environ['LDAP_USERNAME']
    password = os.environ['LDAP_PASSWORD']
    server = os.environ['LDAP_SERVER']
    schema = os.environ['LDAP_BASE_DN']

    update_from_ldap(server, username, password, schema)
