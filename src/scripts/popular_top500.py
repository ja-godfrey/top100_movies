import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

url = "https://www.nytimes.com/interactive/2025/movies/readers-movies-21st-century.html"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(resp.text, "html.parser")

rows = []

# Scrape top 100 movies (they have individual div elements with images)
for row in soup.select("div.row-outer.svelte-1l6f6x5"):
    img = row.select_one("img")
    if not img:
        continue
    
    rank_el = row.select_one(".rank.svelte-1l6f6x5")
    rank = int(rank_el.get_text(strip=True).rstrip('.')) if rank_el else 999
    
    title_el = row.select_one("h3.svelte-1l6f6x5")
    if title_el:
        title_text = title_el.get_text(strip=True)
        title = re.sub(r'^\d+\.\s*', '', title_text)
    else:
        title = ""
    
    img_url = img.get("src", "")
    uniqid = img_url.rstrip("/").split("/")[-1].split(".")[0] if img_url else ""
    
    rows.append({
        "rank": rank,
        "title": title,
        "img_url": img_url,
        "uniqid": uniqid
    })

# Scrape movies 101-500 (they're in a paragraph with spans)
rest_paragraph = soup.select_one("p.rest.svelte-nxbyro")
if rest_paragraph:
    # Find all spans containing movie entries
    spans = rest_paragraph.find_all("span")
    
    for span in spans:
        # Look for span with class "num" (contains rank)
        num_span = span.find("span", class_="num")
        if not num_span:
            continue
            
        rank_text = num_span.get_text(strip=True).rstrip('.')
        try:
            rank = int(rank_text)
        except ValueError:
            continue
            
        # Find the link with the movie title
        link = span.find("a")
        if not link:
            continue
            
        title = link.get_text(strip=True)
        
        rows.append({
            "rank": rank,
            "title": title,
            "img_url": "",  # No images for 101-500
            "uniqid": ""    # No unique IDs for 101-500
        })

# Sort by rank to ensure proper ordering
rows.sort(key=lambda x: x["rank"])

df = pd.DataFrame(rows)
print(f"Scraped {len(df)} movies")
print("DataFrame shape:", df.shape)
print("DataFrame columns:", df.columns.tolist())
print(df.head(10))
print(f"\nLast 10 movies:")
print(df.tail(10))

if df.empty:
    print("WARNING: DataFrame is empty! No data will be saved.")
else:
    out_path = os.path.abspath("./../assets/data/top500.csv")
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"\nSaved to {out_path}")
