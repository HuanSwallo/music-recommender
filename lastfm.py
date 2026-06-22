import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('LASTFM_API_KEY')


def lastfm_getter(method, **params):
    """Make a Last.fm API request and return the parsed JSON response."""
    response = requests.get('http://ws.audioscrobbler.com/2.0/', params={
        "method": method,
        "api_key": api_key,
        "format": "json",
        **params
    })
    response.raise_for_status()
    return response.json()


def get_top_artists(user, limit=20):
    """Return a list of the user's most-played artist names."""
    data = lastfm_getter("user.getTopArtists", user=user, limit=limit)
    artists = data['topartists']['artist']
    return [artist['name'] for artist in artists]


def get_heard_albums(user):
    """Return a set of 'artist - album' strings representing albums the user has heard.

    Pulls from both top albums (up to 1000) and recent tracks (up to 200) so that
    albums scrobbled recently but not yet in the top list are still excluded.
    """
    heard = set()

    # Top albums covers the user's long-term listening history
    data = lastfm_getter("user.getTopAlbums", user=user, limit=1000)
    for album in data['topalbums']['album']:
        heard.add(f"{album['artist']['name'].lower()} - {album['name'].lower()}")

    # Recent tracks catches albums that haven't accumulated enough plays yet
    data = lastfm_getter("user.getRecentTracks", user=user, limit=200)
    for track in data['recenttracks']['track']:
        album_name = track['album']['#text']
        artist_name = track['artist']['#text']
        if album_name:
            heard.add(f"{artist_name.lower()} - {album_name.lower()}")

    return heard


def get_artist_top_tags(artist_name):
    """Return the top 5 Last.fm tags for an artist (used to infer genres)."""
    try:
        data = lastfm_getter("artist.getTopTags", artist=artist_name)
        tags = data.get('toptags', {}).get('tag', [])
        return [tag['name'] for tag in tags[:5]]
    except Exception as e:
        print(f"  Could not fetch tags for {artist_name}: {e}")
        return []


def get_user_genres(top_artists):
    """Return a set of AOTY genre slugs inferred from the user's top artists' Last.fm tags."""
    from genre_match import match_lastfm_tags_to_aoty_genres
    all_genres = set()
    for artist in top_artists:
        tags = get_artist_top_tags(artist)
        matched = match_lastfm_tags_to_aoty_genres(tags)
        all_genres.update(matched)
    return all_genres
