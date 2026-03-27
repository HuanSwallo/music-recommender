from shared import scraper, client
from bs4 import BeautifulSoup


def get_album_id(artist_id, album_name):
    url = f'https://www.albumoftheyear.org/artist/{artist_id}/'
    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    #Find the album link in the artist's page
    album_links = soup.find_all('a', href=lambda h: h and '/album/' in h)
    for link in album_links:
        if album_name.lower() in link.get_text().lower():
            return link['href'].split('/album/')[1].strip('/')
        
    return None

def get_album_scores(artist_id, album_name):
    album_id = get_album_id(artist_id, album_name)
    if not album_id:
        return None
    
    url = f'https://www.albumoftheyear.org/album/{album_id}/'
    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    scores = {
        "critic_score": None,
        "user_score": None,
        "must_hear": "no"
    }

    # Extrac critic score
    critic = soup.find('div', class_='albumCriticScore')
    if critic:
        try:
            scores['critic_score'] = int(critic.get_text().strip())
        except ValueError:
            pass

    # Extract user score
    user = soup.find('div', class_='albumUserScore')  
    if user:
        try:
            scores['user_score'] = int(float(user.get_text().strip()))
        except ValueError:
            pass

    # Check if it's a must hear album
    must_hear = soup.find('div', class_='mustHearButton')
    if must_hear:
        title = must_hear.get('title', '')
        if title == 'Critic & User Must Hear':
            scores['must_hear'] = 'both'
        elif title == 'Critic Must Hear':
            scores['must_hear'] = 'critic'
        elif title == 'User Must Hear':
            scores['must_hear'] = 'user'

    return scores

def calc_recommendation_score(critic_score, user_score, must_hear, is_top_artist=False):
    score = 0
    weight_total = 0

    if critic_score is not None:
        score += critic_score * 0.5
        weight_total += 0.5

    if user_score is not None:
        score += user_score * 0.5
        weight_total += 0.5

    # If only one score is available, use it as the full score
    if 0 < weight_total < 1:
        score = score / weight_total

    must_hear_bonus = {
        "both": 10,
        "critic": 5,
        "user": 5,
        "no": 0
    }

    score += must_hear_bonus.get(must_hear, 0)

    if is_top_artist:
        score += 5

    return round(score, 2)

def score_releases(releases, heard_albums, top_artists):
    top_artists_lower = [artist.lower() for artist in top_artists]
    scored_releases = []

    for release in releases:
        # --- Filter out already heard albums ---
        heard_key = f"{release['artist'].lower()} - {release['name'].lower()}"
        if heard_key in heard_albums:
            print(f"  Skipping (already heard): {release['name']}")
            continue

        print(f"  Scoring: {release['artist']} - {release['name']}")

        # --- Fetch scores from AOTY ---
        scores = get_album_scores(release['artist_id'], release['name'])
        if not scores:
            print(f"  Could not fetch scores for {release['name']}, skipping")
            continue

        critic_score = scores['critic_score']
        user_score = scores['user_score']
        must_hear = scores['must_hear']

        # Skip releases with no scores at all
        if critic_score is None and user_score is None:
            continue

        # --- Affinity check ---
        is_top_artist = release['artist'].lower() in top_artists_lower
        # --- Final score ---
        final_score = calc_recommendation_score(
            critic_score, user_score, must_hear, is_top_artist
        )

        scored_releases.append({
            "artist": release['artist'],
            "name": release['name'],
            "type": release['type'],
            "critic_score": critic_score,
            "user_score": user_score,
            "must_hear": must_hear,
            "is_top_artist": is_top_artist,
            "final_score": final_score
        })

    # Sort by final score descending
    scored_releases.sort(key=lambda x: x['final_score'], reverse=True)
    return scored_releases    

def display_recommendations(recommendations, limit=10):
    """Print the top N recommendations."""
    print(f"\n🎵 Top {limit} Album Recommendations:\n")
    for i, rec in enumerate(recommendations[:limit], 1):
        must_hear_label = {
            "both":   "⭐ Must Hear (Critics + Users)",
            "critic": "🔵 Must Hear (Critics)",
            "user":   "🟠 Must Hear (Users)",
            "no":     ""
        }.get(rec['must_hear'], "")

        affinity = "💚 Top Artist" if rec['is_top_artist'] else ""
        tags = " ".join(filter(None, [must_hear_label, affinity]))

        print(f"{i}. {rec['artist']} - {rec['name']} [{rec['type']}]")
        print(f"   Critic: {rec['critic_score']}  |  User: {rec['user_score']}  |  Final Score: {rec['final_score']}")
        if tags:
            print(f"   {tags}")
        print()   
