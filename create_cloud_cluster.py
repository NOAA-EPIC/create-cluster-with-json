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

#--------------------------------------------------------------------------
def updateJSON(json_in, json_out, request):
    needed_json_vars = ['username', 'project', 'clustertype', 'management_shape',
        'compute_instance_type', 'process_instance_type', 'zone', 'region', 'csp_platform']

    request_keys = request.keys()

    for var in needed_json_vars:
        if (var not in request_keys):
            print('needed JSON var: %s is not in the requested dictionary. Exit.' %(var))
            sys.exit(-1)

    csp_platform = request['csp_platform']
   #Read the JSON file
    with open(json_in, 'r') as f:
        data = json.load(f)

   #Update the data
   #print('data: ', data)
   #print('\n\n')
   #print('data[resourceData]: ', data['resourceData'])
   #print('\n\n')
   #print('data[resourceData][partition_config]: ', data['resourceData']['partition_config'])
   #print('\n\n')
   #print('data[resourceData][partition_config][0]: ', data['resourceData']['partition_config'][0])
   #print('\n\n')
   #print('data[resourceData][partition_config][1]: ', data['resourceData']['partition_config'][1])
   #print('\n\n')
   #print('data[universalData]: ', data['universalData'])

    data['type'] = request['clustertype']
    data['username'] = request['username']
    data['universalData']['project'] = request['project']
    data['resourceData']['region'] = request['region']
    data['resourceData']['management_shape'] = request['management_shape']

    data['resourceData']['partition_config'][0]['instance_type'] = request['compute_instance_type']
    data['resourceData']['partition_config'][1]['instance_type'] = request['process_instance_type']
    data['resourceData']['partition_config'][0]['availability_zone'] = request['zone']
    data['resourceData']['partition_config'][1]['availability_zone'] = request['zone']

    if (csp_platform == 'AWS'):
        data['resourceData']['availability_zone'] = request['zone']
        data['resourceData']['partition_config'][0]['availability_zone'] = request['zone']
        data['resourceData']['partition_config'][1]['availability_zone'] = request['zone']
    elif (csp_platform == 'AWS'):
        data['resourceData']['zones'] = request['zone']
        data['resourceData']['partition_config'][0]['zones'] = request['zone']
        data['resourceData']['partition_config'][1]['zones'] = request['zone']
    elif (csp_platform == 'GCP'):
        data['resourceData']['zone'] = request['zone']
        data['resourceData']['partition_config'][0]['zone'] = request['zone']
        data['resourceData']['partition_config'][1]['zone'] = request['zone']

   #Write the updated data back to the file
    with open(json_out, 'w') as f:
        json.dump(data, f, indent=2)
       #json.dump(data, f, indent=4)

#--------------------------------------------------------------------------
def print_usage():
    print('Usage: %s [--help] --username=YOUR-USERNAME --project=YOUR-PROJECT [options]')
    print('options are (here default for AWS):')
    print('--clustername=myawscluster (must be all lowcases, without special characters)')
    print('--displayname=The-name-to-display')
    print('--description=string-describing-this-cluster')
    print('--management_shape=[c7i.2xlarge]')
   #print('--compute_instance_type=[c7i.48xlarge]')
    print('--compute_instance_type=[c7i.24xlarge]')
    print('--process_instance_type=[c7i.12xlarge]')

#------------------------------------------------------------------
if __name__ == '__main__':
   #username=Firstname.Lastname
   #project="ca-sfs-emc"
   #project="ca-epic"
    username=None
    project=None
    tags=None
    clustername=None
    displayname=None
    description=None
    management_shape=None
    compute_instance_type=None
    process_instance_type=None

    zone=None
    region=None

    opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'username=',
                                                  'project=', 'management_shape=', 'tags=',
                                                  'zone=', 'region=',
                                                  'compute_instance_type=', 'process_instance_type=',
                                                  'clustername=', 'displayname=', 'description='])
    for o, a in opts:
        if o in ['--help']:
            print_usage()
            sys.exit(0)
        elif o in ['--username']:
            username = a
        elif o in ['--project']:
            project = a
        elif o in ['--tags']:
            tags = a
        elif o in ['--zone']:
            zone = a
        elif o in ['--region']:
            region = a
        elif o in ['--management_shape']:
            management_shape = a
        elif o in ['--compute_instance_type']:
            compute_instance_type = a
        elif o in ['--process_instance_type']:
            process_instance_type = a
        elif o in ['--clustername']:
            clustername = a
        elif o in ['--displayname']:
            displayname = a
        elif o in ['--description']:
            description = a
        else:
            assert False, 'unhandled option'

    print('username = ', username)
    print('project = ', project)

    if (username == None or project == None):
        print('User must provide valid username AND project')
        print_usage()
        sys.exit(-1)

#------------------------------------------------------------------
    api_pki_file = 'pw_api.key'

    if os.path.exists(api_pki_file):
        with open(api_pki_file, "r") as file:
            for line in file.readlines():
                if (line.find('export PW_') >= 0):
                    headstr, _, value = line.strip().partition('=')
                    exphead, _, key = headstr.partition(' ')
                    print('key: <%s>, value: <%s>' %(key, value))
                    os.environ[key] = value
    else:
        print(f"File '{api_pki_file}' does not exist.")
        print("User must have a pw_api.key file with its ParallelWorks API_PKI key.")
        print("Check file: pw_api.key.sample to see what it looks like, and how to get it.")
        sys.exit(-1)

    if os.environ.get('PW_PLATFORM_HOST') is not None:
        pw_url = 'https://' + os.environ['PW_PLATFORM_HOST']
       #print('PW_PLATFORM_HOST: ', os.environ.get('PW_PLATFORM_HOST'))
    else:
        pw_url = 'https://noaa.parallel.works'

    if os.environ.get('PW_API_KEY') is not None:
        apikey = os.environ['PW_API_KEY']
       #print('PW_API_KEY: ', os.environ.get('PW_API_KEY'))
    else:
        print('PW_API_KEY is not set in environmental variablse. Exit.')
        sys.exit(-1)

#------------------------------------------------------------------
    item = username.split('.')
    firstname = item[0]
    lastname = item[1]

    item = project.split('-')
    platform = item[0]
    organization = item[-1]

    print('firstname: %s, lastname: %s' %(firstname, lastname))
    print('platform: %s, organization: %s' %(platform, organization))

    finaljsonfile = 'clusterDef.json'
   #clustertype must be one of ['pclusterv2', 'gclusterv2', 'azclusterv2']
    if (platform == 'ca'):
        jsonfile = 'clusterDef.json.AWS'
        clustertype = 'pclusterv2'
        csp_platform = 'AWS'
        if (management_shape == None):
            management_shape="c7i.2xlarge"
        if (compute_instance_type == None):
           #compute_instance_type="c7i.48xlarge"
            compute_instance_type="c7i.24xlarge"
        if (process_instance_type == None):
            process_instance_type="c7i.12xlarge"
        if (zone == None):
            zone="us-east-1b"
        if (region == None):
            region="us-east-1"
    elif (platform == 'cz'):
        jsonfile = 'clusterDef.json.Azure'
        clustertype = 'azclusterv2'
        csp_platform = 'Azure'
        if (management_shape == None):
            management_shape="Standard_F8s_v2"
        if (compute_instance_type == None):
            compute_instance_type="Standard_F72s_v2"
        if (process_instance_type == None):
            process_instance_type="Standard_F48s_v2"
        if (zone == None):
            zone="1"
        if (region == None):
            region="eastus"
    elif (platform == 'cg'):
        jsonfile = 'clusterDef.json.GCP'
        clustertype = 'gclusterv2'
        csp_platform = 'GCP'
        if (management_shape == None):
            management_shape="c2-standard-2"
        if (compute_instance_type == None):
            compute_instance_type="c2-standard-60"
        if (process_instance_type == None):
            process_instance_type="c2-standard-60"
        if (zone == None):
            zone="us-east1-b"
        if (region == None):
            region="us-east1"
    else:
        print('Invalid platfor: ', platform)
        sys.exit(-1)

    if (organization == 'epic'):
        user_bootstrap = "ALLNODES\\n/contrib/%s/setup.sh" %(username)
    else:
        user_bootstrap = "ALLNODES\\n/contrib/Wei.Huang/pwsupport/mount-epic-contrib.sh\\n/contrib/%s/setup.sh" %(username)

    if (clustername == None):
        citl = compute_instance_type.lower()
        citlstr = citl.replace('.', '')
        citlstr1 = citlstr.replace('_', '')
        clusterkind = citlstr1.replace('-', '')
        clustername = '%s%s%s%s' %(lastname.lower(), csp_platform.lower(), organization.lower(), clusterkind)

    if (displayname == None):
        displayname = '%s %s %s %s' %(lastname.upper(), csp_platform.upper(), organization.upper(), compute_instance_type)

    if (description == None):
        description = '%s on %s from %s using %s' %(lastname, csp_platform.upper(), organization.upper(), compute_instance_type)

    if (tags == None):
        tags = 'compute on %s, process on %s' %(compute_instance_type, process_instance_type)

    print('clustername <%s>' %(clustername))
    print('clustertype <%s>' %(clustertype))
    print('displayname <%s>' %(displayname))
    print('description <%s>' %(description))
    print('tags <%s>' %(tags))

#------------------------------------------------------------------
    request = {}
    request['project'] = project
    request['username'] = username
    request['clustertype'] = clustertype
    request['csp_platform'] = csp_platform
    request['management_shape'] = management_shape
    request['compute_instance_type'] = compute_instance_type
    request['process_instance_type'] = process_instance_type
    request['user_bootstrap'] = user_bootstrap
    request['zone'] = zone
    request['region'] = region

    updateJSON(jsonfile, finaljsonfile, request)
   
#------------------------------------------------------------------
    header = prepare_headers(apikey)
    c = Client(pw_url, header, displayname)

    cluster = c.create_v2_cluster(clustername, description, tags, clustertype)
    cluster_id = cluster['_id']

    with open(finaljsonfile) as cluster_defintion:
        data = json.load(cluster_defintion)
        try:
            updated_cluster = c.update_v2_cluster(cluster_id, data)
           #print(updated_cluster)
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

