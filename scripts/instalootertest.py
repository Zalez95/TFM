#!/usr/bin/env python3

from instalooter.looters import HashtagLooter

def links(media, looter):
    if media.get('__typename') == "GraphSidecar":
        media = looter.get_post_info(media['shortcode'])
        nodes = [e['node'] for e in media['edge_sidecar_to_children']['edges']]
        return [n.get('video_url') or n.get('display_url') for n in nodes]
    elif media['is_video']:
        media = looter.get_post_info(media['shortcode'])
        return [media['video_url']]
    else:
        return [media['display_url']]

looter = HashtagLooter("mane6")
looter.download('./output', media_count=50)

with open("mane6.txt", "w") as f:
    for media in looter.medias():
        for link in links(media, looter):
            f.write("{}\n".format(link))

