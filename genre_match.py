# All genres that AOTY has a dedicated chart page for.
# Last.fm tags are matched against this set to find genres we can actually scrape.
AOTY_GENRES = {
    "alt-pop", "alternative metal", "alternative r&b", "alternative rock",
    "ambient", "americana", "art pop", "art rock", "atmospheric black metal",
    "black metal", "classical", "contemporary folk", "contemporary r&b",
    "country", "dance", "dance-pop", "death metal", "doom metal",
    "dream pop", "east coast hip hop", "electronic", "electronic dance music",
    "electropop", "emo", "experimental", "experimental rock", "folk",
    "folk rock", "garage rock", "hard rock", "hardcore punk",
    "heavy metal", "hip hop", "house", "indie folk", "indie pop", "indie rock",
    "indietronica", "jazz", "k-pop", "melodic death metal", "metal",
    "metalcore", "modern classical", "neo-psychedelia", "neo-soul",
    "orchestral", "pop", "pop rap", "pop rock",
    "post-hardcore", "post-industrial", "post-metal", "post-punk",
    "post-rock", "progressive metal", "progressive rock", "psychedelia",
    "psychedelic rock", "punk", "punk rock", "r&b", "rock",
    "shoegaze", "singer-songwriter", "sludge metal", "soul",
    "southern hip hop", "synthpop", "thrash metal", "trap",
}


def genre_to_slug(genre_name):
    """Convert a genre name to the URL slug format used by AOTY (e.g. 'hip hop' -> 'hip-hop')."""
    return genre_name.lower().replace(' ', '-').replace('&', 'and')


def match_lastfm_tags_to_aoty_genres(lastfm_tags):
    """Return the subset of Last.fm tags that match a known AOTY genre."""
    matched = []
    for tag in lastfm_tags:
        tag_clean = tag.lower().strip()
        if tag_clean in AOTY_GENRES:
            matched.append(tag_clean)
    return matched
