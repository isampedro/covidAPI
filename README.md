# CovidAPI

## Modules Description

### import.py

Imports data from csv to database in mongoDB and postgres (with postgis addon).

### trends.py

Shows top N trending hashtags in a given area (center + radius).

### retweets.py

Shows top N most retweeted contents in a given area (center + radius).

### likes.py

Shows top N most liked contents in a given area (center + radius).

### hashtags.py

Shows the times that a hashtag appears in a given area (center + radius).


## Instructions

### Installing necessary modules
On terminal, run the following commands:
> pip install psycopg2 <br />
> pip install pymongo <br />
> pip install geopy <br />

## Usage

- python import.py [path_to_csv]
- python trends.py [radius] [city] [topN]
- python likes.py [radius] [city] [topN]
- python retweets.py [radius] [city] [topN]
- python retweets.py [radius] [city] [hashtag]

## Additional Information

#### Default parameters (MongoDB)

- database_name = covid
- collection_name = tweets
- port: 27017

#### Default parameters (PostgreSQL)

- database_name = covid
- table_name = tweets
- port: 5431

#### Notes

- Radius is in kilometres.
- If the city (or country or map search query) is larger that 1 word, the way you pass it is like 'name of city'.
- For map search queries, the [geopy](https://geopy.readthedocs.io/en/stable/) Python library has been used, with queries in [Nominatim](https://nominatim.org/).
