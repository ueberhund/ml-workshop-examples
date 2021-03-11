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

if ! command -v python3 &> /dev/null 
then 
    echo "python3 could not be found"
    exit
fi

if ! command -v pip3 &> /dev/null 
then 
    echo "pip3 could not be found"
    exit
fi

REGION=$(aws configure get region)
ACCOUNT_ID=$(aws sts get-caller-identity | jq '.Account' -r)

#Create bucket and add files
BUCKET_NAME=personalize-${ACCOUNT_ID}-${REGION}

aws s3 mb s3://${BUCKET_NAME}

cat << EOF > bucket-policy.json
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "personalize.amazonaws.com"
            },
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::${BUCKET_NAME}",
                "arn:aws:s3:::${BUCKET_NAME}/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy file://bucket-policy.json

curl https://raw.githubusercontent.com/quankiquanki/skytrax-reviews-dataset/master/data/airline.csv --output airline.csv 
pip3 install -r requirements.txt
python3 process-airline-data.py 

#Data has the format ITEM_ID / USER_ID / TIMESTAMP / CABIN_TYPE / EVENT_VALUE / EVENT_RATING
aws s3 cp airline-interactions.csv s3://${BUCKET_NAME}/input/airline-interactions.csv

#Data has the format USER_ID / NATIONALITY
aws s3 cp airline-users.csv s3://${BUCKET_NAME}/input/airline-users.csv

echo "Bucket location: ${BUCKET_NAME}"