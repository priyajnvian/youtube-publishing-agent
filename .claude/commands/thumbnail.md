Generate a YouTube thumbnail for a podcast episode.

Steps:
1. Find and verify the guest's headshot from an official source (company site, LinkedIn, press kit)
2. Remove background from headshot: `python3 scripts/remove_bg.py workdir/headshot.jpg`
3. Render the thumbnail:
   `python3 scripts/generate_thumbnail.py --name "..." --designation "..." --company "..." --headshot workdir/headshot_nobg.png --output workdir/thumbnail.jpg`
   (orange layout with the show badge from SHOW_BADGE, guest name in large chalk-style text, designation and company at bottom, headshot on the right)
4. Show the user the result. Thumbnail upload stays manual.

Guest info: $ARGUMENTS
