#!/usr/bin/env python3

from importlib.metadata import metadata
from pprint import pprint
import instagram_scraper
import sys

def main(argv):
    if len(argv) < 3:
        print("Error: usage " + argv[0] + " <-h(ashtag)|-p(rofile)> <name> <-m(optional, metadata)>")
        sys.exit()

    option1 = argv[1]
    name = argv[2]
    metadata = False
    if (len(argv) > 3) and (argv[3] == "-j"):
        metadata = True

    user = input("User: ")
    password = input("Password: ")
    instaScraper = instagram_scraper.InstagramScraper(
        login_user=user, login_pass=password, destination="./output", maximum=50,
        media_metadata=metadata, profile_metadata=metadata, latest=True,
        location=metadata, include_location=metadata, media_types=["image"]
    )
    instaScraper.authenticate_with_login()
    print("Logged in? " + str(instaScraper.logged_in))

    if (option1 == "-h"):
        try:
            media = []
            for item in instaScraper.query_hashtag_gen(hashtag=name):
                media.append(item)
            print(media)
        except Exception as e:
            print(str(e))
    elif (option1 == "-p"):
        try:
            userMetadata = instaScraper.get_shared_data_userinfo(username=name)
            print(userMetadata)

            media = []
            for item in instaScraper.query_media_gen(user=name):
                media.append(item)
            print(media)
        except Exception as e:
            print(str(e))
    else:
        print("Error: Wrong argument: " + option1)

    instaScraper.logout()


if __name__ == "__main__":
    main(sys.argv)
