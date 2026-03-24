from albumoftheyearapi import AOTY
from bs4 import BeautifulSoup
import cloudscraper

def get_artist_id(artist_name):
    """
    Search for the artist and extract the artist ID
    """
    # Format search query
    search_name = artist_name.lower().replace(' ', '+')
    url = f'https://www.albumoftheyear.org/search/artists/?q={search_name}'

    # Use cloudscraper to bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    print(response.status_code)  # should now be 200

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

client = AOTY()
artist_id = get_artist_id("Kendrick Lamar")

if artist_id:
    albums = client.artist_albums(artist_id)
    print(albums)
else:
    print("Could not find artist ID")  