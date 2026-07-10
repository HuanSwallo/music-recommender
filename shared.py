import cloudscraper

# cloudscraper is a requests wrapper that bypasses Cloudflare bot protection,
# which AOTY uses. All HTTP requests to AOTY go through this scraper.
scraper = cloudscraper.create_scraper()
