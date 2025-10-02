import json
from urllib import request, parse, error

BASE = 'http://127.0.0.1:8000'


def http_get(path):
    url = BASE + path
    try:
        with request.urlopen(url) as r:
            return r.getcode(), json.loads(r.read().decode())
    except error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def http_post(path, data):
    url = BASE + path
    body = json.dumps(data).encode()
    req = request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with request.urlopen(req) as r:
            return r.getcode(), json.loads(r.read().decode())
    except error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def http_put(path, data):
    url = BASE + path
    body = json.dumps(data).encode()
    req = request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='PUT')
    try:
        with request.urlopen(req) as r:
            return r.getcode(), json.loads(r.read().decode())
    except error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def test_settings(key):
    print('\n== Settings test ==')
    print('Upserting setting', key)
    code, body = http_put('/api/settings/upsert/', {'key': key, 'value': {'test': True}})
    print('PUT /api/settings/upsert/ ->', code, body)

    print('Listing by key')
    code, body = http_get(f'/api/settings/?key={parse.quote(key)}')
    print('GET /api/settings/?key= ->', code, body)


def test_uistate(key):
    print('\n== UIState test ==')
    print('Posting UIState (upsert)')
    code, body = http_post('/api/ui-state/upsert/', {'key': key, 'state': {'cursor': 1}})
    print('POST /api/ui-state/upsert/ ->', code, body)

    print('Listing UIState by key')
    code, body = http_get(f'/api/ui-state/?key={parse.quote(key)}')
    print('GET /api/ui-state/?key= ->', code, body)


def test_lessons():
    print('\n== Lessons test ==')
    code, body = http_get('/api/lessons/')
    print('GET /api/lessons/ ->', code)
    if isinstance(body, list):
        print('Found', len(body), 'lessons; first item keys:', list(body[0].keys()) if body else [])
    else:
        print(body)


def test_todos():
    print('\n== Todos test ==')
    code, body = http_get('/api/todos/')
    print('GET /api/todos/ ->', code)
    if isinstance(body, list):
        print('Found', len(body), 'todos')
    else:
        print(body)

 
def main():
    print('Running basic API integration tests against', BASE)
    test_settings('demo.setting')
    test_uistate('ui.demo')
    test_lessons()
    test_todos()

if __name__ == '__main__':
    main()
