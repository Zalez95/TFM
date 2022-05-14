#!/usr/bin/env python3

import boto3
import json


awsAccessKeyId = input("AWS Access Key ID: ")
awsAccessKeySecret = input("AWS Access Key Secret: ")

dynamodb_client = boto3.client(
	service_name="dynamodb",
	region_name="eu-west-1",
	aws_access_key_id = awsAccessKeyId,
	aws_secret_access_key = awsAccessKeySecret
)

try:
	tableResponse = dynamodb_client.create_table(
			TableName='Rekognition_FaceDetails',
			KeySchema=[
				{
					'AttributeName': 'RequestId',
					'KeyType': 'HASH'  # Partition key
				}
			],
			AttributeDefinitions=[
				{
					'AttributeName': 'RequestId',
					'AttributeType': 'S'
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 10,
				'WriteCapacityUnits': 10
			}
		)
	print("response:")
	print(tableResponse)
except Exception as e:
	print("Can't create table: " + str(e))

with open("faceDetails.json") as jsonFile:
	jsonText = jsonFile.read()
	jsonContent = json.loads(jsonText)
	requestId = jsonContent["ResponseMetadata"]["RequestId"]
	response = dynamodb_client.put_item(
		TableName='Rekognition_FaceDetails',
		Item={
			"RequestId" : { 'S' : requestId },
			"JSON" : { 'S': jsonText }
		}
	)

	print("response:")
	print(response)
