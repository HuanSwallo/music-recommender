import time
from bs4 import BeautifulSoup
from shared import scraper
from database import (
    save_genre_id, get_genre_id, is_genre_chart_cached,
    save_genre_chart_results, get_cached_genre_chart
)
from genre_match import genre_to_slug

# Minimum thresholds to filter out albums with too little data behind their scores
MIN_USER_RATINGS = 100
MIN_CRITIC_REVIEWS = 3


def parse_album_chart_page(url, score_field_name, count_field_name, genre_slug=None):
    """Scrape an AOTY chart page and return a list of album dicts.

    score_field_name: key to store the score under ('user_score' or 'critic_score')
    count_field_name: key to store the count under ('user_ratings' or 'critic_reviews')
    genre_slug: if provided, also extracts and saves the genre's numeric ID from the page
    """
    try:
        response = scraper.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"  Could not fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    # The user chart page embeds the genre's numeric ID in a data attribute.
    # We save it here so we can build the critic chart URL later.
    if genre_slug:
        genre_select = soup.find('span', class_='genreSelect')
        if genre_select and genre_select.has_attr('data-genre-id'):
            save_genre_id(genre_slug, genre_select['data-genre-id'])

    for row in soup.find_all('div', class_='albumListRow'):
        # Each row has a span with itemprop="item" containing an <a> with "Artist - Album"
        title_span = row.find('span', itemprop='item')
        if not title_span:
            continue
        link_a = title_span.find('a')
        if not link_a:
            continue

        full_text = link_a.get_text().strip()
        if ' - ' not in full_text:
            continue
        artist_name, album_name = full_text.split(' - ', 1)

        # Extract the numeric score (e.g. 82)
        score = None
        score_container = row.find('div', class_='scoreValueContainer')
        if score_container:
            score_div = score_container.find('div', class_='scoreValue')
            if score_div:
                try:
                    score = int(score_div.get_text().strip())
                except ValueError:
                    pass

        # Extract the rating/review count — e.g. "8,380 ratings" -> 8380
        count = 0
        score_text = row.find('div', class_='scoreText')
        if score_text:
            text = score_text.get_text().strip()
            number_part = text.split()[0].replace(',', '')
            try:
                count = int(number_part)
            except ValueError:
                pass

        results.append({
            "artist": artist_name.strip(),
            "name": album_name.strip(),
            score_field_name: score,
            count_field_name: count
        })

    return results


def fetch_user_genre_chart(genre_slug, year="2026"):
    """Fetch the user-rated chart for a genre from AOTY."""
    url_slug = genre_to_slug(genre_slug)
    url = f"https://www.albumoftheyear.org/ratings/user-highest-rated/{year}/{url_slug}/"
    return parse_album_chart_page(url, "user_score", "user_ratings", genre_slug=genre_slug)


def fetch_critic_genre_chart(genre_id, genre_slug, year="2026"):
    """Fetch the critic-rated chart for a genre from AOTY.

    Requires genre_id (the numeric ID from AOTY's URL, e.g. '38' for hip-hop),
    which is extracted from the user chart page and saved to the database.
    """
    url_slug = genre_to_slug(genre_slug)
    url = f"https://www.albumoftheyear.org/genre/{genre_id}-{url_slug}/{year}/"
    return parse_album_chart_page(url, "critic_score", "critic_reviews")


def fetch_both_charts(genre_slug, year="2026"):
    """Fetch and return both user and critic chart results for a genre.

    The user chart must be fetched first because it embeds the numeric genre ID
    needed to construct the critic chart URL.
    """
    user_results = fetch_user_genre_chart(genre_slug, year)
    time.sleep(2)  # Be polite to AOTY's servers between requests

    genre_id = get_genre_id(genre_slug)
    if genre_id:
        critic_results = fetch_critic_genre_chart(genre_id, genre_slug, year)
        time.sleep(2)
    else:
        print(f"  No genre ID known yet for '{genre_slug}', skipping critic chart")
        critic_results = []

    return user_results, critic_results


def merge_chart_results(user_results, critic_results):
    """Combine user and critic chart results into a single list of album dicts.

    Albums appearing in both charts are merged into one entry. Albums that
    only appear in one chart will have None for the other chart's score.
    """
    merged = {}

    for r in user_results:
        key = f"{r['artist'].lower()} - {r['name'].lower()}"
        merged[key] = {
            "artist": r['artist'],
            "name": r['name'],
            "user_score": r.get('user_score'),
            "user_ratings": r.get('user_ratings', 0),
            "critic_score": None,
            "critic_reviews": 0
        }

    for r in critic_results:
        key = f"{r['artist'].lower()} - {r['name'].lower()}"
        if key in merged:
            # Album already seen in user chart — add critic data to it
            merged[key]['critic_score'] = r.get('critic_score')
            merged[key]['critic_reviews'] = r.get('critic_reviews', 0)
        else:
            # Album only appears on the critic chart
            merged[key] = {
                "artist": r['artist'],
                "name": r['name'],
                "user_score": None,
                "user_ratings": 0,
                "critic_score": r.get('critic_score'),
                "critic_reviews": r.get('critic_reviews', 0)
            }

    return list(merged.values())


def get_genre_chart(genre_slug, year="2026"):
    """Return merged chart data for a genre, loading from the DB cache when available.

    Cache expires after 7 days (configured in database.is_genre_chart_cached).
    """
    if is_genre_chart_cached(genre_slug):
        print(f"  Loading genre chart from cache: {genre_slug}")
        return get_cached_genre_chart(genre_slug)

    print(f"  Fetching genre chart: {genre_slug}")
    user_results, critic_results = fetch_both_charts(genre_slug, year)
    merged = merge_chart_results(user_results, critic_results)

    # Save both score types so the cache table stores full data for the next run
    save_genre_chart_results(genre_slug, merged, "user_score")
    save_genre_chart_results(genre_slug, merged, "critic_score")

    return merged


def build_recommendations(genres, heard_albums, top_artists, year="2026"):
    """Build two ranked lists of album recommendations — one by critic score, one by user score.

    Filters out:
    - Albums already in the user's Last.fm history (heard_albums)
    - Albums with fewer than MIN_CRITIC_REVIEWS critic reviews
    - Albums with fewer than MIN_USER_RATINGS user ratings

    Albums by the user's top Last.fm artists are marked with is_top_artist=True.
    """
    top_artists_lower = [a.lower() for a in top_artists]
    critic_pool = {}
    user_pool = {}

    for genre_slug in genres:
        chart = get_genre_chart(genre_slug, year)
        print(f"  '{genre_slug}' chart returned {len(chart)} albums")

        for album in chart:
            heard_key = f"{album['artist'].lower()} - {album['name'].lower()}"

            # Skip albums the user has already listened to
            if heard_key in heard_albums:
                continue

            is_top_artist = album['artist'].lower() in top_artists_lower
            key = heard_key

            # Add to critic pool if it has enough reviews to be meaningful
            critic_score = album.get('critic_score')
            critic_reviews = album.get('critic_reviews', 0)
            if critic_score is not None and critic_reviews >= MIN_CRITIC_REVIEWS:
                # If the album appears across multiple genre charts, keep the highest score
                if key not in critic_pool or critic_score > critic_pool[key]['critic_score']:
                    critic_pool[key] = {
                        "artist": album['artist'], "name": album['name'],
                        "critic_score": critic_score, "critic_reviews": critic_reviews,
                        "is_top_artist": is_top_artist, "genre": genre_slug
                    }

            # Add to user pool if it has enough ratings to be meaningful
            user_score = album.get('user_score')
            user_ratings = album.get('user_ratings', 0)
            if user_score is not None and user_ratings >= MIN_USER_RATINGS:
                # If the album appears across multiple genre charts, keep the highest score
                if key not in user_pool or user_score > user_pool[key]['user_score']:
                    user_pool[key] = {
                        "artist": album['artist'], "name": album['name'],
                        "user_score": user_score, "user_ratings": user_ratings,
                        "is_top_artist": is_top_artist, "genre": genre_slug
                    }

    # Sort each pool by score, highest first
    critic_list = sorted(critic_pool.values(), key=lambda x: x['critic_score'], reverse=True)
    user_list = sorted(user_pool.values(), key=lambda x: x['user_score'], reverse=True)

    print(f"  Critic pool size: {len(critic_list)} | User pool size: {len(user_list)}")
    return critic_list, user_list


def display_top_albums(albums, score_field, label, limit=10):
    """Print the top N albums from a recommendation list."""
    count_field = "critic_reviews" if score_field == "critic_score" else "user_ratings"
    count_label = "Reviews" if score_field == "critic_score" else "Ratings"
    print(f"\n🎵 Top {limit} Albums by {label}:\n")
    if not albums:
        print("  (none found)")
        return
    for i, rec in enumerate(albums[:limit], 1):
        affinity = " 💚 Top Artist" if rec['is_top_artist'] else ""
        print(f"{i}. {rec['artist']} - {rec['name']} [{rec['genre']}]")
        print(f"   {label}: {rec[score_field]}  |  {count_label}: {rec[count_field]}{affinity}")
        print()
