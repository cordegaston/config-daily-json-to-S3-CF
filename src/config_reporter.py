"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from distutils.command.config import config
import os
import boto3
from datetime import datetime
import json
import logging
import csv
from botocore.exceptions import ClientError 


today = datetime.now().strftime("%Y-%m-%d")  # Currnent day
filename = f'/tmp/changed_resources-{today}.csv'  # CSV report filename
AGGREGATOR_NAME = os.environ['AGGREGATOR_NAME']  # AWS Config Aggregator name
BUCKET = os.environ['BUCKET_NAME'] # Bucket Name to store file

# Generate the resource link to AWS Console UI
def get_link(aws_region, resource_id, resource_type):
    return f'https://{aws_region}.console.aws.amazon.com/config/home?region={aws_region}#/resources/timeline?resourceId={resource_id}&resourceType={resource_type}'


# Generate the CSV Report
def create_report(AGGREGATOR_NAME, today, filename):
    client = boto3.client('config')
    response = client.select_aggregate_resource_config(
        Expression=f"SELECT * WHERE configurationItemCaptureTime LIKE '{today}%'",
        ConfigurationAggregatorName=AGGREGATOR_NAME
    )
    changed_resources = response["Results"]
    json_list = [json.loads(line) for line in changed_resources]
    # Transform the JSON response to CSV file
    for resource in json_list:
        aws_region = resource['awsRegion']
        resource_id = resource['resourceId']
        resource_type = resource['resourceType']
        resource['Link'] = get_link(aws_region, resource_id, resource_type)
        print(resource)
    all_fields = set()
    for item in json_list:
        all_fields.update(item.keys())
    # Save the report file
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(all_fields))
        writer.writeheader()
        writer.writerows(json_list)
    print("Report generated " + filename)


def uploadFileS3(filename, BUCKET):
    s3 = boto3.client('s3')
    object_name = os.path.basename(filename)

    try:
        s3.upload_file(filename, BUCKET, object_name)
        print("Upload Successful")    
    
    except ClientError as e:
        logging.error(e)
        print("The file was not found")
        exit()


def config_reporter(event, lambda_context):
    create_report(AGGREGATOR_NAME, today, filename)
    uploadFileS3(filename, BUCKET)