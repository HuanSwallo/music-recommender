from albumoftheyearapi import AOTY
from bs4 import BeautifulSoup
import cloudscraper

client = AOTY()
scraper = cloudscraper.create_scraper() # Use cloudscraper to bypass Cloudflare protection

def get_artist_id(artist_name):
    """
    Search for the artist and extract the artist ID
    """
    # Format search query
    search_name = artist_name.lower().replace(' ', '+')
    url = f'https://www.albumoftheyear.org/search/artists/?q={search_name}'
    response = scraper.get(url)
    response.raise_for_status()

    # Use beautifulsoup to parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the first artist link in the search results
    artist_link = soup.find('a', href=lambda h: h and '/artist/' in h)
    if not artist_link:
        print("Could not find artist in search results")
        return None

    # Extract the ID directly from the search results href
    artist_id = artist_link['href'].split('/artist/')[1].strip('/')
    return artist_id

def get_artist_releases(artist_name):
    artist_id = get_artist_id(artist_name)
    if not artist_id:
        return []
    
    releases = []

    # Get albums for the artist
    try:
        albums = client.artist_albums(artist_id)
        if albums:
            for album in albums:
                releases.append({
                    "artist": artist_name,
                    "name": album,
                    "type": "album",
                    "critic_score": None,
                    "user_score": None
                })
    except Exception as e:
        print(f"Error fetching albums for {artist_name}: {e}")

    # Get mixtapes for the artist
    try:
        mixtapes = client.artist_mixtapes(artist_id)
        if mixtapes:
            for mixtape in mixtapes:
                releases.append({
                    "artist": artist_name,
                    "name": mixtape,
                    "type": "mixtape",
                    "critic_score": None,
                    "user_score": None
                })
    except Exception as e:
        print(f"Error fetching mixtapes for {artist_name}: {e}")

    # Get Eps for the artist
    try:
        eps = client.artist_eps(artist_id)
        if eps:
            for ep in eps:
                releases.append({
                    "artist": artist_name,
                    "name": ep,
                    "type": "ep",
                    "critic_score": None,
                    "user_score": None
                })
    except Exception as e:
        print(f"Error fetching EPs for {artist_name}: {e}")

    return releases

def get_releases_for_top_artists(top_artists):
    all_releases = []
    for artist in top_artists:
        print(f"Fetching releases for {artist}...")
        releases = get_artist_releases(artist)
        print(f"Found {len(releases)} releases for {artist}")
        all_releases.extend(releases)  
    return all_releases

if __name__ == "__main__":
    # Test with a few artists
    test_artists = ["Kendrick Lamar", "Frank Ocean"]
    releases = get_releases_for_top_artists(test_artists)
    print(f"\nTotal releases found: {len(releases)}")
    for r in releases:
        print(f"  [{r['type']}] {r['artist']} - {r['name']}")                                      

