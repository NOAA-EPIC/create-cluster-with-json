#!/bin/bash

export PW_API_KEY="Your Own PW-API-KEY generated at parallel-Work web-site"
export PW_PLATFORM_HOST=noaa.parallel.works

clustertype='pclusterv2'
username="Wei.Huang"
management_shape="c7i.2xlarge"
compute_instance_type="c7i.48xlarge"
process_instance_type="c7i.12xlarge"
project="ca-epic"

sed -e "s/CLUSTERTYPE/${clustertype}/g" \
    -e "s/USERNAME/${username}/g" \
    -e "s/MANAGEMENT_SHAPE/${management_shape}/g" \
    -e "s/COMPUTE_INSTANCE_TYPE/${compute_instance_type}/g" \
    -e "s/PROCESS_INSTANCE_TYPE/${process_instance_type}/g" \
    -e "s/PROJECT/${project}/g" \
    clusterDef.json.AWS.c7i.48xlarge > clusterDef.json

#jsonfile is the file to process.
#clustername must be all lower cases english characters, plus numbers. NO special characters, like underscore, star, etc.
#clusterype must be one of ['pclusterv2', 'gclusterv2', 'azclusterv2'], which corespondint to [AWS, GCP, Azure]
#displayname is a name for your cluster. Here it is named as "CSP-name Acccount-name user-name image-type(chip/node type)"
#description is a string discribe what this cluster is for. it can be any string
#tags is the tag for the cluster. As it will show on Parallel-Works web site associate with the cluser. So, better to make it meaningful

python createCluster.py \
	--jsonfile='clusterDef.json' \
	--clustername='awsepicweic7i' \
	--clustertype='pclusterv2' \
	--displayname='AWS EPIC Wei c7i.48xlarge' \
	--description='Wei pclusterv2 on AWS from EPIC using c7i.48xlarge' \
	--tags='computer on c7i.48xlarge, process on c7i.24xlarge'

