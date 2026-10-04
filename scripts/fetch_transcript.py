#!/usr/bin/env python3
"""Download YouTube's auto-generated (ASR) captions for a video as SRT.

Usage:
    python3 scripts/fetch_transcript.py VIDEO_ID workdir/transcript.srt

Then flatten it for reading with:
    python3 scripts/srt2txt.py workdir/transcript.srt workdir/transcript.txt

Uses the Data API rather than yt-dlp, because yt-dlp's caption download
gets rate limited (HTTP 429) and drafts aren't publicly reachable anyway.
"""

import sys

import yt


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    video_id, out_path = sys.argv[1], sys.argv[2]
    yt.refresh()

    tracks = yt.api('captions', {'part': 'snippet', 'videoId': video_id})['items']
    asr = [t for t in tracks if t['snippet']['trackKind'] == 'asr']
    if not asr:
        sys.exit(f'No auto-generated captions yet for {video_id}. '
                 'YouTube can take a while after upload.')

    srt = yt.api('captions/' + asr[0]['id'], {'tfmt': 'srt'}, raw=True)
    with open(out_path, 'wb') as f:
        f.write(srt)
    print(f'Saved {out_path} ({len(srt)} bytes)')


if __name__ == '__main__':
    main()
