import requests

# Replace with your actual API key and a valid Last.fm username
API_KEY = '60eb4d86490197be705d8ce41e95dd67'
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

params = {

    "method": "user.getTopArtists",
    "user": "TinyTanBoi",
    "api_key": API_KEY,
    "format": "json"
}

response = requests.get(BASE_URL, params=params)
response.raise_for_status()
data = response.json()

for artist in data['topartists']['artist'][:5]:
    print(f"Artist: {artist['name']}, Playcount: {artist['playcount']}")

