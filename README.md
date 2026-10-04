# YouTube Publishing Agent

A Claude Code agent that takes a raw podcast upload sitting in YouTube as a draft and publishes it: transcript, fact-checked guest research, title, description with chapters, tags, and the switch to public.

I built it for a founder-interview podcast I run, and it has published five consecutive episodes in production. The show-specific details have been replaced with placeholders in this repo.

The agent itself is [`CLAUDE.md`](CLAUDE.md). The Python in `scripts/` is the thin layer of tools it calls.

---

## Why it exists

Publishing an interview by hand is a pile of fiddly work: scrub through the video for chapter points, look up the guest, get their name and company spelled right, write a description that isn't generic, pick tags. None of it is hard. All of it is easy to get slightly wrong.

The step that matters most is the one that's easiest to skip, which is **checking names**. On one episode, the first two sentences of YouTube's auto-generated transcript got the show's name, the guest's name and the company's name all wrong. On another, speech recognition spelled the guest's name three different ways and turned the company into a different word entirely. So the agent is told never to copy a name from the transcript, and to confirm every one against official sources before it reaches the description.

## How it works

```
 draft on YouTube
       │
       ▼
 fetch_transcript.py ──► srt2txt.py          ASR captions → timestamped text
       │
       ▼
 Claude: identify guest → web research → verify spellings
       │
       ▼
 Claude: title, description, chapters, tags  → workdir/metaNNN.py
       │
       ▼
 publish.py ──► videos.update ──► videos.list (fresh read)
                                       │
                                       └─ exits non-zero if not public
```

You start it with `/publish`, or by pasting a draft URL. It handles one video per run.

`examples/meta_example.py` shows the metadata file the agent writes: title, description with chapters, tags. The guest in it is fictional.

## Things that went wrong, and are now handled

These are all baked into `CLAUDE.md` so the agent doesn't rediscover them each run.

**The MCP tool couldn't do the job.** The workflow started on [`youtube-uploader-mcp`](https://github.com/anwerj/youtube-uploader-mcp). It turned out its auth only requests `youtube.upload` and `youtube.readonly`, which can't update an existing video or download captions. Its upload tool also needs a local file, so it can only create new videos, not publish drafts. Both jobs need the `youtube.force-ssl` scope, so `scripts/yt.py` talks to the Data API directly, using only the standard library.

**The API said "public" when it wasn't.** On one episode, the update response reported `privacyStatus: public`, but the video stayed unlisted for two runs before anyone noticed. `publish.py` now always re-reads the video after updating, and treats only that second read as the truth.

**Tokens died every week.** Refresh tokens kept failing with `invalid_grant`. The cause is that a Google Cloud OAuth app in *Testing* status gets 7-day refresh tokens. `auth.py` gets you a new one in a minute, and the permanent fix is publishing the consent screen.

**yt-dlp got rate limited.** Its caption download returns HTTP 429 often enough to be useless, and it can't see drafts anyway. Transcripts come from the Data API's `captions` endpoint now.

**Press and guest disagreed.** On one episode the guest quoted a figure on air that was several times smaller than the one in press coverage. The agent is told to prefer what was said on record, or leave the number out, rather than quietly pick one.

## Setup

You need Python 3, [Claude Code](https://claude.com/claude-code), and a Google Cloud project with the YouTube Data API v3 enabled.

1. In Google Cloud, create an OAuth client (Desktop app). Download its JSON into `workdir/client_secret.json`.
2. Run `python3 scripts/auth.py`, open the URL it prints, approve, and paste back the URL you get redirected to. This writes `workdir/token.json`.
3. Fill in the `<placeholders>` in `CLAUDE.md` with your show's name, title format and description footer. Set `SHOW_BADGE` in `scripts/generate_thumbnail.py` if you want thumbnails.
4. Open the folder in Claude Code and run `/publish`.

Everything in `workdir/` is gitignored: credentials, tokens, transcripts, and per-episode metadata.

The thumbnail scripts need `pip install pillow rembg`. The rest is standard library only.

## Known limitations

- **It's shaped around one kind of show.** The workflow assumes one guest per episode and a numbered title format. A panel show or a solo channel would need `CLAUDE.md` rewritten. The scripts themselves are generic.
- **Finding the draft is left to the agent.** There's no `list_drafts.py`. The YouTube API has no clean "list my drafts" call, and so far Claude works it out each run.
- **Thumbnails are manual.** `generate_thumbnail.py` renders one fixed layout from a background-removed headshot, but the final thumbnail is still chosen and uploaded by hand.
- **The thumbnail fonts are macOS paths.** It falls back to Pillow's default font elsewhere, which looks worse.
- **No automated tests.** Each script was run against the live API (`publish.py` only up to its read-only verification step). The real test is a published episode.
- **`auth.py` needs a manual copy-paste.** It doesn't run a local callback server, so you paste the redirect URL by hand.

## Layout

```
├── CLAUDE.md                 # the agent: workflow, rules, lessons learned
├── .claude/commands/         # /publish and /thumbnail
├── scripts/
│   ├── yt.py                 # token refresh + minimal Data API client
│   ├── auth.py               # one-time OAuth setup (force-ssl scope)
│   ├── fetch_transcript.py   # ASR captions as SRT
│   ├── srt2txt.py            # de-duplicates rolling ASR cues into readable text
│   ├── publish.py            # apply metadata, make public, verify
│   ├── generate_thumbnail.py # thumbnail renderer (one fixed layout)
│   └── remove_bg.py          # headshot background removal (rembg)
└── examples/meta_example.py  # metadata file format (fictional guest)
```

## License

MIT
