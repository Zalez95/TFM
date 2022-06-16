import subprocess
import time
import math
import json
import boto3
from datetime import datetime
from bottle import run, post, request, response, get, route


awsAccessKeyId = "AKIA2BIQPL3AKI53QO5K"
awsAccessKeySecret = "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"
awsRegion = "eu-west-1"
toDynamoDBOperator = { "=":"=", "!=":"<>", ">":">", "<":"<", ">=":">=", "<=":"<=" }


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

			filter = req_adhocFilters[i]
			if ("key" in filter) and ("operator" in filter) and ("value" in filter):
				FilterExpression += filter["key"]
				FilterExpression += toDynamoDBOperator.get(filter["operator"], "=")
				FilterExpression += ":filter" + str(i)

				filterTypeStr = columnTypes[columnNames.index(filter["key"])]
				filterValue = (filter["value"] == "True") if (filterTypeStr == "BOOL") else filter["value"]
				ExpressionAttributeValues[":filter" + str(i)] = { filterTypeStr : filterValue }

				previousExpression = True

	#FilterExpression += "gender = :gender AND ageLow < :ageLow"
	#ExpressionAttributeValues[":gender"] = { "S" : "Male" }
	#ExpressionAttributeValues[":ageLow"] = { "N" : "18" }
	#print(FilterExpression)
	#print(ExpressionAttributeValues)

	response = dynamodb_client.scan(
		TableName="valltourisminsta",
		Limit=req_maxDataPoints,
		FilterExpression=FilterExpression,
		ExpressionAttributeValues=ExpressionAttributeValues
	)

	jsonResponseDict = None
	if False:
		jsonResponseDict = {
			"columns":[
				{"text":"id","type":"string"},
				{"text":"faceIndex","type":"number"},
				{"text":"tstamp","type":"string"},
				{"text":"shortCode","type":"string"},
				{"text":"displayUrl","type":"string"},
				{"text":"description","type":"string"},
				{"text":"likesCount","type":"number"},
				{"text":"commentsCount","type":"number"},
				{"text":"confidence","type":"number"},
				{"text":"ageLow","type":"number"},
				{"text":"ageHigh","type":"number"},
				{"text":"gender","type":"string"},
				{"text":"eyeglasses","type":"number"},
				{"text":"sunglasses","type":"number"},
				{"text":"beard","type":"number"},
				{"text":"moustache","type":"number"},
				{"text":"happyConfidence","type":"number"},
				{"text":"surprisedConfidence","type":"number"},
				{"text":"fearConfidence","type":"number"},
				{"text":"sadConfidence","type":"number"},
				{"text":"angryConfidence","type":"number"},
				{"text":"disgustedConfidence","type":"number"},
				{"text":"confusedConfidence","type":"number"},
				{"text":"calmConfidence","type":"number"}
			],
			"rows" : [],
			"type" : "table"
		}
		for item in response["Items"]:
			jsonResponseDict["rows"].append([
				item["id"]["S"],
				int(item["faceIndex"]["N"]),
				int(item["tstamp"]["S"]),
				item["shortCode"]["S"],
				item["displayUrl"]["S"],
				item["description"]["S"],
				int(item["likesCount"]["N"]),
				int(item["commentsCount"]["N"]),
				float(item["confidence"]["N"]),
				int(item["ageLow"]["N"]),
				int(item["ageHigh"]["N"]),
				item["gender"]["S"],
				item["eyeglasses"]["BOOL"] == "true",
				item["sunglasses"]["BOOL"] == "true",
				item["beard"]["BOOL"] == "true",
				item["moustache"]["BOOL"] == "true",
				float(item["happyConfidence"]["N"]),
				float(item["surprisedConfidence"]["N"]),
				float(item["fearConfidence"]["N"]),
				float(item["sadConfidence"]["N"]),
				float(item["angryConfidence"]["N"]),
				float(item["disgustedConfidence"]["N"]),
				float(item["confusedConfidence"]["N"]),
				float(item["calmConfidence"]["N"])
			])
	else:
		jsonResponseDict = []

		for targetName in targetNames:
			datapoints = []
			for item in response["Items"]:
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

	response = dynamodb_client.scan(
		TableName="valltourisminsta",
		AttributesToGet=[req_key]
	)

	values = set()
	for item in response["Items"]:
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
