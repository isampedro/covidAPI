# CovidAPI

## import.py
Imports data from csv to database in mongoDB and postgres (with postgis addon).

## trends.py
Shows top N trending hashtags in a given area (center + radius).
## retweets.py
Shows top N most retweeted users in a given area (center + radius).
## likes.py
Shows top N most liked users in a given area (center + radius).
#### Default parameters (MongoDB):
- database_name = covid
- collection_name = tweets
- port: 27017

#### Default parameters (PostgreSQL):
- database_name = covid
- table_name = tweets
- port: 5431

#### USAGE: 
* python import.py [path_to_csv]
* python trends.py [radius] [city] [topN]
* python likes.py [radius] [city] [topN]
* python retweets.py [radius] [city] [topN]