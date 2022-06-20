import subprocess
import os
import time
import math
import json
import boto3
from datetime import datetime
from bottle import run, post, request, response, get, route

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
		return json.dumps({ req_target : distinctValues })
	else:
		return json.dumps(columnNames)


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

	jsonResponse = json.dumps(jsonResponseDict)
	return jsonResponse


def tagKeys(params):
	columnsArray = []
	for column in columnNames:
		columnsArray.append({"type":"string","text":column})
	return json.dumps(columnsArray)


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

	return json.dumps(valuesArray)


@route('/<path>',method = 'POST')
def process(path):
	params = request.json
	print(params)

	response = ""
	if (path == "search"):
		response = search(params)
	elif (path == "query"):
		response = query(params)
	elif (path == "tag-keys"):
		response = tagKeys(params)
	elif (path == "tag-values"):
		response = tagValues(params)

	print(response)
	return response


@route('/',method = 'GET')
def process():
	return "Hola Mundo"


if __name__ == '__main__':
	awsAccessKeyId = os.environ.get("AWS_AKEY_ID")
	awsAccessKeySecret = os.environ.get("AWS_AKEY_SECRET")

	dynamodb_client = boto3.client(
		service_name="dynamodb",
		region_name=awsRegion,
		aws_access_key_id = awsAccessKeyId,
		aws_secret_access_key = awsAccessKeySecret
	)

	firstRow = dynamodb_client.scan(TableName="valltourisminsta", Limit=1)
	if (firstRow["Items"]):
		columnNames = list(firstRow["Items"][0].keys())
		columnTypes = list(map(lambda x: list(x.keys())[0], firstRow["Items"][0].values()))

	run(host='0.0.0.0', port=8080, debug=True)
