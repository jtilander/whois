# Whois service

List user relations and notes from Active Directory. This is a testbed for running elastic search on a large (a couple of thousand) directory of users. 

Please note that this is just a toy tesdbed for me to tinker with ES.

## Usage

Please POST to /api/v1/populate to initiate a pull from Active Directory and parse it into the internal database. 

This will effectivly do the following:

```
set -e

DOCKER_LDAPDUMP=jtilander/ldapdump
DOCKER_LDAPMUNGE=jtilander/ldapmunge
TARGET_DATA_DIR=/mnt/ldap
LDAP_SERVER=mydc.company.com
LDAP_BASE_DN="dc=company, dc=com"

TMPDIR=/tmp/$BUILD_TAG

if [ ! -d $TMPDIR ]; then
    mkdir $TMPDIR
fi

# Connect to AD and dump out users.pkl
docker run --rm -v $TMPDIR/dump:/data -e "LDAP_USERNAME=${LDAP_USERNAME}" -e "LDAP_PASSWORD=${LDAP_PASSWORD}" -e "LDAP_SERVER=${LDAP_SERVER}" -e "LDAP_BASE_DN=${LDAP_BASE_DN}" ${DOCKER_LDAPDUMP}

# Transform users.pkl into users.json and a bunch of user images
docker run --rm -v $TMPDIR/dump:/input -v $TARGET_DATA_DIR:/data $DOCKER_LDAPMUNGE

# This is where the pickle structure was stored, we don't need it anymore.
rm -rf $TMPDIR

# Now that we've stored the new data in the right place, let's kick the server to reload all of our data.
curl -Ss -X POST https://users.mycompany.com/api/v1/reload
```


Now, the backend service need to be configured with the correct environment for the LDAP_* environment variables for this to work. Please refer to the docker-compose.yml file.


## Development

For development, the easiest way is to use the docker-compose.yml file provied. This will bring up a webserver on localhost:9000 that you can hit with your browser.

The backend python flask app will be booted up in a debug single threaded mode, with autoreload and mapped to the live version you have on your disk. 

The webpages will also be mapped to the live versions on your disk. 

You should be able to live load both pages and backend code.

