from google.cloud import storage

source_file_name = "happy.jpg"
destination_blob_name = source_file_name

storage_client = storage.Client()
bucket = storage_client.bucket("indigo-pod-344620")
blob = bucket.blob(destination_blob_name)

blob.upload_from_filename(source_file_name)

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)

