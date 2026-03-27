from lastfm import get_top_artists, get_heard_albums
from aoty import get_releases_for_top_artists
from recommender import score_releases, display_recommendations

USERNAME = "TinyTanBoi"

def main():
    print("=" * 50)
    print("🎵 Album Recommender System")
    print("=" * 50)

    # --- Step 1: Get Last.fm data ---
    print(f"\n📡 Fetching Last.fm data for '{USERNAME}'...")
    top_artists = get_top_artists(USERNAME)
    heard_albums = get_heard_albums(USERNAME)

    print(f"\n🎤 Your top {len(top_artists)} artists:")
    for i, artist in enumerate(top_artists, 1):
        print(f"  {i}. {artist}")
    print(f"\n💿 Albums filtered out (already heard): {len(heard_albums)}")

    # --- Step 2: Get AOTY releases ---
    print(f"\n🔍 Fetching releases from AOTY for your top artists...")
    releases = get_releases_for_top_artists(top_artists)
    print(f"\n📀 Total releases found: {len(releases)}")

    # --- Step 3: Score and filter ---
    print(f"\n⚙️  Scoring and filtering releases...")
    recommendations = score_releases(releases, heard_albums, top_artists)

    # --- Step 4: Display results ---
    display_recommendations(recommendations, limit=10)

    print("=" * 50)
    print("✅ Done!")
    print("=" * 50)

if __name__ == "__main__":
    main()