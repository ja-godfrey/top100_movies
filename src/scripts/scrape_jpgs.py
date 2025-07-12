import os
import requests
import pandas as pd

df = pd.read_csv("top100.csv", usecols=["uniqid", "img_url"])

os.makedirs("images", exist_ok=True)

for _, row in df.iterrows():
    uniqid = row["uniqid"]
    url = row["img_url"]
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    out_path = os.path.join("images", f"{uniqid}.png")
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
