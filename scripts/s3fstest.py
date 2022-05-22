#!/usr/bin/env python3

from fs_s3fs import S3FS


awsAccessKeyId = input("AWS Access Key ID: ")
awsAccessKeySecret = input("AWS Access Key Secret: ")

s3fs = S3FS(
    bucket_name="valltourisminstabucket",
    aws_access_key_id=awsAccessKeyId,
    aws_secret_access_key=awsAccessKeySecret
)

source_file_name = "happy.jpg"
destination_blob_name = source_file_name

with open(source_file_name, "rb") as local_file:
    with s3fs.open(destination_blob_name, "wb") as gcs_file:
        gcs_file.write(local_file.read())

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)
