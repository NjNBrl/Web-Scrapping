import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ================================
# SETTINGS
# ================================
PAGES_TO_SCRAPE = [1]  # Change as needed
BASE_URL = "https://bitmidi.com/"
DOWNLOAD_FOLDER = "MIDIs"

# ================================
# SETUP
# ================================
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

# ================================
# FUNCTIONS
# ================================
def fetch_html(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def get_song_page_links(page_number):
    url = BASE_URL if page_number == 1 else f"{BASE_URL}?page={page_number}"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    song_links = []
    for a in soup.select("a[href]"):
        href = a["href"]
        if href.startswith("/") and not href.endswith(".mid"):
            song_links.append(urljoin(BASE_URL, href))
    return list(set(song_links))

def get_midi_info(song_page_url):
    """Returns (midi_url, song_title)"""
    html = fetch_html(song_page_url)
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title from <h1> tag
    title_tag = soup.find("h1")
    song_title = title_tag.text.strip() if title_tag else "Unknown Song"
    
    # Extract MIDI link
    midi_url = None
    for a in soup.select("a[href]"):
        href = a["href"]
        if href.endswith(".mid"):
            midi_url = urljoin(song_page_url, href)
            break
    
    return midi_url, song_title

def sanitize_filename(name, allow_numbers=False):
    allowed_chars = (" ", "-", "_")
    if allow_numbers:
        return "".join(c for c in name if c.isalnum() or c in allowed_chars).strip()
    else:
        return "".join(c for c in name if (c.isalpha() or c in allowed_chars)).strip()

def remove_mid_extension(name):
    return name[:-4] if name.lower().endswith(".mid") else name

def download_file(url, song_title):
    song_title_no_ext = remove_mid_extension(song_title)
    safe_title = sanitize_filename(song_title_no_ext, allow_numbers=False)
    local_name = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.mid")
    
    if os.path.exists(local_name):
        print(f"Already downloaded: {local_name}")
        return local_name
    
    print(f"Downloading: {url}")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    with open(local_name, "wb") as f:
        f.write(resp.content)
    print(f"Saved to {local_name}")
    return local_name

# ================================
# MAIN
# ================================
def main():
    total_midis = 0
    for page in PAGES_TO_SCRAPE:
        print(f"\nFetching song pages from BitMidi page {page}...")
        song_pages = get_song_page_links(page)
        print(f"Found {len(song_pages)} song pages on page {page}.")

        for song_url in song_pages:
            midi_url, song_title = get_midi_info(song_url)
            if midi_url:
                download_file(midi_url, song_title)
                total_midis += 1

    print(f"\nDownloaded {total_midis} MIDI file(s).")

if __name__ == "__main__":
    main()
