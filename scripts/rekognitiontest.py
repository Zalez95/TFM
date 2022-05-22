#!/usr/bin/env python3

import boto3


awsAccessKeyId = input("AWS Access Key ID: ")
awsAccessKeySecret = input("AWS Access Key Secret: ")

rekognition_client = boto3.client(
	service_name="rekognition",
	region_name="eu-west-1",
	aws_access_key_id = awsAccessKeyId,
	aws_secret_access_key = awsAccessKeySecret
)
image = {"S3Object": {"Bucket": "valltourisminstabucket", "Name": "happy.jpg"}}
response = rekognition_client.detect_faces(Image=image, Attributes=["ALL", "DEFAULT"])

print("response:")
print(response)
