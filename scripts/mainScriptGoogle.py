#!/usr/bin/env python3

from google.cloud import vision
from instalooter.looters import HashtagLooter
from instalooter.pbar import ProgressBar
from fs_gcsfs import GCSFS
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


def main(argv):
    if len(argv) < 2:
        print("Error: usage " + argv[0] + " <hashtag>")
        sys.exit()

    user = input("User: ")
    password = input("Password: ")
    hashtag = argv[1]

    gcsfs = None
    try:
        gcsfs = GCSFS(bucket_name="indigo-pod-344620")
    except errors.CreateFailed:
        print("Failed to connect with Cloud Storage")
        return

    try:
        looter = HashtagLooter(hashtag, jobs=12)
        looter.login(user, password)

        print("Logged in? " + str(looter.logged_in()))
        mediaCount = looter.download_pictures(
            gcsfs, media_count=50, new_only=True, dlpbar_cls=InstaProgressBar)
        print("Finished! Downloaded " + str(mediaCount) + " pictures")

        looter.logout()
    except (SystemError, ValueError, IOError):
        print("Failed to connect with Instagram")
        if (looter.logged_in()):
            looter.logout()
        return

    image_client = vision.ImageAnnotatorClient()
    for filename in gcsfs.listdir(""):
        response = image_client.annotate_image({
            'image': {'source': {'image_uri': 'gs://indigo-pod-344620/' + filename}},
            'features': [
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                {'type_': vision.Feature.Type.FACE_DETECTION}
            ]
        })

        print(filename + ": " + str(response))


if __name__ == "__main__":
	main(sys.argv)
