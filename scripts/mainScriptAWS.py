#!/usr/bin/env python3

import json
import boto3
from instalooter.looters import HashtagLooter
from instalooter.pbar import ProgressBar
from fs_s3fs import S3FS
from fs import errors
import sys


class InstaProgressBar(ProgressBar):
    def __init__(self, it, *args, **kwargs):
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
        print("\r\033[KDownloaded:\t" + str(self.count) + "/" + str(self.maximum)
            + "\t" + '{:.3f}'.format(perc) + "%", end="")


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

    def run(self):
        """ Downloads, stores and processes images with the requested
            hashtag """
        self.connectS3FS()
        self.storeImages()
        self.processImages()

    def connectS3FS(self):
        """ Connect to S3 storage """
        try:
            print("Trying to connect to " + self.awsBucket + "...")

            self.s3fs = S3FS(
                bucket_name=self.awsBucket,
                region=self.awsRegion,
                aws_access_key_id=self.awsAccessKeyId,
                aws_secret_access_key=self.awsAccessKeySecret
            )

            print("Successfully connected to " + self.awsBucket)
            return True
        except Exception as e:
            print("Failed to connect with AWS S3: " + str(e))
            return False

    def storeImages(self):
        """ Retrieve images and json from instagram and store them in S3 """
        try:
            print("Trying to connect to Instagram...")

            looter = HashtagLooter(self.hashtag, dump_json=True, jobs=12)
            looter.login(self.instaUser, self.instaPass)

            print("Logged in? " + str(looter.logged_in()))
            mediaCount = looter.download_pictures(
                self.s3fs, media_count=self.instaMediaLimit, new_only=True,
                dlpbar_cls=InstaProgressBar)

            looter.logout()

            print("Successfully downloaded from Instagram " + str(mediaCount) + " pictures")
            return True
        except Exception as e:
            print("Failed to download all the pictures: " + str(e))
            if (looter.logged_in()):
                looter.logout()
            return False

    def processImages(self):
        """ Process images with Rekognition and store them in S3 """
        try:
            print("Trying to connect with Rekognition...")

            rekognition_client = boto3.client(
                service_name="rekognition",
                region_name=self.awsRegion,
                aws_access_key_id = self.awsAccessKeyId,
                aws_secret_access_key = self.awsAccessKeySecret
            )

            # Note: images that were download prior to the current run
            # but failed to retrieve its Rekognition JSON can also be
            # processed in this step
            filenames = self.s3fs.listdir("")
            imagesToProcess = list(filter(lambda x: x[-4:] == ".jpg" and not self.s3fs.exists(x[:-4] + "_rek.json"), filenames))
            imageCount = 0
            imageSuccessCount = 0

            for image in imagesToProcess:
                imageCount += 1

                perc = 100.0 * imageCount / float(len(imagesToProcess))
                print("\r\033[KRekognition:\t" + str(imageCount) + "/" + str(len(imagesToProcess))
                    + "\t" + '{:.3f}'.format(perc) + "%", end="")

                response = rekognition_client.detect_faces(
                    Image={"S3Object": {"Bucket": self.awsBucket, "Name": image}},
                    Attributes=["ALL", "DEFAULT"])
                if response:
                    with self.s3fs.open(image[:-4] + "_rek.json", "w") as gcs_file:
                        imageSuccessCount += 1
                        gcs_file.write(json.dumps(response))
                else:
                    print("\nFailed to process the image " + image)

            print("\nSuccessfully proccessed " + str(imageSuccessCount) + " images")
            return True
        except Exception as e:
            print("\nFailed to process all the pictures: " + str(e))
            return False


def main(argv):
    if len(argv) < 2:
        print("Error: usage " + argv[0] + " <hashtag>")
        sys.exit()

    app = App()
    app.awsRegion = "eu-west-1"
    app.awsBucket = "valltourisminstabucket"
    app.instaUser = input("Instagram User: ")
    app.instaPass = input("Instagram Password: ")
    app.awsAccessKeyId = input("AWS Access Key ID: ")
    app.awsAccessKeySecret = input("AWS Access Key Secret: ")
    app.hashtag = argv[1]
    app.instaMediaLimit = 50
    app.run()


if __name__ == "__main__":
	main(sys.argv)
