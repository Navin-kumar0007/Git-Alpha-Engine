import requests

# Test the news endpoint
url = "http://127.0.0.1:8000/api/news/articles?page=1&page_size=100"
r = requests.get(url)
data = r.json()

print(f"Status: {r.status_code}")
print(f"Total articles returned: {data.get('total', 0)}")
print(f"Page size: {data.get('page_size', 0)}")
print(f"Number of articles in response: {len(data.get('articles', []))}")

print("\nFirst 5 article titles:")
for i, article in enumerate(data.get('articles', [])[:5], 1):
    source = article.get('source_name', 'Unknown')
    title = article.get('title', 'N/A')
    url = article.get('url', '')
    is_real = 'example.com' not in url
    print(f"{i}. [{source}] {title[:60]}... (Real: {is_real})")
