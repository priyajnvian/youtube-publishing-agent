# YouTube Publishing Agent

## Project Overview
This agent publishes draft YouTube videos for a founder-interview podcast channel.
Fill in your own show's details below; everything in `<angle brackets>` is a placeholder.
- **Show**: <Show Name> (short prefix used in titles: `<SHOW>`)
- **Channel**: <@your-channel-handle>
- **Website**: <https://your-show.example>

## Quick Start
When the user says "go" or pastes a YouTube draft URL, execute the full publish workflow below.
Run all scripts from the repo root. Per-run files (transcripts, metadata) go in `workdir/`, which is gitignored.

---

## Full Publish Workflow

### Step 1: Identify the Draft Video
- List private/unlisted videos on the channel with `yt.api('search', ...)` / `yt.api('videos', ...)` or the MCP `channels` tool
- Pick the **first (oldest/top) draft** video unless user specifies otherwise
- Note the video ID, current title (if any), and duration

### Step 2: Read the Auto-Generated Transcript
```bash
python3 scripts/fetch_transcript.py VIDEO_ID workdir/transcriptNNN.srt
python3 scripts/srt2txt.py workdir/transcriptNNN.srt workdir/transcriptNNN.txt
```
The `.txt` has `[mm:ss]` stamps every ~30 words, which is what you use for chapters.

### Step 3: Research the Spokesperson & Company
- From the transcript, identify the guest's **full name**, **designation**, and **company name**
- **Expect the transcript to mangle names.** YouTube ASR routinely gets guest and company names wrong, sometimes differently each time they're said. Never copy a name from the transcript into metadata without verifying it.
- Do web research to gather:
  - Brief bio of the person (role, background, achievements)
  - Company overview (what it does, industry, funding, key facts)
  - Any recent news or milestones
- Cross-verify spellings of names and company from official sources
- If the guest's on-record numbers disagree with press coverage, prefer what they said in the episode, or leave the number out. Don't silently pick one.

### Step 4: Write Title & Description

#### Title Format
The title follows one of these patterns (refer to recent episodes for style):
```
<SHOW> - [NUMBER] | [Catchy Hook/Title] | [Person Name] ([Company])
<SHOW> - [NUMBER] | [Person Name] ([Designation], [Company]) - [Short Description]
```

**Examples (replace with titles from your own published videos):**
- `SHOW - 101 | Selling Software to Schools Without Burning Out | Jane Example (Acme Labs)`
- `SHOW - 102 | Why We Fired Our Agency | John Sample (Sample & Co)`

**Rules:**
- Always start with `<SHOW> - [NUMBER]`
- Title should be compelling, clickbait-friendly but honest
- Include the person's name and company
- Keep under 100 characters if possible

#### Description Format
```
[1-2 sentence intro about who the guest is and what the episode covers]

[Brief paragraph about the person/company - 2-3 sentences]

Chapters:
00:00 - Introduction
[timestamps from transcript with chapter titles]

---
About <Show Name>:
<One or two lines about your show.>

Website: <https://your-show.example>
```

### Step 5: Generate Tags
Generate 15-20 relevant tags including:
- Guest name, company name
- Industry keywords
- Your show name, plus "founder interview", "startup podcast"
- Relevant topic keywords from the conversation

### Step 6: Publish Video
Write the metadata to `workdir/metaNNN.py` (same shape as `examples/meta_example.py`), then:
```bash
python3 scripts/publish.py workdir/metaNNN.py
```
- Category: `22` People & Blogs, `24` Entertainment, `27` Education. Pick the most relevant.
- **Note**: Thumbnail is handled manually by the user. Skip thumbnail generation/upload.

### Step 7: Post-Publish Verification
- `publish.py` re-reads the video after updating and exits non-zero if it isn't public. Trust that read, not the update response.
- Report the video URL to the user

---

## Important Notes

- **One video per iteration**: Only process the topmost draft video unless told otherwise
- **Always verify facts**: Cross-check names, titles, company info with web search before publishing
- **Transcript is king**: Base all content on what's actually discussed in the video
- **Episode numbering**: Get the latest number from the public channel listing:
  `yt-dlp --flat-playlist --playlist-end 5 --print "%(title)s" https://www.youtube.com/<@your-channel-handle>/videos`
  An unlisted episode won't appear there, so a gap in the numbers can mean an episode is stuck unlisted.

## OAuth — read this before debugging auth
- Required scope is **`https://www.googleapis.com/auth/youtube.force-ssl`**. It covers both
  `videos.update` (publishing a draft) and `captions.download` (transcript). `scripts/auth.py` requests it.
- `mcp__youtube-uploader__authenticate` only requests `youtube.upload` + `youtube.readonly`,
  which **cannot** publish an existing draft or read captions. Don't use it for this workflow.
- `mcp__youtube-uploader__upload_video` requires a `file_path` and only does new uploads.
  To publish an existing draft, use `scripts/publish.py`.
- If refresh tokens keep dying with `invalid_grant`, the Google Cloud consent screen is in
  **Testing** status (7-day token expiry). Re-run `scripts/auth.py`, or publish the app to fix permanently.
- **Always re-read the video with `videos.list` after `videos.update`.** The update response can
  report `public` while the video stays unlisted. This happened in production, and the episode
  sat unlisted for two runs before anyone noticed.

## Tools
- `scripts/yt.py` — token refresh + minimal YouTube Data API client (stdlib only)
- `scripts/fetch_transcript.py` — ASR captions as SRT via the Data API
- `scripts/srt2txt.py` — flattens rolling ASR cues into timestamped plain text
- `scripts/publish.py` — applies metadata, makes public, verifies with a fresh read
- **yt-dlp** — episode numbering only. Its caption download hits HTTP 429; don't rely on it.
- MCP server [`youtube-uploader-mcp`](https://github.com/anwerj/youtube-uploader-mcp) — optional, for listing channels

## Project Structure
```
├── CLAUDE.md                  # This file - main instructions
├── .claude/commands/          # /publish and /thumbnail slash commands
├── scripts/                   # Data API client and workflow steps
├── examples/meta_example.py   # Metadata file format (fictional guest)
└── workdir/                   # gitignored: client secret, token, transcripts, metadata
```
