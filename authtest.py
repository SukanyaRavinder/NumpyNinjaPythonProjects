import requests

url = 'https://covidfacts.in'
myobj = {'somekey': 'somevalue'}

#use the 'auth' parameter to send requests with HTTP Basic Auth:
x = requests.post(url, data = myobj, auth = ('user', 'pass'))

print(x.status_code)