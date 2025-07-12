import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.nytimes.com/interactive/2025/movies/votes-movies-21st-century.html"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(resp.text, "html.parser")

rows = []
for person in soup.select("div.person-box"):
    name = person.select_one("h2").get_text(strip=True)
    for box in person.select(".movies-wrapper .grid-item"):
        img = box.select_one("img")
        if not img:
            continue

        rank_el = box.select_one(".top-position span")
        rank = int(rank_el.get_text(strip=True)) if rank_el else 999

        alt = img.get("alt", "")
        title = alt.replace("movie cover for ", "").rsplit(" by", 1)[0]

        img_url = img["src"]
        uniqid = img_url.rstrip("/").split("/")[-1].split(".")[0]

        rows.append({
            "person": name,
            "rank": rank,
            "title": title,
            "img_url": img_url,
            "uniqid": uniqid
        })

df = pd.DataFrame(rows)
print(df.head())
df.to_csv("top100.csv", index=False)
