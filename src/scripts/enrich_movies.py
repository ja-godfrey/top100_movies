import pandas as pd
import requests
import time
import json
import os
from typing import Dict, Optional, List

# TMDB API configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def load_api_key() -> str:
    """Load TMDB API key from secrets.txt file"""
    try:
        # Get the path to secrets.txt (two levels up from scripts directory)
        secrets_path = os.path.join(os.path.dirname(__file__), '..', '..', 'secrets.txt')
        
        with open(secrets_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('TMDB_API_KEY='):
                    return line.split('=', 1)[1]
                elif line.startswith('API Key:'):
                    return line.split(':', 1)[1].strip()
        
        raise ValueError("TMDB_API_KEY or API Key not found in secrets.txt")
    except FileNotFoundError:
        raise FileNotFoundError("secrets.txt file not found. Please create it with TMDB_API_KEY=your_key_here")
    except Exception as e:
        raise Exception(f"Error reading API key from secrets.txt: {e}")

def search_movie(title: str, year: Optional[int] = None, api_key: str = None) -> Optional[Dict]:
    """Search for a movie on TMDB and return the first result"""
    if api_key is None:
        api_key = load_api_key()
        
    search_url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': api_key,
        'query': title,
        'language': 'en-US',
        'page': 1,
        'include_adult': False
    }
    
    if year:
        params['year'] = year
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            return data['results'][0]  # Return first result
        return None
    except Exception as e:
        print(f"Error searching for '{title}': {e}")
        return None

def get_movie_details(movie_id: int, api_key: str = None) -> Optional[Dict]:
    """Get detailed movie information including credits"""
    if api_key is None:
        api_key = load_api_key()
        
    # Get movie details
    details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'append_to_response': 'credits'
    }
    
    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting details for movie ID {movie_id}: {e}")
        return None

def extract_movie_info(movie_data: Dict) -> Dict:
    """Extract relevant information from movie data"""
    if not movie_data:
        return {}
    
    # Get directors (by billing order)
    directors = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] == 'Director':
                directors.append(person['name'])
    
    # Get top actors (first 5, by billing order)
    actors = []
    if 'credits' in movie_data and 'cast' in movie_data['credits']:
        actors = [person['name'] for person in movie_data['credits']['cast'][:5]]
    
    # Get cinematographers (by billing order)
    cinematographers = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] == 'Director of Photography':
                cinematographers.append(person['name'])
    
    # Get producers (by billing order)
    producers = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] == 'Producer':
                producers.append(person['name'])
    
    # Get writers (by billing order)
    writers = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] in ['Screenplay', 'Writer', 'Story']:
                writers.append(person['name'])
    
    # Get composers
    composers = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] == 'Original Music Composer':
                composers.append(person['name'])
    
    # Get editors
    editors = []
    if 'credits' in movie_data and 'crew' in movie_data['credits']:
        for person in movie_data['credits']['crew']:
            if person['job'] == 'Editor':
                editors.append(person['name'])
    
    # Get production companies
    production_companies = []
    if 'production_companies' in movie_data:
        production_companies = [company['name'] for company in movie_data['production_companies']]
    
    # Get production countries
    production_countries = []
    if 'production_countries' in movie_data:
        production_countries = [country['name'] for country in movie_data['production_countries']]
    
    # Get spoken languages
    spoken_languages = []
    if 'spoken_languages' in movie_data:
        spoken_languages = [lang['name'] for lang in movie_data['spoken_languages']]
    
    # Get keywords/tags
    keywords = []
    if 'keywords' in movie_data and 'keywords' in movie_data['keywords']:
        keywords = [keyword['name'] for keyword in movie_data['keywords']['keywords']]
    
    return {
        'tmdb_id': movie_data.get('id'),
        'original_title': movie_data.get('original_title'),
        'original_language': movie_data.get('original_language'),
        'release_date': movie_data.get('release_date'),
        'runtime': movie_data.get('runtime'),
        'budget': movie_data.get('budget'),
        'revenue': movie_data.get('revenue'),
        'vote_average': movie_data.get('vote_average'),
        'vote_count': movie_data.get('vote_count'),
        'popularity': movie_data.get('popularity'),
        'overview': movie_data.get('overview'),
        'tagline': movie_data.get('tagline'),
        'status': movie_data.get('status'),
        'adult': movie_data.get('adult'),
        'video': movie_data.get('video'),
        'backdrop_path': movie_data.get('backdrop_path'),
        'poster_path': movie_data.get('poster_path'),
        'imdb_id': movie_data.get('imdb_id'),
        'homepage': movie_data.get('homepage'),
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
        'genres': ', '.join([genre['name'] for genre in movie_data.get('genres', [])]),
        'production_companies': ', '.join(production_companies),
        'production_countries': ', '.join(production_countries),
        'spoken_languages': ', '.join(spoken_languages),
        'keywords': ', '.join(keywords[:10]) if keywords else '',  # Limit to first 10 keywords
        'total_cast_count': len(movie_data.get('credits', {}).get('cast', [])),
        'total_crew_count': len(movie_data.get('credits', {}).get('crew', []))
    }

def enrich_movies_data(csv_path: str, output_path: str, max_movies: int = None):
    """Enrich movie data with TMDB information"""
    # Load API key once
    api_key = load_api_key()
    
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
            if not existing_row.empty and pd.notna(existing_row.iloc[0].get('tmdb_id')):
                print(f"  Skipping {row['title']} - already enriched")
                enriched_data.append(existing_row.iloc[0].to_dict())
                skipped_count += 1
                continue
        
        # Search for movie
        movie_search = search_movie(row['title'], api_key=api_key)
        
        if movie_search:
            # Get detailed information
            movie_details = get_movie_details(movie_search['id'], api_key=api_key)
            movie_info = extract_movie_info(movie_details)
            
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
            print(f"  No TMDB match found for {row['title']}")
        
        enriched_data.append(enriched_row)
        
        # Rate limiting - be nice to the API
        time.sleep(0.25)  # 4 requests per second
    
    # Create new DataFrame and save
    enriched_df = pd.DataFrame(enriched_data)
    enriched_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Enriched data saved to {output_path}")
    print(f"Summary: {processed_count} new movies processed, {skipped_count} movies skipped (already enriched)")

if __name__ == "__main__":
    try:
        # Test API key loading
        api_key = load_api_key()
        print(f"API key loaded successfully (length: {len(api_key)})")
        
        enrich_movies_data(
            csv_path="src/assets/data/top100.csv",
            output_path="src/assets/data/top100_enriched.csv",
            max_movies=100  # Process all 100 movies
        )
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure secrets.txt contains: TMDB_API_KEY=your_actual_api_key") 