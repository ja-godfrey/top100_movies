import pandas as pd

df = pd.read_csv("top100.csv")

job_map = {}
with open("jobs.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or "\t" not in line:
            continue
        category, names = line.split("\t", 1)
        for name in names.split(","):
            job_map[name.strip()] = category

df["job"] = df["person"].map(job_map).fillna("Unknown")

df.to_csv("test.csv", index=False)
