# COVID API Script
This repository contains a Python Flask API for retrieving COVID-related tweets and analyzing their trends, hashtags, likes, and retweets. The API utilizes MongoDB for tweet storage and PostgreSQL for tweet location data storage.

## Packages Needed
To run this script, you need the following packages:

* Flask: A micro web framework for Python.
* pymongo: A Python driver for MongoDB.
* psycopg2: A PostgreSQL adapter for Python.
* geopy: A Python library for geocoding and reverse geocoding.
You can install these packages using pip:

```
pip install Flask pymongo psycopg2 geopy
```

## Use Cases
The COVID API script provides several endpoints to retrieve and analyze COVID-related tweets. Here are the available endpoints and their use cases:

`/test` (GET): Retrieves a combination of data from MongoDB and PostgreSQL for testing purposes. It fetches the first 10 tweets from each database and combines them into a single JSON response.

`/trends` (GET): Retrieves the top trending hashtags based on the provided city and search radius. The endpoint takes three query parameters: city, radius, and n. It uses geocoding to find the specified city's coordinates and then searches for tweets within the given radius. The top n hashtags are returned along with their occurrence count.

`/hashtags` (GET): Searches for tweets with a specific hashtag within the provided city and search radius. The endpoint takes three query parameters: city, radius, and hashtag. It uses geocoding to find the specified city's coordinates and then searches for tweets with the provided hashtag within the given radius. It returns the count of tweets with the hashtag and details of the tweets, including their locations and content.

`/likes` (GET): Retrieves the top n tweets with the most likes based on the provided city and search radius. The endpoint takes three query parameters: city, radius, and n. It uses geocoding to find the specified city's coordinates and then searches for tweets within the given radius. The top n tweets with the most likes are returned, along with their content and like counts.

`/retweets` (GET): Retrieves the top n tweets with the most retweets based on the provided city and search radius. The endpoint takes three query parameters: city, radius, and n. It uses geocoding to find the specified city's coordinates and then searches for tweets within the given radius. The top n tweets with the most retweets are returned, along with their content and retweet counts.

## Examples
Example 1: Retrieving Test Data
Request:

```
GET /test
```

Response:

```
{
  "mongodb_data": [
    {
      "field1": "value1",
      "field2": "value2"
    },
    ...
  ],
  "postgresql_data": [
    {
      "field1": "value1",
      "field2": "value2"
    },
    ...
  ]
}
```

Example 2: Retrieving Top Trending Hashtags
Request:

```
GET /trends?city=New%20York&radius=100&n=5
```
Response:

```
{
  "trends": {
    "hashtag1": 100,
    "hashtag2": 90,
    "hashtag3": 80,
    "hashtag4": 70,
    "hashtag5": 60
  }
}
```

Example 3: Searching for Tweets with a Specific Hashtag
Request:

```
GET /hashtags?city=Los%20Angeles&radius=50&hashtag=covid19
```

Response:

```
{
  "hashtags": {
    "hashtag": "covid19",
    "count": 10,
    "results": {
      "tweet_id1": {
        "location": [longitude, latitude],
        "content": "Tweet content 1"
      },
      "tweet_id2": {
        "location": [longitude, latitude],
        "content": "Tweet content 2"
      },
      ...
    }
  }
}
```

Example 4: Retrieving Top Tweets by Likes
Request:

```
GET /likes?city=Chicago&radius=75&n=3
```

```
{
  "likes": {
    "Top 1": {
      "Likes": 150,
      "Tweet": "Tweet content 1"
    },
    "Top 2": {
      "Likes": 120,
      "Tweet": "Tweet content 2"
    },
    "Top 3": {
      "Likes": 100,
      "Tweet": "Tweet content 3"
    }
  }
}
```

Example 5: Retrieving Top Tweets by Retweets
Request:

```
GET /retweets?city=Miami&radius=60&n=4
```

Response:

```
{
  "retweets": {
    "1": {
      "Retweets": 200,
      "Tweet": "Tweet content 1"
    },
    "2": {
      "Retweets": 180,
      "Tweet": "Tweet content 2"
    },
    "3": {
      "Retweets": 160,
      "Tweet": "Tweet content 3"
    },
    "4": {
      "Retweets": 140,
      "Tweet": "Tweet content 4"
    }
  }
}
```

## Note
Please make sure to have a running MongoDB and PostgreSQL instance with proper configurations before running the API script. Also, adjust the connection parameters according to your database setup.

To run the API, execute the script in your Python environment. The API will be available at http://localhost:5000/. Use the provided examples to access the different endpoints and retrieve data related to COVID-related tweets.