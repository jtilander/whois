#!/usr/bin/python
import os
import logging
import json
import sys
import pickle
from pprint import pprint
import time
import datetime

DEBUG = int(os.environ.get("DEBUG", "0"))
PICKLENAME = '/data/users.pkl'
FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
PHOTO_DIR = '/data/photos'
TARGETFILE = '/data/users.json'


def sanitize_phone(candidate):
    return candidate.strip().replace(' ', '').replace('-', '')

def str_to_utc(datestring):
    if len(datestring.strip()) == 0:
        return 0
    try:
        datestring = datestring.split()[0].strip()
        dt = datetime.datetime.strptime(datestring, "%Y%m%d%H%M%S.0Z")
        utc = time.mktime(dt.timetuple())
        return utc
    except:
        return 0

def transform_users(ldap_results):
    users = []
    for candidate in ldap_results:
        new = {}
        attributes = candidate[1]
        new['email'] = attributes.get('mail', [''])[0].lower()
        new['username'] = attributes.get('sAMAccountName', [''])[0].lower()
        new['fullname'] = " ".join(reversed([x.strip() for x in attributes.get('displayName', [''])[0].split(', ')]))
        new['path'] = attributes.get('distinguishedName', [''])[0]
        new['title'] = attributes.get('title', [''])[0]
        new['company'] = attributes.get('company', [''])[0]
        new['photo'] = attributes.get('thumbnailPhoto', [''])[0]
        new['manager'] = attributes.get('manager', [''])[0]
        new['managername'] = ''
        new['reports'] = attributes.get('directReports', [''])
        new['description'] = attributes.get('description', [''])[0]
        new['address'] = "%s, %s %s, %s" % (
            attributes.get('streetAddress', [''])[0],
            attributes.get('l', [''])[0],
            attributes.get('postalCode', [''])[0],
            attributes.get('c', [''])[0])
        new['phone'] = sanitize_phone(attributes.get('telephoneNumber', [''])[0])
        new['eid'] = attributes.get('employeeNumber', [''])[0]
        new['office'] = attributes.get('physicalDeliveryOfficeName', [''])[0]
        new['notes'] = ''
        new['tags'] = ['']

        timestr = attributes.get('whenCreated', [''])[0]
        new['hiredate'] = str_to_utc(timestr)

        users.append(new)

    users.sort(key=lambda x: x['fullname'])
    return users


def save_and_update_photos(output_dir, records):
    """
    Iterates over a list of records and saves the images in a flat
    directory in output_dir
    """
    logging.info("Saving photos of users...")
    count = 0
    for record in records:
        photo = record['photo']
        name = record['username']
        del record['photo']
        if len(photo) == 0:
            continue
        count = count + 1
        logging.debug('Found a photo for %s' % name)

        filename = os.path.join(output_dir, name + '.jpg')
        open(filename, 'w').write(photo)
    logging.info("Saved %d photos" % count)


def transform_paths(records):
    """
    Translate all the LDAP paths to just be usernames
    """
    default_manager = 'CN=Manager\\, Default,OU=TIBCO,OU=Apps,DC=activision,DC=com'
    lookup = dict()
    lookup[''] = ''
    id2name = dict()
    id2name[''] = ''
    for record in records:
        path = record['path']
        username = record['username']
        lookup[path] = username
        fullname = record['fullname']
        id2name[username] = fullname

    for record in records:
        try:
            record['manager'] = lookup[record['manager']]
        except KeyError:
            if record['manager'] != default_manager:
                logging.warning('Could not find manager: %s. Manager entry set to empty.' % record['manager'])
            record['manager'] = ''

        try:
            record['managername'] = id2name[record['manager']]
        except KeyError:
            logging.warning('Failed to lookup manager id %s for user %s' % (record['manager'], record['username']))
            record['managername'] = ''

        translated = []
        for x in record['reports']:
            try:
                translated.append(lookup[x])
            except KeyError:
                logging.warning('Could not find employee: %s. Skipping as a report for %s' % (x, record['username']))
        record['reports'] = [x for x in translated if len(x.strip()) > 0]


def debug():
    """
    Debugging function with random stuff
    """
    logging.info("Loading pickle stream from %s!" % PICKLENAME)
    data = pickle.load(open(PICKLENAME + '.small'))
    logging.info("Loaded %d items" % len(data))
    attributes = data[32][1]

    pprint(attributes)

    photo = attributes.get('thumbnailPhoto', [''])[0]

    print "Now trying to decode this: "
    pprint(photo)
    open('/data/image.jpg', 'w').write(photo)


def main():
    if DEBUG:
        debug()
        return 0

    logging.info("Loading pickle stream from %s" % PICKLENAME)
    data = pickle.load(open(PICKLENAME))
    logging.info("Loaded %d items" % len(data))

    users = transform_users(data)

    if not os.path.isdir(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
    save_and_update_photos(PHOTO_DIR, users)
    transform_paths(users)

    jsondata = json.dumps(users, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    logging.info('Saving json data to %s' % TARGETFILE)
    open(TARGETFILE, 'w').write(jsondata)

    return 0


if __name__ == '__main__':
    if DEBUG:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    else:
        logging.basicConfig(format=FORMAT, level=logging.INFO)

    sys.exit(main())
