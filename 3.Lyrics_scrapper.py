import os
import requests
from bs4 import BeautifulSoup
import re
from mido import MidiFile

GENIUS_API_TOKEN = 'FUy_sZXEhriY55pscdZejj-TCUB317FyosfzUeCMywC7dWSt8v1lUL6rIDceLGrJ'

def search_song_url(query):
    print(f"Searching for: {query}")
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search'
    params = {'q': query}
    response = requests.get(search_url, params=params, headers=headers)
    print(f"API response code: {response.status_code}")
    if response.status_code != 200:
        print(f"API error: {response.text}")
        return None
    json = response.json()
    hits = json.get('response', {}).get('hits', [])
    print(f"Hits found: {len(hits)}")
    if hits:
        return hits[0]['result']['url']
    return None

def scrape_song_lyrics(url):
    if not url:
        return None
    page = requests.get(url)
    if page.status_code != 200:
        return None
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics_divs = html.find_all('div', attrs={'data-lyrics-container': 'true'})
    if not lyrics_divs:
        return None
    lyrics_lines = []
    for div in lyrics_divs:
        text = div.get_text(separator='\n')
        lyrics_lines.append(text)
    lyrics = '\n'.join(lyrics_lines)
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    lyrics = re.sub(r'\n{2,}', '\n\n', lyrics)
    return lyrics.strip()

midi_dir = 'MIDIs'
lyrics_dir = 'Lyrics'
if not os.path.exists(lyrics_dir):
    os.makedirs(lyrics_dir)

instrumental_tracks = [
    'darude-sandstorm', 'pirates of the caribbean - hes a pirate',
    'wii channels - mii channel', 'star-wars-theme-from-star-wars',
    'super mario - medley', 'steveaustin'
]

for filename in os.listdir(midi_dir):
    if filename.endswith('.mid'):
        base_name = os.path.splitext(filename)[0]  # Remove .mid extension
        midi_path = os.path.join(midi_dir, filename)
        
        # Skip known instrumental tracks
        if any(track.lower() in base_name.lower() for track in instrumental_tracks):
            print(f"Skipping instrumental track: {filename}")
            continue
        
        # Check MIDI for lyrics
        try:
            mid = MidiFile(midi_path)
            lyrics = []
            for msg in mid:
                if hasattr(msg, 'type') and msg.type == 'lyrics':
                    lyrics.append(msg.text)
            if lyrics:
                full_lyrics = ''.join(lyrics)
                txt_path = os.path.join(lyrics_dir, base_name + '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(full_lyrics)
                print(f"Lyrics extracted from MIDI for {filename}")
                continue
        except Exception as e:
            print(f"Error reading MIDI {filename}: {e}")
        
        # Create search query from base_name (without .mid)
        query = base_name.replace('-', ' ').replace('_', ' ').title()
        # Specific query mappings for known songs
        if 'Bohemian Rhapsody' in base_name:
            query = 'Queen Bohemian Rhapsody'
        elif 'Still Dre' in base_name:
            query = 'Dr Dre Still Dre'
        elif 'Never Gonna Give You Up' in base_name:
            query = 'Rick Astley Never Gonna Give You Up'
        elif 'toto-africa' in base_name.lower():
            query = 'Toto Africa'
        elif 'Under The Sea' in base_name:
            query = 'Under The Sea Little Mermaid'
        elif 'Tokyo Ghoul - Unravel' in base_name:
            query = 'TK from Ling Tosite Sigure Unravel'
        
        song_url = search_song_url(query)
        lyrics_text = scrape_song_lyrics(song_url)
        if lyrics_text:
            txt_path = os.path.join(lyrics_dir, base_name + '.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(lyrics_text)
            print(f"Lyrics downloaded from internet for {filename}")
        else:
            print(f"No lyrics found for {filename}")
