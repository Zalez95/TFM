#!/usr/bin/env python3

from instalooter.looters import HashtagLooter
from google.cloud import storage
from google.cloud import vision
import sys
import os

def links(media, looter):
	if media.get('__typename') == "GraphSidecar":
		media = looter.get_post_info(media['shortcode'])
		nodes = [e['node'] for e in media['edge_sidecar_to_children']['edges']]
		return [n.get('display_url') for n in nodes]
	else:
		return [media['display_url']]


def main(argv):
	if len(argv) < 4:
		print("Error: usage " + argv[0] + " <user> <pass> <hashtag>")
		sys.exit()

	directory = './output/'
	user = argv[1]
	password = argv[2]
	hashtag = argv[3]

	looter = HashtagLooter(hashtag, jobs=12)
	looter.login(user, password)
	looter.download_pictures(directory, media_count=50, new_only=True)

	with open(hashtag + ".txt", "w") as f:
		for media in looter.medias():
			for link in links(media, looter):
				f.write("{}\n".format(link))

	looter.logout()

	storage_client = storage.Client()
	bucket = storage_client.bucket("indigo-pod-344620")
	for filename in os.listdir(directory):
		source_file_name = directory + filename
		destination_blob_name = filename
		blob = bucket.blob(destination_blob_name)
		blob.upload_from_filename(source_file_name)

	image_client = vision.ImageAnnotatorClient()
	for filename in os.listdir(directory):
		response = image_client.annotate_image({
			'image': {'source': {'image_uri': 'gs://indigo-pod-344620/' + filename}},
			'features': [{'type_': vision.Feature.Type.FACE_DETECTION}]
		})

		print(filename + ": " + str(response))


if __name__ == "__main__":
	main(sys.argv)
