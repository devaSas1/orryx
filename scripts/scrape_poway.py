import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import os
import shutil  # [ADDED]

INPUT_FILE = "poway_links.txt"
OUTPUT_FILE = "poway_knowledge_base_structured.json"
MAX_CHARS = 2000



def clean_text(text):
    return ' '.join(text.split())

def extract_visible_text(url):
    try:
        print(f"🔍 Scraping: {url}")
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Kill scripts, styles, and headers
        for tag in soup(["script", "style", "header", "footer", "nav", "form"]):
            tag.extract()

        text = soup.get_text(separator=' ')
        return clean_text(text)
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return ""

def generate_qa_pair(url):
    text = extract_visible_text(url)
    if not text:
        return None
    return {
        "question": f"What does this page say? ({url})",
        "answer": text[:MAX_CHARS] + f"\n\nLearn more: {url}"
    }

# === Load URLs ===
if not os.path.exists(INPUT_FILE):
    print(f"❌ Input file not found: {INPUT_FILE}")
    exit()

with open(INPUT_FILE, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# === Scrape in parallel ===
qa_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(generate_qa_pair, urls))

qa_data = [r for r in results if r is not None]

# === Save output ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(qa_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Scraping complete. Output saved to {OUTPUT_FILE}")

# === Move output to clients/poway/data === [ADDED]
DEST_PATH = "../clients/poway/data/poway_knowledge_base_structured.json"  # [ADDED]
try:  # [ADDED]
    if os.path.exists(DEST_PATH):  # [ADDED]
        os.remove(DEST_PATH)  # [ADDED]
    shutil.move(OUTPUT_FILE, DEST_PATH)  # [ADDED]
    print(f"✅ Moved file to {DEST_PATH}")  # [ADDED]
except Exception as e:  # [ADDED]
    print(f"❌ Could not move file: {e}")  # [ADDED]
