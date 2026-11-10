# NYC Taxi Data Cleaning

A small beginner project where I take a real, messy dataset of New York City taxi trips, find what is wrong with it, clean it, and answer questions with SQL.

## What I wanted to learn
- How to check a dataset for problems before using it
- How to clean data with Pandas and keep a record of what was removed
- How to store clean data in a database and query it with SQL

## What the project does
1. Reads 6,433 taxi trips (March 2019).
2. Finds the problems: missing payment types and zones, trips with zero distance, trips with zero passengers, and trips with impossible speeds.
3. Removes 156 bad rows and saves them in a separate `rejected_trips` table with the reason.
4. Fills missing zones and payment types with "Unknown" and adds new columns (trip minutes, pickup hour, day of week, tip percentage).
5. Checks the clean data again, then loads it into SQLite.
6. Runs 9 SQL queries to answer questions.

## Questions I answered
- Which boroughs and zones have the most pickups?
- What are the busiest hours of the day?
- How do tips differ by payment type?
- How do yellow and green taxis compare?

## A few results
- 6,277 of 6,433 trips were kept after cleaning.
- The busiest pickup hour was 6 pm.
- Queens trips had a much higher average fare than Manhattan trips, mainly because of the airports.
- Credit card trips had an average tip of about 24%. Cash trips show a tip of 0 in this data.

## Tools
Python, Pandas, SQLite, SQL

## How to run
pip install -r requirements.txt
python src/clean_taxis.py
python src/run_queries.py

## Files
- data/taxis_raw.csv: the raw data
- src/clean_taxis.py: profiles, cleans, checks and loads the data
- src/run_queries.py: runs the SQL queries
- sql/queries.sql: the analysis queries

## What I'd like to improve
- Add a chart for trips by hour
- Try the same cleaning on a bigger dataset

## Data source
NYC Taxi and Limousine Commission trip records, as provided in the seaborn-data sample (github.com/mwaskom/seaborn-data).
