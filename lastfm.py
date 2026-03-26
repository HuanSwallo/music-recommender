import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('LASTFM_API_KEY')

def lastfm_getter(method, **params):
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params= {
        "method": method,
        "api_key": api_key,
        "format": "json",
        **params
    })
    response.raise_for_status()
    return response.json()

def get_top_artists(user):
    data = lastfm_getter("user.getTopArtists", user=user, limit=20)
    artists = data['topartists']['artist']
    return [artist['name'] for artist in artists]

def get_heard_albums(user):
    heard = set()

    # Get top albums
    data = lastfm_getter("user.getTopAlbums", user=user, limit=1000)
    for album in data['topalbums']['album']:
        heard.add(f"{album['artist']['name'].lower()} - {album['name'].lower()}")

    # Get recent tracks
    data = lastfm_getter("user.getRecentTracks", user=user, limit=200)
    for track in data['recenttracks']['track']:
        heard.add(f"{track['artist']['#text'].lower()} - {track['album']['#text'].lower()}")

    return heard

def display_summary(username):
    """Print a summary of what we know about the user."""
    print(f"\n📊 Last.fm profile summary for: {username}")

    top_artists = get_top_artists(username)
    print(f"\n🎤 Top {len(top_artists)} artists:")
    for i, artist in enumerate(top_artists, 1):
        print(f"  {i}. {artist}")

    heard = get_heard_albums(username)
    print(f"\n💿 Total albums filtered out (already heard): {len(heard)}")

    return top_artists, heard

# --- Run ---
if __name__ == "__main__":
    username = "TinyTanBoi"
    top_artists, heard_albums = display_summary(username)      
    

