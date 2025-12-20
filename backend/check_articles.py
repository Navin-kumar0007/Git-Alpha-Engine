import requests

# Get articles and check URLs
url = "http://127.0.0.1:8000/api/news/articles?page=1&page_size=20"
r = requests.get(url)
data = r.json()

print("Checking article URLs:\n")
print("=" * 80)

for i, article in enumerate(data.get('articles', [])[:10], 1):
    title = article.get('title', 'N/A')[:50]
    url = article.get('url', '')
    source = article.get('source_name', 'Unknown')
    
    is_dummy = 'example.com' in url
    status = "DUMMY (won't open)" if is_dummy else "REAL (should open)"
    
    print(f"\n{i}. [{source}] {title}...")
    print(f"   URL: {url}")
    print(f"   Status: {status}")

print("\n" + "=" * 80)
print("\nTo see REAL articles, scroll down past the first 8 dummy articles!")
