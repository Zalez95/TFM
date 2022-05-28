#!/usr/bin/env python3

import sys
import boto3
import json


def main(argv):
	if len(argv) < 3:
		print("Error: usage " + argv[0] + " <looter json path> <rekognition json path>")
		return

	awsAccessKeyId = input("AWS Access Key ID: ")
	awsAccessKeySecret = input("AWS Access Key Secret: ")

	dynamodb_client = boto3.client(
		service_name="dynamodb",
		region_name="eu-west-1",
		aws_access_key_id = awsAccessKeyId,
		aws_secret_access_key = awsAccessKeySecret
	)

	tables = dynamodb_client.list_tables()
	if not tables or not tables["TableNames"] or \
			("looter" not in tables["TableNames"]) or \
			("rekognition" not in tables["TableNames"]):
		print("Error: tables doesn't exist")
		return

	id = ""
	with open(argv[1]) as looterJsonFile:
		looterJsonContent = json.loads(looterJsonFile.read())

		id = looterJsonContent["id"]

		response = dynamodb_client.put_item(
			TableName='looter',
			Item={
				"id" : { 'S': id },
				"timestamp" : { 'S': str(looterJsonContent["taken_at_timestamp"]) },
				"url" : { 'S': looterJsonContent["display_url"] },
				"description" : { 'S': looterJsonContent["edge_media_to_caption"]["edges"][0]["node"]["text"] },
				"likesCount" : { 'N': str(looterJsonContent["edge_liked_by"]["count"]) },
				"commentsCount" : { 'N': str(looterJsonContent["edge_media_to_comment"]["count"]) }
			}
		)

		print("response:")
		print(response)

	with open(argv[2]) as rekJsonFile:
		rekJsonContent = json.loads(rekJsonFile.read())

		for iFaceDetails in range(len(rekJsonContent["FaceDetails"])):
			faceDetails = rekJsonContent["FaceDetails"][iFaceDetails]

			emotions = { x["Type"] : x["Confidence"] for x in faceDetails["Emotions"] }

			response = dynamodb_client.put_item(
				TableName='rekognition',
				Item={
					"id" : { 'S': id },
					"faceIndex" : { 'N': str(iFaceDetails) },
					"confidence" : { 'N' : str(faceDetails["Confidence"]) },
					"ageLow" : { 'N' : str(faceDetails["AgeRange"]["Low"]) },
					"ageHigh" : { 'N' : str(faceDetails["AgeRange"]["High"]) },
					"gender" : { 'S' : faceDetails["Gender"]["Value"] },
					"eyeglasses" : { 'BOOL' : faceDetails["Eyeglasses"]["Value"] == True },
					"sunglasses" : { 'BOOL' : faceDetails["Sunglasses"]["Value"] == True },
					"beard" : { 'BOOL' : faceDetails["Beard"]["Value"] == True },
					"moustache" : { 'BOOL' : faceDetails["Mustache"]["Value"] == True },
					"happyConfidence" : { 'N' : str(emotions["HAPPY"]) },
					"surprisedConfidence" : { 'N' : str(emotions["SURPRISED"]) },
					"fearConfidence" : { 'N' : str(emotions["FEAR"]) },
					"sadConfidence" : { 'N' : str(emotions["SAD"]) },
					"angryConfidence" : { 'N' : str(emotions["ANGRY"]) },
					"disgustedConfidence" : { 'N' : str(emotions["DISGUSTED"]) },
					"confusedConfidence" : { 'N' : str(emotions["CONFUSED"]) },
					"calmConfidence" : { 'N' : str(emotions["CALM"]) }
				}
			)

			print("response:")
			print(response)


if __name__ == "__main__":
	main(sys.argv)
