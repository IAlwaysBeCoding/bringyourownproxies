import InjectorHttpConnection

import requests
print requests.get('http://www.google.com')
r = requests.post('https://www.google.com',data={'lol':'dfd','dfd':'dd'})
print r.request.headers
