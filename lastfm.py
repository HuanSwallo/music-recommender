import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('LASTFM_API_KEY')

def lastfm_getter(method, **params):
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params={
        "method": method,
        "api_key": api_key,
        "format": "json",
        **params
    })
    response.raise_for_status()
    return response.json()

def get_top_artists(user, limit=20):
    data = lastfm_getter("user.getTopArtists", user=user, limit=limit)
    artists = data['topartists']['artist']
    return [artist['name'] for artist in artists]

def get_heard_albums(user):
    heard = set()
    data = lastfm_getter("user.getTopAlbums", user=user, limit=1000)
    for album in data['topalbums']['album']:
        heard.add(f"{album['artist']['name'].lower()} - {album['name'].lower()}")
    data = lastfm_getter("user.getRecentTracks", user=user, limit=200)
    for track in data['recenttracks']['track']:
        album_name = track['album']['#text']
        artist_name = track['artist']['#text']
        if album_name:
            heard.add(f"{artist_name.lower()} - {album_name.lower()}")
    return heard

def get_artist_top_tags(artist_name):
    try:
        data = lastfm_getter("artist.getTopTags", artist=artist_name)
        tags = data.get('toptags', {}).get('tag', [])
        return [tag['name'] for tag in tags[:5]]
    except Exception as e:
        print(f"  Could not fetch tags for {artist_name}: {e}")
        return []

def get_user_genres(top_artists):
    from genre_match import match_lastfm_tags_to_aoty_genres
    all_genres = set()
    for artist in top_artists:
        tags = get_artist_top_tags(artist)
        matched = match_lastfm_tags_to_aoty_genres(tags)
        all_genres.update(matched)
    return all_genres

def display_summary(username):
    print(f"\n📊 Last.fm profile summary for: {username}")
    top_artists = get_top_artists(username)
    print(f"\n🎤 Top {len(top_artists)} artists:")
    for i, artist in enumerate(top_artists, 1):
        print(f"  {i}. {artist}")
    heard = get_heard_albums(username)
    print(f"\n💿 Total albums filtered out (already heard): {len(heard)}")
    return top_artists, heard

if __name__ == "__main__":
    username = "TinyTanBoi"
    top_artists, heard_albums = display_summary(username)