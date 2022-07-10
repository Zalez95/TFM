#!/usr/bin/env python3

import sys
import boto3


def main(argv):
	if len(argv) < 2:
		print("Error: usage " + argv[0] + " <file>")
		sys.exit()

	awsAccessKeyId = input("AWS Access Key ID: ")
	awsAccessKeySecret = input("AWS Access Key Secret: ")

	try:
		rekognition_client = boto3.client(
			service_name="rekognition",
			region_name="eu-west-1",
			aws_access_key_id = awsAccessKeyId,
			aws_secret_access_key = awsAccessKeySecret
		)
		image = {"S3Object": {"Bucket": "valltourisminstabucket", "Name": argv[1]}}
		response = rekognition_client.detect_faces(Image=image, Attributes=["ALL", "DEFAULT"])

		print("response:")
		print(response)
	except Exception as e:
		print("Failed to connect with Rekognition: " + str(e))

if __name__ == "__main__":
	main(sys.argv)
