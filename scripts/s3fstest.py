#!/usr/bin/env python3

import sys
from fs_s3fs import S3FS


def main(argv):
	if len(argv) < 2:
		print("Error: usage " + argv[0] + " <file>")
		sys.exit()

	awsAccessKeyId = input("AWS Access Key ID: ")
	awsAccessKeySecret = input("AWS Access Key Secret: ")

	source_file_name = argv[1]
	destination_blob_name = source_file_name

	try:
		s3fs = S3FS(
			bucket_name="valltourisminstabucket",
			aws_access_key_id=awsAccessKeyId,
			aws_secret_access_key=awsAccessKeySecret
		)

		with open(source_file_name, "rb") as local_file:
			with s3fs.open(destination_blob_name, "wb") as s3File:
				s3File.write(local_file.read())

		print(
			"File {} uploaded to {}.".format(
				source_file_name, destination_blob_name
			)
		)
	except Exception as e:
		print("Failed to upload " + source_file_name + ": " + str(e))


if __name__ == "__main__":
	main(sys.argv)
