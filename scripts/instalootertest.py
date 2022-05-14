#!/usr/bin/env python3

from instalooter.looters import HashtagLooter
from instalooter.looters import ProfileLooter
from instalooter.pbar import ProgressBar
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
    if len(argv) < 3:
        print("Error: usage " + argv[0] + " <-h(ashtag)|-p(rofile)> <name>")
        sys.exit()

    user = input("User: ")
    password = input("Password: ")
    option = argv[1]
    name = argv[2]

    if (option == "-h"):
        try:
            looter = HashtagLooter(name, jobs=12)
            looter.login(user, password)

            print("Logged in? " + str(looter.logged_in()))
            mediaCount = looter.download_pictures(
                './output', media_count=50, new_only=True, dlpbar_cls=InstaProgressBar)
            print("Finished! Downloaded " + str(mediaCount) + " pictures")

            looter.logout()
        except (SystemError, ValueError, IOError):
            print("Failed to connect with Instagram")
            if (looter.logged_in()):
                looter.logout()
    elif (option == "-p"):
        try:
            looter = ProfileLooter(name, jobs=12)
            looter.login(user, password)

            print("Logged in? " + str(looter.logged_in()))
            mediaCount = looter.download_pictures(
                './output', media_count=50, new_only=True, dlpbar_cls=InstaProgressBar)
            print("Finished! Downloaded " + str(mediaCount) + " pictures")

            looter.logout()
        except (SystemError, ValueError, IOError):
            print("Failed to connect with Instagram")
            if (looter.logged_in()):
                looter.logout()
    else:
        print("Error: Wrong argument: " + option)


if __name__ == "__main__":
    main(sys.argv)
