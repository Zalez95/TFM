from fs_gcsfs import GCSFS

gcsfs = GCSFS(bucket_name="indigo-pod-344620")

source_file_name = "happy.jpg"
destination_blob_name = source_file_name

with open(source_file_name, "rb") as local_file:
    with gcsfs.open(destination_blob_name, "wb") as gcs_file:
        gcs_file.write(local_file.read())

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)
