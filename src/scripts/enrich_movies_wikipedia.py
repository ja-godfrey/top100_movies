import pandas as pd
import requests
import time
import json
import os
import re
from typing import Dict, Optional, List
from urllib.parse import quote

# Wikipedia API configuration
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"

def search_movie_wikipedia(title: str, year: Optional[int] = None) -> Optional[Dict]:
    """Search for a movie on Wikipedia and return the first result"""
    search_params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': f"{title} film",
        'srlimit': 5,
        'srnamespace': 0
    }
    
    if year:
        search_params['srsearch'] += f" {year}"
    
    try:
        response = requests.get(WIKIPEDIA_SEARCH_URL, params=search_params)
        response.raise_for_status()
        data = response.json()
        
        if data['query']['search']:
            # Get the first result
            first_result = data['query']['search'][0]
            
            # Get detailed page info
            page_title = first_result['title']
            page_url = f"https://en.wikipedia.org/wiki/{quote(page_title)}"
            
            # Get page content using MediaWiki API
            content_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts|pageimages',
                'titles': page_title,
                'exintro': True,
                'explaintext': True,
                'piprop': 'original'
            }
            
            content_response = requests.get(WIKIPEDIA_API_URL, params=content_params)
            content_response.raise_for_status()
            content_data = content_response.json()
            
            # Extract content from the response
            pages = content_data['query']['pages']
            page_id = list(pages.keys())[0]
            page_info = pages[page_id]
            
            # Get infobox data
            infobox_data = get_infobox_data(page_title)
            
            return {
                'title': page_title,
                'url': page_url,
                'extract': first_result.get('snippet', ''),
                'content': page_info.get('extract', ''),
                'image_url': page_info.get('original', {}).get('source', ''),
                'infobox': infobox_data
            }
        return None
    except Exception as e:
        print(f"Error searching for '{title}': {e}")
        return None

def get_infobox_data(page_title: str) -> Dict:
    """Extract infobox data from Wikipedia page"""
    try:
        # Get page content with infobox
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': page_title,
            'rvprop': 'content',
            'rvsection': 0
        }
        
        response = requests.get(WIKIPEDIA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        content = pages[page_id]['revisions'][0]['*']
        
        # Extract infobox data
        infobox_data = {}
        
        # Extract basic info
        infobox_data['director'] = extract_infobox_field(content, 'director')
        infobox_data['producer'] = extract_infobox_field(content, 'producer')
        infobox_data['writer'] = extract_infobox_field(content, 'writer')
        infobox_data['screenplay'] = extract_infobox_field(content, 'screenplay')
        infobox_data['story'] = extract_infobox_field(content, 'story')
        infobox_data['starring'] = extract_infobox_field(content, 'starring')
        infobox_data['music'] = extract_infobox_field(content, 'music')
        infobox_data['cinematography'] = extract_infobox_field(content, 'cinematography')
        infobox_data['editing'] = extract_infobox_field(content, 'editing')
        infobox_data['production_company'] = extract_infobox_field(content, 'production_company')
        infobox_data['distributor'] = extract_infobox_field(content, 'distributor')
        infobox_data['release_date'] = extract_infobox_field(content, 'release_date')
        infobox_data['running_time'] = extract_infobox_field(content, 'running_time')
        infobox_data['country'] = extract_infobox_field(content, 'country')
        infobox_data['language'] = extract_infobox_field(content, 'language')
        infobox_data['budget'] = extract_infobox_field(content, 'budget')
        infobox_data['box_office'] = extract_infobox_field(content, 'box_office')
        infobox_data['genre'] = extract_infobox_field(content, 'genre')
        infobox_data['rating'] = extract_infobox_field(content, 'rating')
        
        return infobox_data
    except Exception as e:
        print(f"Error getting infobox data for '{page_title}': {e}")
        return {}

def extract_infobox_field(content: str, field_name: str) -> str:
    """Extract a specific field from Wikipedia infobox"""
    try:
        # Look for infobox patterns with better regex
        patterns = [
            rf'\|\s*{field_name}\s*=\s*(.*?)(?:\n\||\n\}}|\n\|\}}|\n\|\s*\w+\s*=)',
            rf'\|\s*{field_name}\s*=\s*(.*?)(?:\n\||\n\}}|\n\|\}})',
            rf'{field_name}\s*=\s*(.*?)(?:\n\||\n\}}|\n\|\}})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                
                # Clean up the value more thoroughly
                # Remove HTML tags
                value = re.sub(r'<[^>]+>', '', value)
                
                # Remove ref tags and their content
                value = re.sub(r'<ref[^>]*>.*?</ref>', '', value, flags=re.DOTALL)
                value = re.sub(r'<ref[^>]*/>', '', value)
                
                # Remove citation needed
                value = re.sub(r'\{\{citation needed[^}]*\}\}', '', value)
                
                # Handle Wikipedia links - extract the display text
                value = re.sub(r'\[\[([^|\]]+)\]\]', r'\1', value)  # Simple links
                value = re.sub(r'\[\[([^|]+)\|([^\]]+)\]\]', r'\2', value)  # Links with display text
                
                # Handle templates - try to extract meaningful content
                value = re.sub(r'\{\{plainlist\|\s*([^}]+)\}\}', r'\1', value)
                value = re.sub(r'\{\{plainlist\|\s*([^}]+)\}\}', r'\1', value)
                value = re.sub(r'\{\{([^}]+)\}\}', r'\1', value)
                
                # Remove extra whitespace and newlines
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                
                # Remove leading/trailing punctuation
                value = re.sub(r'^[,\s*]+|[,\s*]+$', '', value)
                
                return value
        
        return ""
    except Exception as e:
        print(f"Error extracting field '{field_name}': {e}")
        return ""

def clean_list_item(item: str) -> str:
    """Clean up a single list item from Wikipedia markup"""
    if not item:
        return ""
    
    # Remove Wikipedia markup
    item = re.sub(r'\[\[([^|\]]+)\]\]', r'\1', item)  # Simple links
    item = re.sub(r'\[\[([^|]+)\|([^\]]+)\]\]', r'\2', item)  # Links with display text
    item = re.sub(r'\{\{([^}]+)\}\}', r'\1', item)  # Templates
    item = re.sub(r'<[^>]+>', '', item)  # HTML tags
    
    # Remove common prefixes/suffixes and template artifacts
    item = re.sub(r'^(Plainlist|plainlist|Unbulleted list|cite web|ubl|Ill)[^a-zA-Z0-9]+', '', item, flags=re.IGNORECASE)  # Remove template and list prefixes
    item = re.sub(r'^(\*|\||,|\s)+', '', item)  # Remove leading asterisks, pipes, commas, whitespace
    item = re.sub(r'(\*|\||,|\s)+$', '', item)  # Remove trailing asterisks, pipes, commas, whitespace
    
    # Remove any remaining curly braces or pipes
    item = re.sub(r'[{}|]', '', item)
    
    # Remove any remaining 'Plainlist', 'plainlist', 'Unbulleted list', 'cite web', 'ubl', 'Ill' anywhere in the string
    item = re.sub(r'(Plainlist|plainlist|Unbulleted list|cite web|ubl|Ill)', '', item, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    item = re.sub(r'\s+', ' ', item)
    return item.strip()

def extract_movie_info_wikipedia(wiki_data: Dict) -> Dict:
    """Extract relevant information from Wikipedia data"""
    if not wiki_data:
        return {}
    
    infobox = wiki_data.get('infobox', {})
    
    # Parse starring (actors)
    starring = infobox.get('starring', '')
    actors = []
    if starring:
        # Split by common delimiters and clean each item
        raw_actors = re.split(r'[,\n]', starring)
        actors = [clean_list_item(actor) for actor in raw_actors if clean_list_item(actor)]
    
    # Parse director
    director = infobox.get('director', '')
    directors = []
    if director:
        raw_directors = re.split(r'[,\n]', director)
        directors = [clean_list_item(d) for d in raw_directors if clean_list_item(d)]
    
    # Parse writer
    writer = infobox.get('writer', '')
    screenplay = infobox.get('screenplay', '')
    story = infobox.get('story', '')
    writers = []
    if writer:
        raw_writers = re.split(r'[,\n]', writer)
        writers.extend([clean_list_item(w) for w in raw_writers if clean_list_item(w)])
    if screenplay:
        raw_screenplay = re.split(r'[,\n]', screenplay)
        writers.extend([clean_list_item(w) for w in raw_screenplay if clean_list_item(w)])
    if story:
        raw_story = re.split(r'[,\n]', story)
        writers.extend([clean_list_item(w) for w in raw_story if clean_list_item(w)])
    writers = list(set(writers))  # Remove duplicates
    
    # Parse producer
    producer = infobox.get('producer', '')
    producers = []
    if producer:
        raw_producers = re.split(r'[,\n]', producer)
        producers = [clean_list_item(p) for p in raw_producers if clean_list_item(p)]
    
    # Parse cinematography
    cinematography = infobox.get('cinematography', '')
    cinematographers = []
    if cinematography:
        raw_cinematographers = re.split(r'[,\n]', cinematography)
        cinematographers = [clean_list_item(c) for c in raw_cinematographers if clean_list_item(c)]
    
    # Parse music
    music = infobox.get('music', '')
    composers = []
    if music:
        raw_composers = re.split(r'[,\n]', music)
        composers = [clean_list_item(m) for m in raw_composers if clean_list_item(m)]
    
    # Parse editing
    editing = infobox.get('editing', '')
    editors = []
    if editing:
        raw_editors = re.split(r'[,\n]', editing)
        editors = [clean_list_item(e) for e in raw_editors if clean_list_item(e)]
    
    # Parse production company
    production_company = infobox.get('production_company', '')
    production_companies = []
    if production_company:
        raw_companies = re.split(r'[,\n]', production_company)
        production_companies = [clean_list_item(p) for p in raw_companies if clean_list_item(p)]
    
    # Parse genre
    genre = infobox.get('genre', '')
    genres = []
    if genre:
        raw_genres = re.split(r'[,\n]', genre)
        genres = [clean_list_item(g) for g in raw_genres if clean_list_item(g)]
    
    # Parse country
    country = infobox.get('country', '')
    countries = []
    if country:
        raw_countries = re.split(r'[,\n]', country)
        countries = [clean_list_item(c) for c in raw_countries if clean_list_item(c)]
    
    # Parse language
    language = infobox.get('language', '')
    languages = []
    if language:
        raw_languages = re.split(r'[,\n]', language)
        languages = [clean_list_item(l) for l in raw_languages if clean_list_item(l)]
    
    # Clean up runtime
    runtime = infobox.get('running_time', '')
    if runtime:
        # Extract minutes from runtime string - handle various formats
        runtime_match = re.search(r'(\d+)\s*(?:minutes?|min)', runtime, re.IGNORECASE)
        if runtime_match:
            runtime = int(runtime_match.group(1))
        else:
            # Try to extract hours and minutes
            hours_match = re.search(r'(\d+)\s*h(?:ours?)?', runtime, re.IGNORECASE)
            minutes_match = re.search(r'(\d+)\s*m(?:inutes?)?', runtime, re.IGNORECASE)
            if hours_match and minutes_match:
                runtime = int(hours_match.group(1)) * 60 + int(minutes_match.group(1))
            elif hours_match:
                runtime = int(hours_match.group(1)) * 60
            else:
                runtime = None
    
    # Clean up budget - improved parsing
    budget = infobox.get('budget', '')
    if budget:
        # Remove currency symbols and clean up
        budget_clean = re.sub(r'[\$£€¥]', '', budget)
        
        # Look for million/billion indicators
        if 'million' in budget_clean.lower():
            # Extract number before "million"
            budget_match = re.search(r'([\d,]+(?:\.[\d]+)?)\s*million', budget_clean, re.IGNORECASE)
            if budget_match:
                budget = int(float(budget_match.group(1).replace(',', '')) * 1000000)
            else:
                budget = None
        elif 'billion' in budget_clean.lower():
            # Extract number before "billion"
            budget_match = re.search(r'([\d,]+(?:\.[\d]+)?)\s*billion', budget_clean, re.IGNORECASE)
            if budget_match:
                budget = int(float(budget_match.group(1).replace(',', '')) * 1000000000)
            else:
                budget = None
        else:
            # Try to extract just a number (assume it's in the base currency)
            budget_match = re.search(r'([\d,]+(?:\.[\d]+)?)', budget_clean)
            if budget_match:
                budget = int(float(budget_match.group(1).replace(',', '')))
            else:
                budget = None
    
    # Clean up box office - improved parsing
    box_office = infobox.get('box_office', '')
    if box_office:
        # Remove currency symbols and clean up
        box_clean = re.sub(r'[\$£€¥]', '', box_office)
        
        # Look for million/billion indicators
        if 'million' in box_clean.lower():
            # Extract number before "million"
            box_match = re.search(r'([\d,]+(?:\.[\d]+)?)\s*million', box_clean, re.IGNORECASE)
            if box_match:
                box_office = int(float(box_match.group(1).replace(',', '')) * 1000000)
            else:
                box_office = None
        elif 'billion' in box_clean.lower():
            # Extract number before "billion"
            box_match = re.search(r'([\d,]+(?:\.[\d]+)?)\s*billion', box_clean, re.IGNORECASE)
            if box_match:
                box_office = int(float(box_match.group(1).replace(',', '')) * 1000000000)
            else:
                box_office = None
        else:
            # Try to extract just a number (assume it's in the base currency)
            box_match = re.search(r'([\d,]+(?:\.[\d]+)?)', box_clean)
            if box_match:
                box_office = int(float(box_match.group(1).replace(',', '')))
            else:
                box_office = None
    
    return {
        'wikipedia_title': wiki_data.get('title', ''),
        'wikipedia_url': wiki_data.get('url', ''),
        'wikipedia_extract': wiki_data.get('extract', ''),
        'wikipedia_content': wiki_data.get('content', ''),
        'wikipedia_image_url': wiki_data.get('image_url', ''),
        'release_date': infobox.get('release_date', ''),
        'runtime': runtime,
        'budget': budget,
        'box_office': box_office,
        'rating': infobox.get('rating', ''),
        'director_1': directors[0] if len(directors) > 0 else '',
        'director_2': directors[1] if len(directors) > 1 else '',
        'director_3': directors[2] if len(directors) > 2 else '',
        'actor_1': actors[0] if len(actors) > 0 else '',
        'actor_2': actors[1] if len(actors) > 1 else '',
        'actor_3': actors[2] if len(actors) > 2 else '',
        'actor_4': actors[3] if len(actors) > 3 else '',
        'actor_5': actors[4] if len(actors) > 4 else '',
        'cinematographer_1': cinematographers[0] if len(cinematographers) > 0 else '',
        'cinematographer_2': cinematographers[1] if len(cinematographers) > 1 else '',
        'producer_1': producers[0] if len(producers) > 0 else '',
        'producer_2': producers[1] if len(producers) > 1 else '',
        'producer_3': producers[2] if len(producers) > 2 else '',
        'writer_1': writers[0] if len(writers) > 0 else '',
        'writer_2': writers[1] if len(writers) > 1 else '',
        'writer_3': writers[2] if len(writers) > 2 else '',
        'composer_1': composers[0] if len(composers) > 0 else '',
        'composer_2': composers[1] if len(composers) > 1 else '',
        'editor_1': editors[0] if len(editors) > 0 else '',
        'editor_2': editors[1] if len(editors) > 1 else '',
        'genres': ', '.join(genres),
        'production_companies': ', '.join(production_companies),
        'production_countries': ', '.join(countries),
        'spoken_languages': ', '.join(languages),
        'distributor': infobox.get('distributor', ''),
        'total_actors_count': len(actors),
        'total_crew_count': len(directors) + len(writers) + len(producers) + len(cinematographers) + len(composers) + len(editors)
    }

def enrich_movies_data_wikipedia(csv_path: str, output_path: str, max_movies: int = None):
    """Enrich movie data with Wikipedia information"""
    # Load existing data
    df = pd.read_csv(csv_path)
    
    if max_movies:
        df = df.head(max_movies)
    
    # Check if enriched file already exists
    existing_enriched = None
    if os.path.exists(output_path):
        try:
            existing_enriched = pd.read_csv(output_path)
            print(f"Found existing enriched data with {len(existing_enriched)} movies")
        except Exception as e:
            print(f"Could not read existing enriched file: {e}")
    
    enriched_data = []
    processed_count = 0
    skipped_count = 0
    
    for index, row in df.iterrows():
        print(f"Processing {index + 1}/{len(df)}: {row['title']}")
        
        # Check if this movie is already enriched
        if existing_enriched is not None:
            existing_row = existing_enriched[existing_enriched['title'] == row['title']]
            if not existing_row.empty and pd.notna(existing_row.iloc[0].get('wikipedia_title')):
                print(f"  Skipping {row['title']} - already enriched")
                enriched_data.append(existing_row.iloc[0].to_dict())
                skipped_count += 1
                continue
        
        # Search for movie on Wikipedia
        wiki_data = search_movie_wikipedia(row['title'])
        
        if wiki_data:
            # Extract information
            movie_info = extract_movie_info_wikipedia(wiki_data)
            
            # Combine original data with enriched data
            enriched_row = {
                'rank': row['rank'],
                'title': row['title'],
                'img_url': row['img_url'],
                'uniqid': row['uniqid'],
                **movie_info
            }
            processed_count += 1
        else:
            # Keep original data if no match found
            enriched_row = {
                'rank': row['rank'],
                'title': row['title'],
                'img_url': row['img_url'],
                'uniqid': row['uniqid']
            }
            print(f"  No Wikipedia match found for {row['title']}")
        
        enriched_data.append(enriched_row)
        
        # Rate limiting - be nice to Wikipedia
        time.sleep(1)  # 1 request per second
    
    # Create new DataFrame and save
    enriched_df = pd.DataFrame(enriched_data)
    enriched_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Enriched data saved to {output_path}")
    print(f"Summary: {processed_count} new movies processed, {skipped_count} movies skipped (already enriched)")

if __name__ == "__main__":
    try:
        print("Starting Wikipedia movie enrichment...")
        
        enrich_movies_data_wikipedia(
            csv_path="src/assets/data/top100.csv",
            output_path="src/assets/data/top100_wikipedia_enriched.csv",
            max_movies=10  # Start with 10 movies for testing
        )
    except Exception as e:
        print(f"Error: {e}") 