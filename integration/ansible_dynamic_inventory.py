#!/usr/bin/env python

import argparse
import json
from threading import Thread
import yaml
import re
import requests

#------------------------------------------------------------------------------
def read_config():
    try:
        with open('config.yml', 'r') as yaml_f:
            config = yaml.load(yaml_f)
    except IOError:
        pass

    hostinfo_url = 'http://hostinfo/api/'
    if 'general' in config.keys():
        if 'hostinfo_url' in config['general']:
            hostinfo_url = config['general']['hostinfo_url']

            if not hostinfo_url.endswith('/'):
                hostinfo_url += '/'

    hostinfo_maps = {}
    if 'grouping' in config.keys():
        for group in config['grouping']:
            query_string = config['grouping'][group]
            elements = re.split('\s|[,.]\s', query_string)

            hostinfo_maps[group] = elements

    return hostinfo_url, hostinfo_maps


#------------------------------------------------------------------------------
class Hostinfo(Thread):
    def __init__(self, url, query):
        Thread.__init__(self)
        self.url = url
        self.query = query

    def run(self):
        self.hosts = self.get_hosts(self.url, self.query)

    def get_hosts(self, hostinfo_url, hostinfo_query):
        hosts = []
        hostinfo_query.append('lastping=today')
        hostinfo_query = [re.sub('=', '.eq.', algo) for algo in hostinfo_query]

        endpoint = hostinfo_url + 'query/'
        endpoint += '/'.join(hostinfo_query)
        host_list = requests.get(endpoint)

        if host_list.status_code != 200:
            print "Unable to contact %s, received %d" % (endpoint, host_list.status_code)
            exit(1)

        for host in host_list.json()['hosts']:
            hosts.append(host.get('hostname'))

        return hosts

#------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produce an Hostinfo Inventory file')
    parser.add_argument('--list', action='store_true', default=True,
                        help='List instances (default: True)')
    parser.add_argument('--host', action='store',
                        help='Get variables about a specific instance')
    args = parser.parse_args()

    threads = []
    url, maps = read_config()

    if args.list:
        group_maps = {}

        for group in maps:
            current = Hostinfo(url, maps[group])
            threads.append(current)
            current.start()

        for thread in threads:
            thread.join()
            group_maps[group] = thread.hosts

        print json.dumps(group_maps)
