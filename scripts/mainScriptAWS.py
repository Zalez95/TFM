#!/usr/bin/env python3

import json
import boto3
from instalooter.looters import HashtagLooter
from instalooter.pbar import ProgressBar
from fs_s3fs import S3FS
from getpass import getpass
from datetime import datetime
import sys
import os

REKOGNITION_LIMIT = 5000


class MyProgressBar(ProgressBar):
	def __init__(self, it = None, *args, **kwargs):
		self.count = 0
		self.maximum = 0
		ProgressBar.__init__(self, it)
		print()

	def update(self):
		self.count += 1
		self.printCurrent()

	def set_maximum(self, maximum):
		self.maximum = maximum

	def finish(self):
		self.printCurrent()
		print("")

	def printCurrent(self):
		perc = 0
		if self.maximum > 0:
			perc = 100.0 * self.count / float(self.maximum)
		print("\r\033[KProgress:\t" + str(self.count) + "/" + str(self.maximum)
			+ "\t" + "{:.3f}".format(perc) + "%", end="")


class App:
	instaUser = ""
	instaPass = ""
	awsAccessKeyId = ""
	awsAccessKeySecret = ""
	awsRegion = ""
	awsBucket = ""
	hashtag = ""
	instaMediaLimit = None
	s3fs = None
	looterSession = None
	rekognition = None
	dynamodb = None
	rekognitionImgCount = 0

	def connect(self):
		""" Connects to all the needed services """
		# Connect to S3 storage
		try:
			print("Trying to connect to " + self.awsBucket + "...")

			self.s3fs = S3FS(
				bucket_name=self.awsBucket,
				region=self.awsRegion,
				aws_access_key_id=self.awsAccessKeyId,
				aws_secret_access_key=self.awsAccessKeySecret
			)

			print("Successfully connected to " + self.awsBucket)
		except Exception as e:
			print("Failed to connect with " + self.awsBucket + ": " + str(e))
			return False

		# Connect to Instagram
		try:
			print("Trying to connect to Instagram...")

			looter = HashtagLooter(hashtag="", session=self.looterSession)
			looter.login(self.instaUser, self.instaPass)

			print("Successfully connected to Instagram")
		except Exception as e:
			print("Failed to connect to Instagram: " + str(e))
			return False

		# Connect to Rekognition
		try:
			print("Trying to connect with Rekognition...")

			self.rekognition = boto3.client(
				service_name="rekognition",
				region_name=self.awsRegion,
				aws_access_key_id = self.awsAccessKeyId,
				aws_secret_access_key = self.awsAccessKeySecret
			)

			print("Successfully connected to Rekognition")
		except Exception as e:
			print("Failed to connect to Rekognition: " + str(e))
			self.looter.logout()
			return False

		# Connect to DynamoDB
		try:
			print("Trying to connect with DynamoDB...")

			self.dynamodb = boto3.client(
				service_name="dynamodb",
				region_name="eu-west-1",
				aws_access_key_id = self.awsAccessKeyId,
				aws_secret_access_key = self.awsAccessKeySecret
			)

			print("Successfully connected to DynamoDB")
		except Exception as e:
			print("Failed to connect to DynamoDB: " + str(e))
			self.looter.logout()
			return False

		# Retrieve the rekognitionImgCount value from S3
		print("Trying to read rekognitionImgCount...")
		with self.s3fs.open("rekognitionImgCount.txt", "r") as s3File:
			s3File.seek(0)
			lines = s3File.readlines()
			self.rekognitionImgCount = int(lines[0]) if lines else 0
			print("Successfully read rekognitionImgCount: " + str(self.rekognitionImgCount))

		# Create DynamoDB tables if they don't exist
		if not self.__checkDBTables():
			print("Trying to create DynamoDB tables...")
			if self.__createDBTables():
				print("Successfully created DynamoDB tables")
			else:
				print("Failed to create DynamoDB tables")
				return False

		return True

	def disconnect(self):
		# Write rekognitionImgCount to S3
		print("Trying to write rekognitionImgCount...")
		with self.s3fs.open("rekognitionImgCount.txt", "w") as s3File:
			s3File.write(str(self.rekognitionImgCount))
			print("Successfully written rekognitionImgCount: " + str(self.rekognitionImgCount))

		try:
			print("Trying to disconnect from Instagram...")

			looter = HashtagLooter(hashtag="", session=self.looterSession)
			looter.logout()

			print("Successfully disconnected from Instagram")
		except Exception as e:
			print("Failed to disconnect from Instagram: " + str(e))
			return False

		try:
			print("Trying to disconnect from AWS...")

			self.rekognition = None
			self.looterSession = None
			self.s3fs = None
			self.dynamodb = None

			print("Successfully disconnected from AWS")
		except Exception as e:
			print("Failed to disconnect from AWS: " + str(e))
			return False

		return True

	def downloadImages(self):
		""" Retrieve images and JSONs from Instagram and stores them in S3 """
		try:
			print("Trying to download images from Instagram...")

			looter = HashtagLooter(self.hashtag, dump_json=True, jobs=12, session=self.looterSession)

			print("Logged in? " + str(looter.logged_in()))
			mediaCount = looter.download_pictures(
				self.s3fs, media_count=self.instaMediaLimit, new_only=True,
				dlpbar_cls=MyProgressBar)

			print("Successfully downloaded from Instagram " + str(mediaCount) + " images")
			return True
		except Exception as e:
			print("Failed to download all the images: " + str(e))
			return False

	def processImages(self):
		""" Process images with Rekognition and stores them as JSONs in S3 """
		try:
			print("Trying to process the images...")

			# Note: images that were download prior to the current run
			# but failed to retrieve its Rekognition JSON can also be
			# processed in this step
			filenames = self.s3fs.listdir("")
			imagesToProcess = list(filter(lambda x: x[-4:] == ".jpg" and not self.s3fs.exists(x[:-4] + "_rek.json"), filenames))
			progressBar = MyProgressBar()
			progressBar.set_maximum(len(imagesToProcess))
			imageSuccessCount = 0

			for image in imagesToProcess:
				progressBar.update()
				progressBar.printCurrent()

				if (self.rekognitionImgCount > REKOGNITION_LIMIT):
					raise Exception("Rekognition image count exceeded")

				response = self.rekognition.detect_faces(
					Image={ "S3Object" : { "Bucket" : self.awsBucket, "Name" : image } },
					Attributes=["ALL", "DEFAULT"])
				if response:
					self.rekognitionImgCount += 1

					with self.s3fs.open(image[:-4] + "_rek.json", "w") as s3File:
						imageSuccessCount += 1
						s3File.write(json.dumps(response))
				else:
					print("\nFailed to process the image " + image)

			progressBar.finish()
			print("Successfully processed " + str(imageSuccessCount) + " images")
			return True
		except Exception as e:
			print("\nFailed to process all the images: " + str(e))
			return False

	def __checkDBTables(self):
		""" Checks if the DynamoDB tables exists """
		tables = self.dynamodb.list_tables()
		return tables and tables["TableNames"] and \
			("valltourisminsta" in tables["TableNames"])

	def __createDBTables(self):
		""" Creates the tables for the Instalooter and Rekognition JSON data in
			DynamoDB:
				Instalooter JSON:
					id (same than the file name)
					timestamp
					short code of the instagram post
					image url
					description
					likes count
					comment count
				Rekognition JSON:
					FaceDetails -> array of faces, each one with:
						confidence value
						gender
						age range
						emotions lists and their confidence
						glasses
						sunglasses
						moustache
						beard"""
		try:
			print("Trying to create the tables...")

			# valltourisminsta table
			response = self.dynamodb.create_table(
				TableName="valltourisminsta",
				KeySchema=[
					{
						"AttributeName" : "id",
						"KeyType" : "HASH"  # Partition key
					},
					{
						"AttributeName" : "faceIndex",
						"KeyType" : "RANGE"  # Sort key
					}
				],
				AttributeDefinitions=[
					{
						"AttributeName" : "id",
						"AttributeType" : "S"
					},
					{
						"AttributeName" : "faceIndex",
						"AttributeType" : "N"
					}
				],
				ProvisionedThroughput={
					"ReadCapacityUnits" : 10,
					"WriteCapacityUnits" : 10
				}
			)

			print("DynamoDB valltourisminsta table response: " + str(response))

			print("Successfully created the tables")
			return True
		except Exception as e:
			print("Failed to create tables: " + str(e))
			return False

	def insertDBItems(self):
		"""" Processes the JSONs stored in S3 and inserts their data into
			DynamoDB """
		try:
			print("Trying to insert items into DynamoDB...")

			filenames = self.s3fs.listdir("")
			idsS3 = set(map(lambda x: x[:-4], filter(lambda x: x[-4:] == ".jpg", filenames)))

			scanResponse = self.dynamodb.scan(
				TableName="valltourisminsta",
				ProjectionExpression="id"
			)
			items = scanResponse['Items']
			while ("LastEvaluatedKey" in scanResponse):
				scanResponse = self.dynamodb.scan(
					TableName="valltourisminsta",
					ProjectionExpression="id",
					ExclusiveStartKey=scanResponse['LastEvaluatedKey']
				)
				items = items + scanResponse['Items']
			idsInserted = set(map(lambda x: x["id"]["S"], items))

			idsToInsert = idsS3.difference(idsInserted)
			for id in idsToInsert:
				with self.s3fs.open(id + ".json", "r") as looterFile, \
						self.s3fs.open(id + "_rek.json", "r") as rekognitionFile:
					looterJsonContent = json.loads(looterFile.read())
					rekJsonContent = json.loads(rekognitionFile.read())

					description = ""
					if (len(looterJsonContent["edge_media_to_caption"]["edges"]) > 0):
						description = looterJsonContent["edge_media_to_caption"]["edges"][0]["node"]["text"]

					for iFaceDetails in range(len(rekJsonContent["FaceDetails"])):
						faceDetails = rekJsonContent["FaceDetails"][iFaceDetails]

						emotions = { x["Type"] : x["Confidence"] for x in faceDetails["Emotions"] }

						self.dynamodb.put_item(
							TableName="valltourisminsta",
							Item={
								"id" : { "S" : id },
								"faceIndex" : { "N" : str(iFaceDetails) },
								"dTime" : { "S" : datetime.fromtimestamp(looterJsonContent["taken_at_timestamp"]).isoformat() },
								"shortCode" : { "S" : looterJsonContent["shortcode"] },
								"displayUrl" : { "S" : looterJsonContent["display_url"] },
								"description" : { "S" : description },
								"likesCount" : { "N" : str(looterJsonContent["edge_liked_by"]["count"]) },
								"commentsCount" : { "N" : str(looterJsonContent["edge_media_to_comment"]["count"]) },
								"confidence" : { "N" : str(faceDetails["Confidence"]) },
								"ageLow" : { "N" : str(faceDetails["AgeRange"]["Low"]) },
								"ageHigh" : { "N" : str(faceDetails["AgeRange"]["High"]) },
								"gender" : { "S" : faceDetails["Gender"]["Value"] },
								"eyeglasses" : { "BOOL" : faceDetails["Eyeglasses"]["Value"] == True },
								"sunglasses" : { "BOOL" : faceDetails["Sunglasses"]["Value"] == True },
								"beard" : { "BOOL" : faceDetails["Beard"]["Value"] == True },
								"moustache" : { "BOOL" : faceDetails["Mustache"]["Value"] == True },
								"happyConfidence" : { "N" : str(emotions["HAPPY"]) },
								"surprisedConfidence" : { "N" : str(emotions["SURPRISED"]) },
								"fearConfidence" : { "N" : str(emotions["FEAR"]) },
								"sadConfidence" : { "N" : str(emotions["SAD"]) },
								"angryConfidence" : { "N" : str(emotions["ANGRY"]) },
								"disgustedConfidence" : { "N" : str(emotions["DISGUSTED"]) },
								"confusedConfidence" : { "N" : str(emotions["CONFUSED"]) },
								"calmConfidence" : { "N" : str(emotions["CALM"]) }
							}
						)

						print("Put " + id + "," + str(iFaceDetails) + " in valltourisminsta table")

			print("Successfully put items into DynamoDB")
			return True
		except Exception as e:
			print("Failed to insert items into DynamoDB: " + str(e))
			return False


def main(argv):
	if len(argv) < 2:
		print("Error: usage " + argv[0] + " <hashtag file (one per line)>")
		sys.exit()

	with open(argv[1], "r") as hashtagsFile:
		lines = hashtagsFile.readlines()

		app = App()
		app.awsRegion = "eu-west-1"
		app.awsBucket = "valltourisminstabucket"
		app.instaUser = os.environ.get("INSTA_USER")
		app.instaPass = os.environ.get("INSTA_PASS")
		app.awsAccessKeyId = os.environ.get("AWS_AKEY_ID")
		app.awsAccessKeySecret = os.environ.get("AWS_AKEY_SECRET")
		app.instaMediaLimit = 1000

		if app.connect():
			for iLine in range(len(lines)):
				hashtag = lines[iLine].strip()
				print("=== Processing hashtag " + str(iLine + 1) + "/" + str(len(lines)) + ": #" + hashtag + " ===")
				app.hashtag = hashtag
				app.downloadImages()
				print("=== Processed hashtag #" + hashtag + " ===")

			app.processImages()
			app.insertDBItems()
			app.disconnect()


if __name__ == "__main__":
	main(sys.argv)
