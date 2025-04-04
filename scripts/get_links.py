import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://poway.com"
visited = set()
all_links = set()

def is_valid_link(link):
    if link is None or link == "":
        return False
    if link.startswith("tel:") or link.startswith("mailto:"):
        return False
    
    if any(link.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".js", ".css", ".ico", ".webp", ".mp4", ".mp3"]):
        return False
    
    if any(x in link for x in [
        "/blog/", "/journal/", "/guest-columns/", "/e-edition/", "/news/", "/author/",
        "/page/", "/product/", "/cart/", "/checkout/", "/cdn-cgi/l/email-protection",
        "/list/member/",  # 🛑 Business directory detail pages
        "/jobs/",         # 🛑 Job boards
        "/hotdeals/",     # 🛑 Ads or promos
        "/events/details/",  # 🛑 Specific event pages
        "calendarMonth=",    # 🛑 Query-heavy dynamic pages
        "/mp4", "/media/",    # 🛑 Embedded files and media
    ]):
        return False
    if "#" in link:
        return False

    return True

def crawl(url, depth=0, max_depth=3):
    if depth > max_depth or url in visited:
        return

    print(f"🔍 Crawling (depth {depth}): {url}")
    visited.add(url)


    try:
        response = requests.get(url, timeout=5)
        if "text/html" not in response.headers.get("Content-Type", ""):
            return
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            href = tag['href']
            full_url = urljoin(url, href)
            print(f"👉 Found: {full_url}")  # [TEMP DEBUG LINE]
            parsed = urlparse(full_url)

            if not parsed.netloc.endswith("poway.com"):
                continue  # Skip truly external links

            if is_valid_link(full_url) and full_url not in visited:
                all_links.add(full_url)
                crawl(full_url, depth + 1, max_depth)

    except Exception as e:
        print(f"❌ Failed to crawl {url}: {e}")

# === START CRAWL ===
crawl(BASE_URL)

# === EXPORT LINKS ===
with open("poway_links.txt", "w") as f:
    for link in sorted(all_links):
        f.write(link + "\n")

print(f"\n✅ Finished! Total links found: {len(all_links)}")
