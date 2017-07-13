#!/usr/bin/python
import os
import ldap
import logging
import json
import pickle
import sys

DEBUG = int(os.environ.get("DEBUG", "0"))
LDAP_SERVER = 'ldap://%s' % os.environ.get('LDAP_SERVER', 'no_server_selected')
LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', '')


def ldap_find_object(ldap_client, objectname):
    """
    Given a full object name, return the full object.
    """
    # The next lines will also need to be changed to support your search requirements and directory
    baseDN = objectname
    searchScope = ldap.SCOPE_BASE
    # retrieve all attributes - again adjust to your needs - see documentation for more options
    retrieveAttributes = None
    searchFilter = '(objectClass=*)'
    logging.debug('Searching for object %s' % objectname)
    try:
        ldap_result_id = ldap_client.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = ldap_client.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                # here you don't have to append to a list
                # you could do whatever you want with the individual entry
                # The appending to list is just for illustration.
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
        return result_set
    except ldap.LDAPError, e:
        logging.exception(e)
        raise


def ldap_find_user(ldap_client, username):
    """
    Given a short username (i.e. the login name), you can search the entire domain and find
    the object in AD.
    """
    return ldap_search(ldap_client, ['objectClass=person', 'sAMAccountName=%s' % username])


def ldap_find_useremail(ldap_client, email):
    """
    Given a the email, you can search the entire domain and find
    the object in AD.
    """
    return ldap_search(ldap_client, ['objectClass=person', 'mail=%s' % email.lower()])


def ldap_search(ldap_client, query):
    """

    query is an array of search strings, e.g.

    ['objectClass=person', 'sAMAccountName=jtilander']

    """
    # The next lines will also need to be changed to support your search requirements and directory
    baseDN = LDAP_BASE_DN
    searchScope = ldap.SCOPE_SUBTREE
    # retrieve all attributes - again adjust to your needs - see documentation for more options
    retrieveAttributes = None
    searchFilter = '(&%s)' % "".join(['(%s)' % x for x in query])
    logging.debug('Executing search %s' % searchFilter)
    try:
        ldap_result_id = ldap_client.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = ldap_client.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                # here you don't have to append to a list
                # you could do whatever you want with the individual entry
                # The appending to list is just for illustration.
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
        return result_set
    except ldap.LDAPError, e:
        logging.exception(e)
        raise


def ldap_list_users(username, password):
    # http://mattfahrner.com/2014/03/09/using-paged-controls-with-python-and-ldap/
    base = LDAP_BASE_DN
    search_flt = '(objectClass=person)'
    # search_flt = '(&(objectClass=person)(sAMAccountName=%s))' % 'gevans'

    # searchreq_attrlist = ['cn','entryDN','entryUUID','mail','objectClass']
    searchreq_attrlist = None

    from ldap.ldapobject import LDAPObject
    from ldap.controls import SimplePagedResultsControl

    class PagedResultsSearchObject:
        page_size = 50

        def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0, serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0):
            """
            Behaves exactly like LDAPObject.search_ext_s() but internally uses the
            simple paged results control to retrieve search results in chunks.

            This is non-sense for really large results sets which you would like
            to process one-by-one
            """
            req_ctrl = SimplePagedResultsControl(True, size=self.page_size, cookie='')

            # Send first search request
            msgid = self.search_ext(
                base,
                ldap.SCOPE_SUBTREE,
                search_flt,
                attrlist=searchreq_attrlist,
                serverctrls=(serverctrls or []) + [req_ctrl]
            )

            result_pages = 0
            all_results = []

            while True:
                rtype, rdata, rmsgid, rctrls = self.result3(msgid)
                all_results.extend(rdata)
                result_pages += 1
                # Extract the simple paged results response control
                pctrls = [
                    c
                    for c in rctrls
                    if c.controlType == SimplePagedResultsControl.controlType
                ]
                if pctrls:
                    if pctrls[0].cookie:
                        # Copy cookie from response control to request control
                        req_ctrl.cookie = pctrls[0].cookie
                        msgid = self.search_ext(
                            base,
                            ldap.SCOPE_SUBTREE,
                            search_flt,
                            attrlist=searchreq_attrlist,
                            serverctrls=(serverctrls or []) + [req_ctrl]
                        )
                    else:
                        break
            return result_pages, all_results

    class MyLDAPObject(LDAPObject, PagedResultsSearchObject):
        pass

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    level = 0
    if DEBUG:
        ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)
        level = 10
    ldap.set_option(ldap.OPT_REFERRALS, 0)
    client = MyLDAPObject(LDAP_SERVER, trace_level=level)
    client.protocol_version = 3
    client.simple_bind_s(username, password)
    client.page_size = 10

    # Send search request
    result_pages, all_results = client.paged_search_ext_s(
        base,
        ldap.SCOPE_SUBTREE,
        search_flt,
        attrlist=searchreq_attrlist,
        serverctrls=None
    )

    client.unbind_s()

    # print '# Received %d results in %d pages.' % (len(all_results),result_pages)

    # Filter out results that doesn't seem to be relevant
    results = []
    for candidate in all_results:
        # fqn = candidate[0]
        attributes = candidate[1]
        if "sAMAccountName" not in attributes:
            continue
        if "mail" not in attributes:
            continue
        results.append(candidate)

    return results


def ldap_login(username, password):
    """
    Verifies credentials for username and password.
    Returns a tuple with true/false for the first member and the reason as the second.
    """
    # fully qualified AD user name
    LDAP_USERNAME = '%s' % username
    # your password
    LDAP_PASSWORD = password

    print "Logging in with '%s' / '%s' " % (LDAP_USERNAME, LDAP_PASSWORD)
    try:
        # build a client
        ldap_client = ldap.initialize(LDAP_SERVER)
        # perform a synchronous bind
        if DEBUG:
            ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        return False, 'Wrong username ili password', None
    except ldap.SERVER_DOWN:
        return False, 'AD server not awailable', None
    return True, 'Successfully authenticated', ldap_client


def main():
    username = os.environ.get('LDAP_USERNAME')
    password = os.environ.get('LDAP_PASSWORD')

    print "Connecting to %s as %s and dumping all the users matching '%s'..." % (LDAP_SERVER, username, LDAP_BASE_DN)
    users = ldap_list_users(username, password)
    # pprint(users)

    print "Found %d user records." % len(users)

    print "Saving python pickle to /data/users.pkl"
    pickle.dump(users, open('/data/users.pkl', 'w'))

    # print "Saving json dump to /data/users.json"
    # users = users.decode('utf-8').strip()

    # jsonstring = json.dumps(users, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    # open("/data/users.json", "wt").write(jsonstring)
    return 0


if __name__ == '__main__':
    sys.exit(main())
