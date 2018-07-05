# Whois service

List user relations and notes from Active Directory. This is a testbed for running elastic search on a large (a couple of thousand) directory of users. 

Started out as a testbed for elasticsearch and more "modern" web development with queues, es, docker and nginx. Now it's perhaps just a very simple and static directory browser.

## Deploy

Easiest way is to deploy this on rancher. There is a sample catalog entry in the ./rancher directory. The rancher template will ask a whole bunch of questions, and after filling them out the services should be launched. 


## Populating data

At first when you start the service, there will be no data loaded. You will need to hit the endpoint to populate data:

```
curl -X POST http://whois.mycompany.com/api/v1/populate?dump=yes
```

You can stick this in a cronjob somewhere to run each night, or as often as you need it to. 

It's a little bit naive right now -- it deletes the entire database and then rebuild it from scratch. So for a little while, it will look like the database is broken or empty. For some 30k users, this takes a couple of minutes so it shouldn't be a big deal.

## Development

For development, the easiest way is to use the docker-compose.yml file provied. This will bring up a webserver on localhost:9000 that you can hit with your browser.

The backend python flask app will be booted up in a debug single threaded mode, with autoreload and mapped to the live version you have on your disk. 

The webpages will also be mapped to the live versions on your disk. 

You should be able to live load both pages and backend code.

You will need to set a couple of environment variables, e.g. 

```
export LDAP_SERVER=domaincontroller.mycompany.com
export LDAP_BASE_DN="dc=mycompany, dc=com"
export LDAP_USERNAME=serviceaccount@mycompany.com
export LDAP_PASSWORD=password
```

In order to boot this up locally you need to set the environment variable DEBUG=1. E.g. 

```
DEBUG=1 make up
```

In order to iterate, just type:

```
DEBUG=1 make
```

This will bring up the entire stack, and map the live source code for the frontend and the backend into the containers.


During development you might want to reset the data in elasticsearch, but not necessarily re-download the data from your active directory server. This can be done by hitting this URL:

```
curl -X POST http://localhost:9000/api/v1/populate?dump=no
```

## API

|Endpoint.        |Verb|Description|
|-----------------|----|-----------|
|/flat            |GET |List all the users in a text file suitable to consume with grep|
|/json            |GET |Return a raw json dump of the internal database|
|/api/v1/populate |POST|Trigger a rebuild of the database from AD. ?dump=yes required to actually pull from AD|
|/api/v1/health   |GET |Obtain some stats|
|/api/v1/search   |GET |Search for users|
|/api/v1/users    |GET |Dump users|
|/api/v1/user/<id>|GET |List individual user details|

## TODO

* Sort reports by years of service, descending
* Gravatar fallback support: https://en.gravatar.com/site/implement/images/
* Generate diffs and optionally send an email (or store in webform) so that we can track and notify when people leave
