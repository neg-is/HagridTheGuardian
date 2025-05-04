import requests

url = 'https://id.twitch.tv/oauth2/token'
params = {
    'client_id': '5dm95j6ug2qd48c08l1oya1byre0l5',
    'client_secret': 'gcuvm0ympcnrs7f5np3jf3tp8d7a5s',
    'code': 'xr71wa8ybrei8y6c8e1yr3r5vopxb5',
    'grant_type': 'authorization_code',
    'redirect_uri': 'https://twitchtokengenerator.com/redirect'
}

response = requests.post(url, params)
data = response.json()
print(data)

# You will get:
# {
#   "access_token": "...",
#   "refresh_token": "...",
#   "expires_in": 12345,
#   "scope": [...]
# }
