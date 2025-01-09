#!/bin/bash

export PW_PLATFORM_HOST=noaa.parallel.works
export PW_API_KEY="Your Own PW_API_KEY from ParallelWork site"
#To generate your own PW_API_KEY:
#1. Log in to your noaa.parallel.works account.
#2. Click (and hold) at your username (at upper right corner)
#3. Move down the menu to "ACCOUNT".
#4. Click "Authentication" at top leftish on the menu.
#5. Click on "API Keys" and following the steps to "Add Key", Give it a meaningful and choose Expiration "no expiration".
#   make sure to copy the key when it pops up during creation. This is the only time you can access this key.

#Please note, you shouldn't send this PW_API_KEY to anyone via email or by any other channel.
#This key can be used to authenticate as your user into the platform, so if the wrong person gets it,
#they could potentially use it to access your account and files.

clustertype='pclusterv2'
username="Wei.Huang"
management_shape="c7i.2xlarge"
compute_instance_type="c7i.48xlarge"
process_instance_type="c7i.12xlarge"
#project="ca-epic"
project="ca-sfs-emc"

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
#displayname is a name for your cluster.
#description is a string discribe what this cluster is for. it can be any string
#tags is the tag for the cluster. As it will show on Parallel-Works web site associate with the cluser. So, better to make it meaningful

if [[ $project == *"epic"* ]]; then
    echo "Using EPIC account"
    lorganization=epic
    uorganization=EPIC
elif [[ $project == *"sfs-emc"* ]]; then
    echo "Using EMC account"
    lorganization=emc
    uorganization=EMC
else
    echo "Unknown project: ${project}. exit"
    exit -1
fi

if [[ $project == *"ca-"* ]]; then
    lcspname=aws
    ucspname=AWS
    clustertype=pclusterv2
elif [[ $project == *"cg-"* ]]; then
    lcspname=gcp
    ucspname=GCP
    clustertype=gclusterv2
elif [[ $project == *"cz-"* ]]; then
    lcspname=azure
    ucspname=AZURE
    clustertype=azclusterv2
else
    echo "Unknown CSP: ${project}. exit"
    exit -1
fi

IFS='.' read -r instance_class linstance_size <<< "$compute_instance_type"
IFS='.' read -r firstname lastname <<< "$username"
lowerlastname=$(echo "$lastname" | sed 's/.*/\L&/')

displayname="${ucspname} ${uorganization} ${lastname} ${compute_instance_type}"
description="${ucspname} cluster for ${firstname} ${lastname} from ${uorganization} using ${compute_instance_type}"
clustername=${lcspname}${lorganization}${lowerlastname}${instance_class}
tags="computer on ${compute_instance_type}, process on ${process_instance_type}"

echo "displayname: ${displayname}"

python createCluster.py \
	--jsonfile=clusterDef.json \
	--clustername=${clustername} \
	--clustertype=${clustertype} \
	--displayname="${displayname}" \
	--description="${description}" \
	--tags="${tags}"

