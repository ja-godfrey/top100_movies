# Movie Overlap Finder

A single-page web application that helps users find overlapping movie preferences from the top 100 lists collected by the NYT.

## Project Structure

```
top100_movies/
├── README.md                 # This file
├── src/                      # Source code directory
│   ├── index.html            # Main HTML file
│   ├── assets/               # Static assets
│   │   ├── data/             # Data files
│   │   │   ├── top100.csv    # Movie data with rankings
│   │   │   └── jobs.txt      # Job category mappings
│   │   └── images/           # Movie poster images
│   ├── scripts/              # Python scripts for data processing
│   │   ├── scrape_top100.py  # Scrapes movie data from NYT
│   │   ├── scrape_jpgs.py    # Downloads movie poster images
│   │   └── addjobs.py        # Adds job categories to data
│   └── styles/               # CSS files (currently inline)
└── docs/                     # Documentation
    └── questions.md          # Research questions and analysis ideas
```

## Features

- **Dark Mode Interface**: Modern dark theme with smooth animations
- **Search & Filter**: Type to search for movies with real-time filtering
- **Visual Movie Cards**: Display full movie posters for selected films
- **Overlap Analysis**: Find people in the film industry with similar movie preferences
- **Responsive Design**: Works on desktop and mobile devices

## How to Use

1. Open `src/index.html` in a web browser
2. Type in the search box to find movies
3. Click "Add" or press Enter to select a movie
4. Continue adding movies to your selection
5. Click "Find Overlaps" to see which people share your movie preferences

## Data Sources

The application uses data from the New York Times' "The 21st Century's 100 Greatest Films" survey, which includes votes from various film industry professionals including actors, directors, critics, and executives.

## Development

### Data Processing Scripts

- `scrape_top100.py`: Scrapes the original NYT data
- `addjobs.py`: Categorizes people by their job roles
- `scrape_jpgs.py`: Downloads movie poster images

### Running the Scripts

```bash
cd src/scripts
python scrape_top100.py    # Get the base data
python addjobs.py          # Add job categories
python scrape_jpgs.py      # Download images
```

## Browser Compatibility

- Modern browsers with ES6+ support
- Requires internet connection for external fonts and CSV loading 