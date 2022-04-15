#!/usr/bin/env python3

from instalooter.looters import HashtagLooter
import sys

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

    user = argv[1]
    password = argv[2]
    hashtag = argv[3]

    looter = HashtagLooter(hashtag, jobs=12)
    looter.login(user, password)
    looter.download_pictures('./output', media_count=50, new_only=True)

    with open(hashtag + ".txt", "w") as f:
        for media in looter.medias():
            for link in links(media, looter):
                f.write("{}\n".format(link))

    looter.logout()


if __name__ == "__main__":
    main(sys.argv)
