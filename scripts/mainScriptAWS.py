#!/usr/bin/env python3

import json
import boto3
from instalooter.looters import HashtagLooter
from instalooter.pbar import ProgressBar
from fs_s3fs import S3FS
from fs import errors
import sys


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
    looterSession = None
    rekognition = None

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

        return True

    def disconnect(self):
        looter = HashtagLooter(hashtag="", session=self.looterSession)
        looter.logout()

        self.rekognition = None
        self.looterSession = None
        self.s3fs = None

    def run(self):
        """ Downloads, stores and processes images with the requested
            hashtag """
        return self.__storeImages() and self.__processImages()

    def __storeImages(self):
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

    def __processImages(self):
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

                response = self.rekognition.detect_faces(
                    Image={"S3Object": {"Bucket": self.awsBucket, "Name": image}},
                    Attributes=["ALL", "DEFAULT"])
                if response:
                    with self.s3fs.open(image[:-4] + "_rek.json", "w") as gcs_file:
                        imageSuccessCount += 1
                        gcs_file.write(json.dumps(response))
                else:
                    print("\nFailed to process the image " + image)

            progressBar.finish()
            print("Successfully proccessed " + str(imageSuccessCount) + " images")
            return True
        except Exception as e:
            print("\nFailed to process all the images: " + str(e))
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
        app.instaUser = input("Instagram User: ")
        app.instaPass = input("Instagram Password: ")
        app.awsAccessKeyId = input("AWS Access Key ID: ")
        app.awsAccessKeySecret = input("AWS Access Key Secret: ")
        app.instaMediaLimit = 50

        if app.connect():
            for iLine in range(len(lines)):
                hashtag = lines[iLine].strip()
                print("=== Processing hashtag " + str(iLine + 1) + "/" + str(len(lines)) + ": #" + hashtag + " ===")
                app.hashtag = hashtag
                app.run()
                print("=== Processed hashtag #" + hashtag + " ===")

            app.disconnect()


if __name__ == "__main__":
	main(sys.argv)
