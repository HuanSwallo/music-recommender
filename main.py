import os
import requests
import cloudscraper
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from albumoftheyearapi import AOTY

load_dotenv()

api_key = os.getenv('LASTFM_API_KEY')

def get_top_artists():
    params = {
        "method": "user.getTopArtists",
        "user": "TinyTanBoi",
        "api_key": api_key,
        "format": "json"
    }

    response = requests.get('http://ws.audioscrobbler.com/2.0/' , params=params)
    response.raise_for_status()
    data = response.json()
    return [artist['name'] for artist in data['topartists']['artist'][:5]]

def get_artist_id(artist_name, scraper):
    search_name = artist_name.lower().replace(' ', '+')
    url = f'https://www.albumoftheyear.org/search/artists/?q={search_name}'
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    artist_link = soup.find('a', href=lambda h: h and '/artist/' in h)
    if not artist_link:
        print(f"Could not find artist {artist_name} in search results")
        return None
    return artist_link['href'].split('/artist/')[1].strip('/')


client = AOTY()
scraper = cloudscraper.create_scraper()

top_artists = get_top_artists()

for artist_name in top_artists:
    print(f"\n🎤 {artist_name}")
    artist_id = get_artist_id(artist_name, scraper)
    if not artist_id:
        print("  Could not find artist on AOTY")
        continue
    albums = client.artist_albums(artist_id)
    if not albums:
        print("  No albums found")
        continue
    print("  Recommended albums:")
    for album in albums[:3]:
        print(f"  - {album}")