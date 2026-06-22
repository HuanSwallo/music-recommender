from lastfm import get_top_artists, get_heard_albums, get_user_genres
from recommender import build_recommendations, display_top_albums
from database import init_db

USERNAME = "TinyTanBoi"


def main():
    print("=" * 50)
    print("🎵 Album Recommender System")
    print("=" * 50)

    # Set up the SQLite database tables on first run
    init_db()

    # Step 1: Pull the user's listening data from Last.fm
    print(f"\n📡 Fetching Last.fm data for '{USERNAME}'...")
    top_artists = get_top_artists(USERNAME, limit=5)
    heard_albums = get_heard_albums(USERNAME)

    print(f"\n🎤 Your top {len(top_artists)} artists:")
    for i, artist in enumerate(top_artists, 1):
        print(f"  {i}. {artist}")
    print(f"\n💿 Albums filtered out (already heard): {len(heard_albums)}")

    # Step 2: Map the user's top artists' Last.fm tags to AOTY genre slugs
    print(f"\n🏷️  Matching genres from Last.fm tags...")
    genres = get_user_genres(top_artists)
    print(f"  Matched genres: {genres}")

    if not genres:
        print("  No matching genres found, falling back to 'pop'")
        genres = {"pop"}

    # Step 3: Scrape AOTY genre charts and build recommendations
    print(f"\n⚙️  Building recommendations from genre charts...")
    critic_recs, user_recs = build_recommendations(genres, heard_albums, top_artists, year="2026")

    # Step 4: Display results
    display_top_albums(critic_recs, "critic_score", "Critic Score", limit=10)
    display_top_albums(user_recs, "user_score", "User Score", limit=10)

    print("=" * 50)
    print("✅ Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
