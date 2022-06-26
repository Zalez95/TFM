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
columnNames = []
columnTypes = []


def search(params):
	req_target = params["target"]
	if (req_target):
		distinctValues = []
		return { req_target : distinctValues }
	else:
		return columnNames


def init():
	awsAccessKeyId = os.environ.get("AWS_AKEY_ID")
	awsAccessKeySecret = os.environ.get("AWS_AKEY_SECRET")

	globals()["dynamodb_client"] = boto3.client(
		service_name="dynamodb",
		region_name=awsRegion,
		aws_access_key_id = awsAccessKeyId,
		aws_secret_access_key = awsAccessKeySecret
	)

	firstRow = dynamodb_client.scan(TableName="valltourisminsta", Limit=1)
	if (firstRow["Items"]):
		globals()["columnNames"] = list(firstRow["Items"][0].keys())
		globals()["columnTypes"] = list(map(lambda x: list(x.keys())[0], firstRow["Items"][0].values()))


def lambda_handler(event, context):
	init()
	return search(event)
