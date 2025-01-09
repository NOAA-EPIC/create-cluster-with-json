import os
import time
import sys
import requests
import json
import base64
import getopt

from client import Client

#--------------------------------------------------------------------------
def prepare_headers(apikey):
    encoded_bytes = base64.b64encode(apikey.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + encoded_string
    }
    return headers

#------------------------------------------------------------------
if __name__ == '__main__':
   #inputs
    print('PW_PLATFORM_HOST: ', os.environ.get('PW_PLATFORM_HOST'))
    if os.environ.get('PW_PLATFORM_HOST') is not None:
        pw_url = 'https://' + os.environ['PW_PLATFORM_HOST']
    else:
        pw_url = 'https://noaa.parallel.works'

    print('PW_API_KEY: ', os.environ.get('PW_API_KEY'))
    if os.environ.get('PW_API_KEY') is not None:
        apikey = os.environ['PW_API_KEY']
    else:
        print('PW_API_KEY is not set in environmental variablse. Exit.')
        sys.exit(-1)

    jsonfile = 'clusterDef.json'
    clustername = 'testfromapi1'
    displayname = 'WEI EPIC AWS c7i.48xlarge'
   #type must be one of ['pclusterv2', 'gclusterv2', 'azclusterv2']
    clustertype = 'pclusterv2'
    description = 'Wei pclusterv2 on AWS from EPIC using c7i.48xlarge'
    tags = 'computer on c7i.48xlarge, process on c7i.24xlarge'

    opts, args = getopt.getopt(sys.argv[1:], '', ['help=', 'jsonfile=', 'clustername=',
                                                  'displayname=', 'clustertype=',
                                                  'description=', 'tags='])
    for o, a in opts:
        if o in ['--help']:
            print('Usage: %s [--help] [--jsonfile=filename]')
            sys.exit(0)
        elif o in ['--jsonfile']:
            jsonfile = a
        elif o in ['--clustername']:
            clustername = a
        elif o in ['--displayname']:
            displayname = a
        elif o in ['--clustertype']:
            clustertype = a
        elif o in ['--description']:
            description = a
        elif o in ['--tags']:
            tags = a
        else:
            assert False, 'unhandled option'

#------------------------------------------------------------------
    header = prepare_headers(apikey)
    name = clustername
    type = clustertype
    c = Client(pw_url, header)

    cluster = c.create_v2_cluster(name, description, tags, type)
    cluster_id = cluster['_id']

    with open(jsonfile) as cluster_defintion:
        data = json.load(cluster_defintion)
        try:
            updated_cluster = c.update_v2_cluster(cluster_id, data)
            print(updated_cluster)
        except requests.exceptions.HTTPError as e:
            print(e.response.text)

'''
# This section will get and display the resource list.
# get_resources gets the full list of resources,
# and get_resource will get the named resource.
resources = c.get_resources()
print(json.dumps(resources, indent=4))
namedResource = c.get_resource("testfromapi1")
print(json.dumps(namedResource, indent=4))
'''


