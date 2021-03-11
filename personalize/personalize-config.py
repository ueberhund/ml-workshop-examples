import boto3
import time
import json
import sys

interactions_data=sys.argv[1]
users_data=sys.argv[2]
role_arn=sys.argv[3]

personalize = boto3.client(service_name='personalize')
personalize_runtime = boto3.client(service_name='personalize-runtime')
personalize_events = boto3.client(service_name='personalize-events')

dataset_group_name = "airlines-dataset-group"

create_dataset_group_response = personalize.create_dataset_group(
    name = dataset_group_name
)

dataset_group_arn = create_dataset_group_response['datasetGroupArn']

status = None
max_time = time.time() + 3*60*60 # 3 hours
while time.time() < max_time:
    describe_dataset_group_response = personalize.describe_dataset_group(
        datasetGroupArn = dataset_group_arn
    )
    status = describe_dataset_group_response["datasetGroup"]["status"]
    print("DatasetGroup: {}".format(status))
    
    if status == "ACTIVE" or status == "CREATE FAILED":
        break
        
    time.sleep(20)

schema_name="airlines-interaction-schema"

schema = {
    "type": "record",
    "name": "Interactions",
    "namespace": "com.amazonaws.personalize.schema",
    "fields": [
        {
            "name": "ITEM_ID",
            "type": "string"
        },
        {
            "name": "USER_ID",
            "type": "string"
        },
        {
            "name": "TIMESTAMP",
            "type": "long"
        },
        {
            "name":"CABIN_TYPE",
            "type": "string",
            "categorical": True
        },
        {
          "name": "EVENT_TYPE",
          "type": "string"
        },
        {
          "name": "EVENT_VALUE",
          "type": "float"
        }
    ],
    "version": "1.0"
}

create_schema_response = personalize.create_schema(
    name = schema_name,
    schema = json.dumps(schema)
)

schema_arn = create_schema_response['schemaArn']

dataset_type = "INTERACTIONS"
create_dataset_response = personalize.create_dataset(
    datasetType = dataset_type,
    datasetGroupArn = dataset_group_arn,
    schemaArn = schema_arn,
    name = "airlines-dataset-interactions" 
)

interactions_dataset_arn = create_dataset_response['datasetArn']

metadata_schema_name="airlines-users-schema"

metadata_schema = {
    "type": "record",
    "name": "Users",
    "namespace": "com.amazonaws.personalize.schema",
    "fields": [
        {
            "name": "USER_ID",
            "type": "string"
        },
        {
            "name": "NATIONALITY",
            "type": "string",
            "categorical": True
        }
    ],
    "version": "1.0"
}

create_metadata_schema_response = personalize.create_schema(
    name = metadata_schema_name,
    schema = json.dumps(metadata_schema)
)

metadata_schema_arn = create_metadata_schema_response['schemaArn']

dataset_type = "USERS"
create_metadata_dataset_response = personalize.create_dataset(
    datasetType = dataset_type,
    datasetGroupArn = dataset_group_arn,
    schemaArn = metadata_schema_arn,
    name = "airlines-metadata-dataset-users"
)

metadata_dataset_arn = create_metadata_dataset_response['datasetArn']

#Import interactions data
create_dataset_import_job_response = personalize.create_dataset_import_job(
    jobName = "airlines-dataset-import-job",
    datasetArn = interactions_dataset_arn,
    dataSource = {
        "dataLocation": interactions_data
    },
    roleArn = role_arn
)

dataset_import_job_arn = create_dataset_import_job_response['datasetImportJobArn']

#Import Users data
create_metadata_dataset_import_job_response = personalize.create_dataset_import_job(
    jobName = "airlines-users-metadata-dataset-import-job",
    datasetArn = metadata_dataset_arn,
    dataSource = {
        "dataLocation": users_data
    },
    roleArn = role_arn
)

metadata_dataset_import_job_arn = create_metadata_dataset_import_job_response['datasetImportJobArn']

#Wait for jobs to reach ACTIVE status
status = None
max_time = time.time() + 3*60*60 # 3 hours
while time.time() < max_time:
    describe_dataset_import_job_response = personalize.describe_dataset_import_job(
        datasetImportJobArn = dataset_import_job_arn
    )
    
    dataset_import_job = describe_dataset_import_job_response["datasetImportJob"]
    if "latestDatasetImportJobRun" not in dataset_import_job:
        status = dataset_import_job["status"]
        print("DatasetImportJob: {}".format(status))
    else:
        status = dataset_import_job["latestDatasetImportJobRun"]["status"]
        print("LatestDatasetImportJobRun: {}".format(status))
    
    if status == "ACTIVE" or status == "CREATE FAILED":
        break
        
    time.sleep(60)

status = None
max_time = time.time() + 3*60*60 # 3 hours
while time.time() < max_time:
    describe_dataset_import_job_response = personalize.describe_dataset_import_job(
        datasetImportJobArn = metadata_dataset_import_job_arn
    )
    
    dataset_import_job = describe_dataset_import_job_response["datasetImportJob"]
    if "latestDatasetImportJobRun" not in dataset_import_job:
        status = dataset_import_job["status"]
        print("DatasetImportJob: {}".format(status))
    else:
        status = dataset_import_job["latestDatasetImportJobRun"]["status"]
        print("LatestDatasetImportJobRun: {}".format(status))
    
    if status == "ACTIVE" or status == "CREATE FAILED":
        break
        
    time.sleep(60)

#Create solutions
recipe_arn = "arn:aws:personalize:::recipe/aws-user-personalization"

create_solution_response = personalize.create_solution(
    name = "airlines-user-personalization-solution-HPO",
    datasetGroupArn = dataset_group_arn,
    recipeArn = recipe_arn,
    performHPO=True
)

solution_arn = create_solution_response['solutionArn']

create_solution_version_response = personalize.create_solution_version(
    solutionArn = solution_arn
)

solution_version_arn = create_solution_version_response['solutionVersionArn']