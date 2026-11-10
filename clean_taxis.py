"""NYC taxi trips: profile, clean, check and load into SQLite."""
import sqlite3
import time
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "taxis_raw.csv"
DB_PATH = BASE_DIR / "data" / "taxi.db"
URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/taxis.csv"


# ---------- EXTRACT ----------
def get_raw_data():
    """Use the local file if it exists, otherwise download it."""
    if not RAW_PATH.exists():
        print("Downloading raw data...")
        for attempt in range(1, 4):
            try:
                resp = requests.get(URL, timeout=60)
                resp.raise_for_status()
                RAW_PATH.parent.mkdir(exist_ok=True)
                RAW_PATH.write_bytes(resp.content)
                break
            except requests.exceptions.RequestException:
                print(f"  Attempt {attempt}/3 failed")
                if attempt == 3:
                    raise
                time.sleep(5)
    return pd.read_csv(RAW_PATH)


# ---------- PROFILE ----------
def profile(df):
    """Print what is wrong with the raw data before cleaning."""
    print(f"Raw data: {len(df)} rows, {df.shape[1]} columns")
    print("Missing values per column:")
    print(df.isnull().sum()[df.isnull().sum() > 0].to_string())
    print(f"Duplicate rows: {df.duplicated().sum()}")


# ---------- CLEAN ----------
def clean(df):
    df = df.copy()
    df["pickup"] = pd.to_datetime(df["pickup"])
    df["dropoff"] = pd.to_datetime(df["dropoff"])
    df["trip_minutes"] = ((df["dropoff"] - df["pickup"]).dt.total_seconds() / 60).round(2)

    # Find rows that cannot be real trips and record why
    reasons = pd.Series("", index=df.index)
    reasons[df["distance"] <= 0] += "zero_distance;"
    reasons[df["trip_minutes"] <= 0] += "zero_duration;"
    reasons[df["passengers"] == 0] += "zero_passengers;"
    speed = df["distance"] / (df["trip_minutes"] / 60).where(df["trip_minutes"] > 0)
    reasons[speed > 80] += "impossible_speed;"
    rejected = df[reasons != ""].copy()
    rejected["reason"] = reasons[reasons != ""].str.rstrip(";")
    good = df[reasons == ""].copy()

    # Fill missing text values with a clear label instead of leaving blanks
    for col in ["payment", "pickup_zone", "dropoff_zone", "pickup_borough", "dropoff_borough"]:
        good[col] = good[col].fillna("Unknown")

    # New columns that make analysis easier
    good["pickup_date"] = good["pickup"].dt.strftime("%Y-%m-%d")
    good["pickup_hour"] = good["pickup"].dt.hour
    good["pickup_day"] = good["pickup"].dt.day_name()
    good["tip_pct"] = (good["tip"] / good["fare"] * 100).round(1)
    good["pickup"] = good["pickup"].dt.strftime("%Y-%m-%d %H:%M:%S")
    good["dropoff"] = good["dropoff"].dt.strftime("%Y-%m-%d %H:%M:%S")
    rejected["pickup"] = rejected["pickup"].dt.strftime("%Y-%m-%d %H:%M:%S")
    rejected["dropoff"] = rejected["dropoff"].dt.strftime("%Y-%m-%d %H:%M:%S")

    print(f"Cleaning: kept {len(good)} rows, rejected {len(rejected)} rows")
    print(rejected["reason"].value_counts().to_string())
    return good.reset_index(drop=True), rejected.reset_index(drop=True)


# ---------- CHECK ----------
def quality_checks(df):
    problems = []
    if df.empty:
        problems.append("no rows left after cleaning")
    if df[["pickup", "dropoff", "distance", "fare", "total"]].isnull().any().any():
        problems.append("nulls in required columns")
    if (df["trip_minutes"] <= 0).any():
        problems.append("trips with zero or negative duration")
    if (df["distance"] <= 0).any():
        problems.append("trips with zero distance")
    if not df["passengers"].between(1, 6).all():
        problems.append("passengers outside 1-6")
    if (df["total"] < df["fare"]).any():
        problems.append("total is lower than fare")
    if problems:
        raise ValueError("Quality check failed: " + "; ".join(problems))
    print("Quality checks passed.")


# ---------- LOAD ----------
def load(good, rejected):
    with sqlite3.connect(DB_PATH) as conn:
        good.to_sql("trips", conn, if_exists="replace", index=False)
        rejected.to_sql("rejected_trips", conn, if_exists="replace", index=False)
    print(f"Loaded {len(good)} trips and {len(rejected)} rejected rows into taxi.db")


def run():
    raw = get_raw_data()
    profile(raw)
    good, rejected = clean(raw)
    quality_checks(good)
    load(good, rejected)


if __name__ == "__main__":
    run()
