import os
import time
import sys
import requests
import json
import base64
import argparse
import logging

from client import Client

# Create and configure logger
logging.basicConfig(filename="create-cluster.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------
def prepare_headers(apikey):
    encoded_bytes = base64.b64encode(apikey.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + encoded_string
    }
    return headers

# --------------------------------------------------------------------------
def updateJSON(json_in, json_out, request):
    """
    Update JSON file with request.
    the request must include informations"
    username: [John.Doe]
    project: [ca-epic]
    clustertype: [pclusterv2]
    management_shape: [c7i.2xlarge]
    compute_instance_type: [c7i.24xlarge]
    process_instance_type: [c7i.12xlarge]
    zone: [us-east-1, eastus, us-east1b]
    region: [us-east-1]
    csp_platform: [AWS]
    ----------
    returns:
    None
    """
    needed_json_vars = ['username', 'project', 'clustertype', 'management_shape',
        'compute_instance_type', 'process_instance_type', 'zone', 'region', 'csp_platform']

    request_keys = request.keys()

    for var in needed_json_vars:
        if (var not in request_keys):
            logger.error(f'needed JSON var: {var} is not in request dictionary.')
            raise SystemExit

    csp_platform = request['csp_platform']
    # Read the JSON file, and update it with request.
    with open(json_in, 'r') as f:
        data = json.load(f)

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
    elif (csp_platform == 'Azure'):
        data['resourceData']['zones'] = request['zone']
        data['resourceData']['partition_config'][0]['zones'] = request['zone']
        data['resourceData']['partition_config'][1]['zones'] = request['zone']
    elif (csp_platform == 'GCP'):
        data['resourceData']['zone'] = request['zone']
        data['resourceData']['partition_config'][0]['zone'] = request['zone']
        data['resourceData']['partition_config'][1]['zone'] = request['zone']

    # Write the updated data back to the file
    with open(json_out, 'w') as f:
        # json.dump(data, f, indent=4)
        json.dump(data, f, indent=2)


# ------------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-u", "--username", type=str, required=True,
                        help="user login name. Usually user's Firstname.Last_name")
    parser.add_argument("-p", "--project", type=str, required=True,
                        help="project name, like ca-epic")
    parser.add_argument("-t", "--tags", type=str, required=False,
                        default=None,
                        help="Optional tag for the created cluster")
    parser.add_argument("--management_shape", type=str, required=False,
                        default=None,
                        help="Optional Management_shape, or Controller: c7i.2xlarge, Standard_F8s_v2, c2-standard-2")
    parser.add_argument("--compute_instance_type", type=str, required=False,
                        default=None,
                        help="Optional compute node: c7i.24xlarge, Standard_F72s_v2, c2-standard-60")
    parser.add_argument("--process_instance_type", type=str, required=False,
                        default=None,
                        help="Optional process node: c7i.12xlarge, Standard_F48s_v2, c2-standard-60")
    parser.add_argument("--zone", type=str, required=False,
                        default=None,
                        help="Optional CSP zone: us-east-1, 1, us-east1-b")
    parser.add_argument("--region", type=str, required=False,
                        default=None,
                        help="Optional CSP region: us-east-1, eastus, us-east1")
    parser.add_argument("--clustername", type=str, required=False,
                        default=None,
                        help="Optional clustername: must be all lower cases, no special characters")
    parser.add_argument("--displayname", type=str, required=False,
                        default=None,
                        help="Optional displayname: Character string as Display Name")
    parser.add_argument("--description", type=str, required=False,
                        default=None,
                        help="Optional description: Character string to describe this cluster")
    args = parser.parse_args()

    logger.info(f'username: {args.username}')
    logger.info(f'project:  {args.project}')
    logger.info(f'management_shape: {args.management_shape}')
    logger.info(f'compute_instance_type: {args.compute_instance_type}')
    logger.info(f'process_instance_type: {args.process_instance_type}')
    logger.info(f'region: {args.region}')
    logger.info(f'zone: {args.zone}')
    logger.info(f'tags: {args.tags}')
    logger.info(f'clustername: {args.clustername}')
    logger.info(f'displayname: {args.displayname}')
    logger.info(f'description: {args.description}')

#------------------------------------------------------------------
    api_pki_file = 'pw_api.key'

    if os.path.exists(api_pki_file):
        with open(api_pki_file, "r") as file:
            for line in file.readlines():
                if (line.find('export PW_') >= 0):
                    headstr, _, value = line.strip().partition('=')
                    exphead, _, key = headstr.partition(' ')
                    os.environ[key] = value
    else:
        logger.error(f'needed JSON var: {var} is not in request dictionary.')
        logger.error(f"File '{api_pki_file}' does not exist.")
        logger.error(f"User must have a pw_api.key file with its ParallelWorks API_PKI key.")
        logger.error(f"Check file: pw_api.key.sample to see what it looks like, and how to get it.")
        raise SystemExit

    if os.environ.get('PW_PLATFORM_HOST') is not None:
        pw_url = 'https://' + os.environ['PW_PLATFORM_HOST']
    else:
        pw_url = 'https://noaa.parallel.works'

    if os.environ.get('PW_API_KEY') is not None:
        apikey = os.environ['PW_API_KEY']
    else:
        logger.error(f'PW_API_KEY is not set in environmental variablse. Exit.')
        raise SystemExit

#------------------------------------------------------------------
    item = args.username.split('.')
    firstname = item[0]
    lastname = item[1]

    item = args.project.split('-')
    platform = item[0]
    organization = item[-1]

    tags = args.tags
    zone = args.zone
    region = args.region
    clustername = args.clustername
    displayname = args.displayname
    description = args.description
    management_shape = args.management_shape
    compute_instance_type = args.compute_instance_type
    process_instance_type = args.process_instance_type

    finaljsonfile = 'clusterDef.json'
    # clustertype must be one of ['pclusterv2', 'azclusterv2', 'gclusterv2']
    if (platform == 'ca'):
        jsonfile = 'clusterDef.json.AWS'
        clustertype = 'pclusterv2'
        csp_platform = 'AWS'
        if (management_shape == None):
            management_shape = "c7i.2xlarge"
        if (compute_instance_type == None):
           #compute_instance_type = "c7i.48xlarge"
            compute_instance_type = "c7i.24xlarge"
        if (process_instance_type == None):
            process_instance_type = "c7i.12xlarge"
        if (zone == None):
            zone = "us-east-1b"
        if (region == None):
            region = "us-east-1"
    elif (platform == 'cz'):
        jsonfile = 'clusterDef.json.Azure'
        clustertype = 'azclusterv2'
        csp_platform = 'Azure'
        if (management_shape == None):
            management_shape = "Standard_F8s_v2"
        if (compute_instance_type == None):
            compute_instance_type = "Standard_F72s_v2"
        if (process_instance_type == None):
            process_instance_type = "Standard_F48s_v2"
        if (zone == None):
            zone = "1"
        if (region == None):
            region = "eastus"
    elif (platform == 'cg'):
        jsonfile = 'clusterDef.json.GCP'
        clustertype = 'gclusterv2'
        csp_platform = 'GCP'
        if (management_shape == None):
            management_shape = "c2-standard-2"
        if (compute_instance_type == None):
            compute_instance_type = "c2-standard-60"
        if (process_instance_type == None):
            process_instance_type = "c2-standard-60"
        if (zone == None):
            zone = "us-east1-b"
        if (region == None):
            region = "us-east1"
    else:
        logger.error(f'Invalid platfor: {plaform}')
        raise SystemExit

    if (organization == 'epic'):
        user_bootstrap = f"ALLNODES\\n/contrib/{args.username}/setup.sh"
    else:
        user_bootstrap = f"ALLNODES\\n/contrib/{args.username}/pwsupport/mount-epic-contrib.sh\\n/contrib/%s/setup.sh"

    if (clustername == None):
        citl = compute_instance_type.lower()
        citlstr = citl.replace('.', '')
        citlstr1 = citlstr.replace('_', '')
        clusterkind = citlstr1.replace('-', '')
       #clustername = '%s%s%s%s' %(lastname.lower(), csp_platform.lower(), organization.lower(), clusterkind)
        clustername = f'{lastname.lower()}{csp_platform.lower()}{organization.lower()}{clusterkind}'

    if (displayname == None):
       #displayname = '%s %s %s %s' %(lastname.upper(), csp_platform.upper(), organization.upper(), compute_instance_type)
        displayname = f'{lastname.upper()} {csp_platform.upper()} {organization.upper()} {compute_instance_type}'

    if (description == None):
       #description = '%s on %s from %s using %s' %(lastname, csp_platform.upper(), organization.upper(), compute_instance_type)
        description = f'{lastname} on {csp_platform.upper()} from {organization.upper()} using {compute_instance_type}'

    if (tags == None):
        tags = 'compute on %s, process on %s' %(compute_instance_type, process_instance_type)

    logger.info(f'Firstname: {firstname}, Lastname: {lastname}')
    logger.info(f'platform:  {platform}')
    logger.info(f'organization: {organization}')
    logger.info(f'management_shape: {management_shape}')
    logger.info(f'compute_instance_type: {compute_instance_type}')
    logger.info(f'process_instance_type: {process_instance_type}')
    logger.info(f'zone: {zone}')
    logger.info(f'region: {region}')
    logger.info(f'clustertype: {clustertype}')
    logger.info(f'displayname: {displayname}')
    logger.info(f'description: {description}')
    logger.info(f'tags: {tags}')

    # ------------------------------------------------------------------
    request = {}
    request['project'] = args.project
    request['username'] = args.username
    request['clustertype'] = clustertype
    request['csp_platform'] = csp_platform
    request['management_shape'] = management_shape
    request['compute_instance_type'] = compute_instance_type
    request['process_instance_type'] = process_instance_type
    request['user_bootstrap'] = user_bootstrap
    request['zone'] = zone
    request['region'] = region

    updateJSON(jsonfile, finaljsonfile, request)
   
    # ------------------------------------------------------------------
    header = prepare_headers(apikey)
    c = Client(pw_url, header, displayname)

    cluster = c.create_v2_cluster(clustername, description, tags, clustertype)
    cluster_id = cluster['_id']

    with open(finaljsonfile) as cluster_defintion:
        data = json.load(cluster_defintion)
        try:
            updated_cluster = c.update_v2_cluster(cluster_id, data)
        except requests.exceptions.HTTPError as e:
            print(e.response.text)


# ------------------------------------------------------------------
if __name__ == '__main__':
    main()
