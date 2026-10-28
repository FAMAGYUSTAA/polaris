import urllib.request, urllib.parse, json

def req(url, data=None, headers=None):
    if headers is None: headers = {}
    r = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None, headers=headers)
    try: return json.loads(urllib.request.urlopen(r).read())
    except urllib.error.HTTPError as e: return {'error': e.code}

hq = req('http://127.0.0.1:8000/api/auth/login', {'username': 'hq_operator', 'password': 'hq_password', 'grant_type': 'password'})
print('HQ Login:', hq)

st = req('http://127.0.0.1:8000/api/auth/login', {'username': 'bharati_operator', 'password': 'bharati_password', 'grant_type': 'password'})
print('Station Login:', st)

hq_headers = {'Authorization': 'Bearer ' + hq['access_token'], 'Content-Type': 'application/json'}
st_headers = {'Authorization': 'Bearer ' + st['access_token'], 'Content-Type': 'application/json'}

try: 
    urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/sync/delta', data=b'{"events":[]}', headers=hq_headers))
    print('Sync HQ: Success (Wait, HQ should be denied? Actually my dependencies check only STATION role for delta... wait, I need to check my dependencies.py)')
except urllib.error.HTTPError as e: print('Sync HQ Error:', e.code)

try: 
    urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/directives', data=b'{"station_id":"BHARATI","message":"test","issued_by":"hq"}', headers=st_headers))
    print('Directive ST: Success (BAD)')
except urllib.error.HTTPError as e: print('Directive ST Error:', e.code)

try: 
    r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/sync/delta', data=b'{"events":[]}', headers=st_headers))
    print('Sync ST Status:', json.loads(r.read())['status'])
except urllib.error.HTTPError as e: print('Sync ST Error:', e.code, e.read())
