import json, os, urllib.request, urllib.parse

# Credentials live in workdir/, which is gitignored. scripts/auth.py creates this file.
WORKDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workdir')
TOKFILE = os.path.join(WORKDIR, 'token.json')

def _load():
    if not os.path.exists(TOKFILE):
        raise SystemExit(f'No token at {TOKFILE}. Run scripts/auth.py first.')
    with open(TOKFILE) as f:
        return json.load(f)

def refresh():
    d = _load()
    body = urllib.parse.urlencode({
        'client_id': d['client_id'],
        'client_secret': d['client_secret'],
        'refresh_token': d['refresh_token'],
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request(d['token_uri'], data=body)
    with urllib.request.urlopen(req) as r:
        new = json.load(r)
    d['token'] = new['access_token']
    with open(TOKFILE, 'w') as f:
        json.dump(d, f)
    return d['token']

def token():
    return _load()['token']

def api(path, params=None, method='GET', body=None, tok=None, raw=False):
    url = 'https://www.googleapis.com/youtube/v3/' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', 'Bearer ' + (tok or token()))
    if data:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        payload = r.read()
    return payload if raw else json.loads(payload)
