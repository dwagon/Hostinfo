#!/usr/bin/env python

"""
Small python script to integrate hostinfo with rundeck
"""
import requests
import logging
import os
import sys
import yaml

from time import sleep

# TODO: Setup argparse 
# TODO: Write host files out sepretately
# TODO: multithread host hostinfo calls

URL = "http://hostinfo/api"

#--------------------------------------------------------
def get_hosts(logger):
    hosts = []

    endpoint = URL + '/host/'
    host_list = requests.get(endpoint)

    if host_list.status_code != 200:
        logger.error("Unable to contact %s, received %d", endpoint, host_list.status_code)
        sys.exit(1)

    for host in host_list.json()['hosts']:
        hosts.append(host.get('hostname'))

    return hosts

#--------------------------------------------------------
def retry(func):
    '''
    Make my API call reliable if hostinfo doe snot respond
    in 3 attempts
    '''
    def retried_func(*args, **kwargs):
        MAX_TRIES = 3
        tries = 0
        while True:
            resp = func(*args, **kwargs)
            if resp.status_code != 200 and tries < MAX_TRIES:
                tries += 1
                sleep(10)
                continue
            break
        return resp
    return retried_func

#--------------------------------------------------------
def get_host_details(logger, hosts):
    hosts_details = {}

    r = retry(lambda endpoint: requests.get(endpoint))

    for host in hosts:
        endpoint = URL + '/host/' + host

        results = r(endpoint)
        hosts_details[host] = results.json()['host']['keyvalues']

    return hosts_details

#--------------------------------------------------------
def sanitise_hosts_data(logger, details):
    print details
    exit()
    
#--------------------------------------------------------
def main():
    SSH_USER = ""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    hosts = get_hosts(logger)

    details = get_host_details(logger, hosts)

    resources = {}

    for host in details:
        resource_details = {}
        for detail in details[host]:
            data = [x.get('value') for x in details[host][detail]]

            # If only one entry in list, it is a key:value pair
            # pop it out
            if len(data) is 1:
                data = data.pop()

            resource_details[detail] = data

        # Set the mandatory RunDeck values
        resource_details['username'] = SSH_USER
        resource_details['hostname'] = host

        resources[host] = resource_details

        #resources[host] = sanitise_hosts_data(logger, host)

    with open('data.yml', 'w') as outfile:
        outfile.write( yaml.safe_dump(resources, encoding='utf-8', allow_unicode=True, default_flow_style=False))

#--------------------------------------------------------
if __name__ == "__main__":
    main()
