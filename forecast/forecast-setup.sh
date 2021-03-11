#!/bin/bash

set -e

#Check to make sure all required commands are installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found"
    exit
fi

if ! command -v aws &> /dev/null
then
    echo "aws could not be found"
    exit
fi

REGION=$(aws configure get region)
ACCOUNT_ID=$(aws sts get-caller-identity | jq '.Account' -r)

#Create bucket and add files
BUCKET_NAME=forecastpoc-${ACCOUNT_ID}-${REGION}

aws s3 mb s3://${BUCKET_NAME}

curl https://raw.githubusercontent.com/aws-samples/amazon-forecast-samples/master/notebooks/immersion_day/data/item-demand-time.csv --output item-demand-time.csv 

#Data has the format timestamp / target_value / item_id
aws s3 cp item-demand-time.csv s3://${BUCKET_NAME}/input/item-demand-time.csv

echo "Bucket location: ${BUCKET_NAME}"