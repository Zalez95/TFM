import os
import time
import math
import json
import boto3
from datetime import datetime

useTable = False
awsRegion = "eu-west-1"
toDynamoDBOperator = { "=":"=", "!=":"<>", ">":">", "<":"<", ">=":">=", "<=":"<=" }
toGrafanaType = { "BOOL":"boolean", "N":"number", "S":"string" }


dynamodb_client = None


def tagValues(params):
	req_key = params["key"]

	scanResponse = dynamodb_client.scan(
		TableName="valltourisminsta",
		ProjectionExpression=req_key
	)
	items = scanResponse['Items']
	while ("LastEvaluatedKey" in scanResponse):
		scanResponse = dynamodb_client.scan(
			TableName="valltourisminsta",
			ProjectionExpression=req_key,
			ExclusiveStartKey=scanResponse['LastEvaluatedKey']
		)
		items = items + scanResponse['Items']

	values = set()
	for item in items:
		typeStr = list(item[req_key].keys())[0]
		if (typeStr == "N"):
			values.add(str(float(item[req_key]["N"])))
		elif (typeStr == "S"):
			values.add(item[req_key]["S"])
		elif (typeStr == "BOOL"):
			values.add(str(item[req_key]["BOOL"] == "true"))

	valuesArray = []
	for value in values:
		valuesArray.append({"text":value})

	return valuesArray


def init():
	awsAccessKeyId = os.environ.get("AWS_AKEY_ID")
	awsAccessKeySecret = os.environ.get("AWS_AKEY_SECRET")

	globals()["dynamodb_client"] = boto3.client(
		service_name="dynamodb",
		region_name=awsRegion,
		aws_access_key_id = awsAccessKeyId,
		aws_secret_access_key = awsAccessKeySecret
	)


def lambda_handler(event, context):
	init()
	return tagValues(event)
