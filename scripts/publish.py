#!/usr/bin/env python3
"""Apply metadata to an existing YouTube draft and make it public.

Usage:
    python3 scripts/publish.py workdir/meta551.py

The metadata file defines VIDEO_ID, TITLE, DESCRIPTION, TAGS and CATEGORY_ID.
See examples/meta550.py.
"""

import importlib.util
import sys

import yt


def load_metadata(path):
    spec = importlib.util.spec_from_file_location('meta', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fetch_video(video_id):
    items = yt.api('videos', {'part': 'snippet,status', 'id': video_id})['items']
    if not items:
        sys.exit(f'Video {video_id} not found on the authenticated channel.')
    return items[0]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    m = load_metadata(sys.argv[1])
    yt.refresh()

    current = fetch_video(m.VIDEO_ID)
    snippet, status = current['snippet'], current['status']
    snippet.update({
        'title': m.TITLE,
        'description': m.DESCRIPTION,
        'tags': m.TAGS,
        'categoryId': m.CATEGORY_ID,
        'defaultLanguage': 'en',
    })
    body = {
        'id': m.VIDEO_ID,
        'snippet': snippet,
        # videos.update replaces the whole status part, so carry over the
        # fields we aren't changing or they silently reset to defaults.
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
            'embeddable': status.get('embeddable', True),
            'license': status.get('license', 'youtube'),
            'publicStatsViewable': status.get('publicStatsViewable', True),
        },
    }
    yt.api('videos', {'part': 'snippet,status'}, method='PUT', body=body)

    # The update response has claimed "public" while the video stayed
    # unlisted (this happened in production). Only a fresh read is trustworthy.
    after = fetch_video(m.VIDEO_ID)
    privacy = after['status']['privacyStatus']
    print('title  :', after['snippet']['title'])
    print('privacy:', privacy)
    print('url    : https://youtu.be/' + m.VIDEO_ID)
    if privacy != 'public':
        sys.exit('Video is NOT public after update. Check it in YouTube Studio.')


if __name__ == '__main__':
    main()
