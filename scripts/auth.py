#!/usr/bin/env python3
"""One-time OAuth setup: turns a Google client secret into workdir/token.json.

Usage:
    1. Download your OAuth client JSON from Google Cloud and save it as
       workdir/client_secret.json
    2. python3 scripts/auth.py
    3. Open the printed URL, approve, then paste back the URL your browser
       was redirected to (the page itself will fail to load; that's expected).
"""

import glob
import json
import os
import sys
import urllib.parse
import urllib.request

from yt import TOKFILE, WORKDIR

# force-ssl is the only scope that covers both videos.update (publishing an
# existing draft) and captions.download. youtube.upload cannot do either.
SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'


def load_client():
    matches = glob.glob(os.path.join(WORKDIR, 'client_secret*.json'))
    if not matches:
        raise SystemExit(f'No client_secret*.json found in {WORKDIR}')
    with open(matches[0]) as f:
        data = json.load(f)
    # Google ships "installed" for desktop clients and "web" for web clients.
    return data.get('installed') or data['web']


def consent_url(client):
    params = {
        'client_id': client['client_id'],
        'redirect_uri': client['redirect_uris'][0],
        'response_type': 'code',
        'access_type': 'offline',
        # Without prompt=consent Google omits the refresh_token on re-auth.
        'prompt': 'consent',
        'scope': SCOPE,
    }
    return client['auth_uri'] + '?' + urllib.parse.urlencode(params)


def exchange_code(client, code):
    body = urllib.parse.urlencode({
        'code': code,
        'client_id': client['client_id'],
        'client_secret': client['client_secret'],
        'redirect_uri': client['redirect_uris'][0],
        'grant_type': 'authorization_code',
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(client['token_uri'], data=body)) as r:
        return json.load(r)


def main():
    client = load_client()
    print('Open this URL and approve access:\n')
    print(consent_url(client))
    redirected = input('\nPaste the full URL you were redirected to: ').strip()
    code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query).get('code')
    if not code:
        sys.exit('No ?code= in that URL. Copy it from the address bar after approving.')

    tokens = exchange_code(client, code[0])
    if 'refresh_token' not in tokens:
        sys.exit('Google returned no refresh_token. Revoke the app at '
                 'myaccount.google.com/permissions and run this again.')

    os.makedirs(WORKDIR, exist_ok=True)
    with open(TOKFILE, 'w') as f:
        json.dump({
            'token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'token_uri': client['token_uri'],
            'client_id': client['client_id'],
            'client_secret': client['client_secret'],
            'scopes': [SCOPE],
        }, f)
    os.chmod(TOKFILE, 0o600)
    print(f'Saved {TOKFILE}')


if __name__ == '__main__':
    main()
