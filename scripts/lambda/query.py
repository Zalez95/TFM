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


def query(params):
	req_maxDataPoints = params.get('maxDataPoints', 50)
	req_targets = params["targets"]
	req_range = params["range"]
	req_adhocFilters = params["adhocFilters"]
	req_intervalMs = params["scopedVars"]["__interval_ms"]["value"]

	targetNames = []
	for target in req_targets:
		req_target = target["target"]
		if req_target == '' or req_target == '*':
			break
		else:
			targetNames.append(req_target)
	if not targetNames:
		targetNames = columnNames

	previousExpression = False

	FilterExpression = ""
	ExpressionAttributeValues = {}
	if req_range:
		previousExpression = True
		FilterExpression += "dTime BETWEEN :from AND :to"
		ExpressionAttributeValues[":from"] = { "S" : req_range["from"] }
		ExpressionAttributeValues[":to"] = { "S" : req_range["to"] }

	if req_adhocFilters:
		for i in range(len(req_adhocFilters)):
			if previousExpression:
				FilterExpression += " AND "

			adhocFilter = req_adhocFilters[i]
			if ("key" in adhocFilter) and ("operator" in adhocFilter) and ("value" in adhocFilter):
				FilterExpression += adhocFilter["key"]
				FilterExpression += toDynamoDBOperator.get(adhocFilter["operator"], "=")
				FilterExpression += ":filter" + str(i)

				filterTypeStr = columnTypes[columnNames.index(adhocFilter["key"])]
				filterValue = (adhocFilter["value"] == "True") if (filterTypeStr == "BOOL") else adhocFilter["value"]
				ExpressionAttributeValues[":filter" + str(i)] = { filterTypeStr : filterValue }

				previousExpression = True

	#print(FilterExpression)
	#print(ExpressionAttributeValues)

	projectionExpression = "dTime"
	for x in targetNames:
		if x != "dTime":
			projectionExpression += ", " + x

	scanResponse = dynamodb_client.scan(
		TableName="valltourisminsta",
		Limit=req_maxDataPoints,
		ProjectionExpression=projectionExpression,
		FilterExpression=FilterExpression,
		ExpressionAttributeValues=ExpressionAttributeValues
	)
	items = scanResponse["Items"]
	while (len(items) < req_maxDataPoints) and ("LastEvaluatedKey" in scanResponse):
		scanResponse = dynamodb_client.scan(
			TableName="valltourisminsta",
			Limit=req_maxDataPoints,
			ProjectionExpression=projectionExpression,
			FilterExpression=FilterExpression,
			ExpressionAttributeValues=ExpressionAttributeValues,
			ExclusiveStartKey=scanResponse['LastEvaluatedKey']
		)
		items = items + scanResponse['Items']

	jsonResponseDict = None
	if useTable:
		targetNames2 = list(filter(lambda x: x != "dTime", targetNames))

		jsonResponseDict = {
			"columns":[],
			"rows" : [],
			"type" : "table"
		}

		jsonResponseDict["columns"].append({ "text" : "Time", "type" : "time" })
		for targetName in targetNames2:
			typeDynamoDBStr = columnTypes[columnNames.index(targetName)]
			jsonResponseDict["columns"].append({
				"text" : targetName,
				"type" : toGrafanaType[typeDynamoDBStr]
			})

		for item in items:
			row = []

			tstamp = time.mktime(datetime.strptime(item["dTime"]["S"], "%Y-%m-%dT%H:%M:%S").timetuple())
			tstampMs = req_intervalMs * math.ceil(1000 * tstamp / req_intervalMs)
			row.append(tstampMs)

			for targetName in targetNames2:
				typeDynamoDBStr = columnTypes[columnNames.index(targetName)]

				if (typeDynamoDBStr == "N"):
					row.append(float(item[targetName][typeDynamoDBStr]))
				elif (typeDynamoDBStr == "S"):
					row.append(item[targetName][typeDynamoDBStr])
				elif (typeDynamoDBStr == "BOOL"):
					row.append(item[targetName][typeDynamoDBStr] == "true")

			jsonResponseDict["rows"].append(row)
	else:
		jsonResponseDict = []

		for targetName in targetNames:
			datapoints = []
			for item in items:
				tstamp = time.mktime(datetime.strptime(item["dTime"]["S"], "%Y-%m-%dT%H:%M:%S").timetuple())
				tstampMs = req_intervalMs * math.ceil(1000 * tstamp / req_intervalMs)

				typeStr = list(item[targetName].keys())[0]
				if (typeStr == "N"):
					datapoints.append([ float(item[targetName]["N"]), tstampMs ])
				elif (typeStr == "S"):
					datapoints.append([ item[targetName]["S"], tstampMs ])
				elif (typeStr == "BOOL"):
					datapoints.append([ item[targetName]["BOOL"] == "true", tstampMs ])
			jsonResponseDict.append({"target":targetName,"refId":targetName, "datapoints":datapoints})

	return jsonResponseDict


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
	return query(event)
