from flask import Flask, jsonify, request
import pymongo
import psycopg2.pool
from geopy.geocoders import Nominatim
import operator
import re

app = Flask(__name__)

# Configuration for MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB_NAME = 'covid'
MONGO_COLLECTION_NAME = 'tweets'

# Configuration for PostgreSQL
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = '5432'
POSTGRESQL_DB_NAME = 'covid'
POSTGRESQL_USER = 'root'
POSTGRESQL_PASSWORD = 'root'
POSTGRESQL_TABLE_NAME = 'tweets'



# MongoDB connection pool
mongo_pool_size = 10  # You can adjust the pool size as needed
mongo_client = pymongo.MongoClient('localhost',27017, maxPoolSize=mongo_pool_size)

# PostgreSQL connection pool
conn_string = f"host={POSTGRESQL_HOST} port={POSTGRESQL_PORT} dbname={POSTGRESQL_DB_NAME} user={POSTGRESQL_USER} password={POSTGRESQL_PASSWORD}"
postgresql_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=conn_string)



#@app.teardown_appcontext
#def close_db_connections(error):
#    # Close database connections at the end of the application context
#    global mongo_client

#    if mongo_client is not None:
#        mongo_client.close()
#        mongo_client = None



@app.route('/test', methods=['GET'])
def get_test():
    # Connecting to MongoDB and retrieving data
    mongodb = mongo_client[MONGO_DB_NAME]
    mongodb_collection= mongodb[MONGO_COLLECTION_NAME]
    #print("mongo_coll: "+str(mongodb_collection))
    mongo_data = list(mongodb_collection.find({}, {'_id': 0}).limit(10))
    #print("mongo-data: "+str(mongo_data))

    # Connecting to PostgreSQL and retrieving data
    postgresql_connection = postgresql_pool.getconn()
    postgresql_cursor = postgresql_connection.cursor()
    postgresql_cursor.execute(f"SELECT * FROM {POSTGRESQL_TABLE_NAME} LIMIT 10")
    postgresql_data = [dict(zip([column[0] for column in postgresql_cursor.description], row)) for row in postgresql_cursor.fetchall()]
    postgresql_cursor.close()
    postgresql_pool.putconn(postgresql_connection)

    # Combine and return data
    combined_data = {
        "mongodb_data": mongo_data,
        "postgresql_data": postgresql_data
    }

    return jsonify(combined_data)


@app.route('/trends', methods=['GET'])
def get_trends():
    # Get query parameters from the URL
    radius = request.args.get('radius')
    city = request.args.get('city')
    n = int(request.args.get('n'))

    try:
        # Geolocator
        geolocator = Nominatim(user_agent="covidAPI")
        location = geolocator.geocode(city)
        point = location.longitude, location.latitude
    except Exception as e:
        # Handle the exception and set default longitude and latitude values
        point = -58.4370894, -34.6075682

    tweets_location = {}
    # PostgreSQL query with parameters
    postgresql_connection = postgresql_pool.getconn()
    postgresql_cursor = postgresql_connection.cursor()
    postgresql_query = "SELECT id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" + str(point[0]) + ' ' + str(point[1]) + ")', 4326)::geography, tweets.geom)<=" + str(radius)
    #print(postgresql_query)
    postgresql_cursor.execute(postgresql_query)
    postgresql_data = postgresql_cursor.fetchall()
    postgresql_cursor.close()
    postgresql_pool.putconn(postgresql_connection)


    # MongoDB query with parameters
    mongodb =  mongo_client[MONGO_DB_NAME]
    mongodb_collection = mongodb[MONGO_COLLECTION_NAME]
    #mongodb_query = {}
    #mongo_data = list(mongodb_collection.find(mongodb_query, {'_id': 0}).limit(10))


    tweets_location = {}
    for row in postgresql_data:
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location

    hashtags_counter = {}
    for tweet_id in tweets_location:
        text = mongodb_collection.find_one(
            {"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1, '_id': 0})
        if text is not None:
            hashtags = re.findall(r"#(\w+)", text['Tweet Content'])
            for hashtag in hashtags:
                if hashtag in hashtags_counter:
                    hashtags_counter[hashtag] += 1
                else:
                    hashtags_counter[hashtag] = 1

    sorted_hashtags_counter = sorted(
        hashtags_counter.items(), key=operator.itemgetter(1), reverse=True)

    # Storing the top n trending hashtags and their counts in a dictionary
    trending_hashtags = {}
    for hashtag, count in sorted_hashtags_counter[:n]:
        trending_hashtags[hashtag] = count

    #print("\nTop " + str(n) + " Trending hashtags:")
    #print(trending_hashtags)


    # Combine and return data
    combined_data = {
        "trends": trending_hashtags
    }

    return jsonify(combined_data)

@app.route('/hashtags', methods=['GET'])
def get_hashtags():
    # Get query parameters from the URL
    radius = request.args.get('radius')
    city = request.args.get('city')
    hashtag = request.args.get('hashtag')

    try:
        # Geolocator
        geolocator = Nominatim(user_agent="covidAPI")
        location = geolocator.geocode(city)
        point = location.longitude, location.latitude
    except Exception as e:
        # Handle the exception and set default longitude and latitude values
        point = -58.4370894, -34.6075682

    tweets_location = {}

    # PostgreSQL query with parameters
    postgresql_connection = postgresql_pool.getconn()
    postgresql_cursor = postgresql_connection.cursor()
    postgresql_query = "SELECT id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" + str(point[0]) + ' ' + str(point[1]) + ")', 4326)::geography, tweets.geom)<=" + str(radius)
    #print(postgresql_query)
    postgresql_cursor.execute(postgresql_query)
    postgresql_data = postgresql_cursor.fetchall()
    postgresql_cursor.close()
    postgresql_pool.putconn(postgresql_connection)


    # MongoDB query with parameters
    mongodb =  mongo_client[MONGO_DB_NAME]
    mongodb_collection = mongodb[MONGO_COLLECTION_NAME]
    #mongodb_query = {}
    #mongo_data = list(mongodb_collection.find(mongodb_query, {'_id': 0}).limit(10))


    tweets_location = {}
    for row in postgresql_data:
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location
        #print(str(tweets_location))

    hashtag_count = 0
    hashtag_results = {}

    for tweet_id in tweets_location:
        text = mongodb_collection.find_one({"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1, '_id': 0})
        if text is not None:
            hashtags = re.findall(r"#(\w+)", text['Tweet Content'])
            if hashtag in hashtags:
                hashtag_count += 1
                hashtag_results[tweet_id] = {'location': tweets_location[tweet_id], 'content': text['Tweet Content']}

    result_dict = {"hashtag": hashtag, "count": hashtag_count, "results": hashtag_results}


    # Combine and return data
    combined_data = {
        "hashtags": result_dict
    }

    return jsonify(combined_data)

@app.route('/likes', methods=['GET'])
def get_likes():
    # Get query parameters from the URL
    radius = request.args.get('radius')
    city = request.args.get('city')
    n = int(request.args.get('n'))

    try:
        # Geolocator
        geolocator = Nominatim(user_agent="covidAPI")
        location = geolocator.geocode(city)
        point = location.longitude, location.latitude
    except Exception as e:
        # Handle the exception and set default longitude and latitude values
        point = -58.4370894, -34.6075682

    tweets_location = {}

    # PostgreSQL query with parameters
    postgresql_connection = postgresql_pool.getconn()
    postgresql_cursor = postgresql_connection.cursor()
    postgresql_query = "SELECT id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" + str(point[0]) + ' ' + str(point[1]) + ")', 4326)::geography, tweets.geom)<=" + str(radius)
    #print(postgresql_query)
    postgresql_cursor.execute(postgresql_query)
    postgresql_data = postgresql_cursor.fetchall()
    #print(str(postgresql_data))
    postgresql_cursor.close()
    postgresql_pool.putconn(postgresql_connection)


    # MongoDB query with parameters
    mongodb =  mongo_client[MONGO_DB_NAME]
    mongodb_collection = mongodb[MONGO_COLLECTION_NAME]

    tweets_location = {}
    for row in postgresql_data:
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location

    likes_counter = {}
    for tweet_id in tweets_location:
        text = mongodb_collection.find_one({"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1,
                             'Screen Name': 1, 'Likes Received': 1, '_id': 0})
        #text = mongodb_collection.find_one({"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1, '_id': 0})
        print("TEXT")
        print(str(text))
        print(str(tweet_id))
        if text is not None:
            likes_counter[text['Tweet Content']] = text['Likes Received']

    sorted_likes_counter = sorted(likes_counter.items(), key=operator.itemgetter(1), reverse=True)
    #print("sorted likes")
    #print(str(sorted_likes_counter))

    # Storing the top n tweets by likes in a dictionary
    top_tweets_by_likes = {}
    for idx, (tweet_content, likes) in enumerate(sorted_likes_counter[:n], 1):
        tweet_info = {
            "Likes": likes,
            "Tweet": tweet_content
        }
        top_tweets_by_likes[f"Top {idx}"] = tweet_info
    
    return jsonify(top_tweets_by_likes)

@app.route('/retweets', methods=['GET'])
def get_retweets():
    # Get query parameters from the URL
    radius = request.args.get('radius')
    city = request.args.get('city')
    n = int(request.args.get('n'))

    try:
        # Geolocator
        geolocator = Nominatim(user_agent="covidAPI")
        location = geolocator.geocode(city)
        point = location.longitude, location.latitude
    except Exception as e:
        # Handle the exception and set default longitude and latitude values
        point = -58.4370894, -34.6075682

    tweets_location = {}

    # PostgreSQL query with parameters
    postgresql_connection = postgresql_pool.getconn()
    postgresql_cursor = postgresql_connection.cursor()
    postgresql_query = "SELECT id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" + str(point[0]) + ' ' + str(point[1]) + ")', 4326)::geography, tweets.geom)<=" + str(radius)
    #print(postgresql_query)
    postgresql_cursor.execute(postgresql_query)
    postgresql_data = postgresql_cursor.fetchall()
    postgresql_cursor.close()
    postgresql_pool.putconn(postgresql_connection)


    # MongoDB query with parameters
    mongodb =  mongo_client[MONGO_DB_NAME]
    mongodb_collection = mongodb[MONGO_COLLECTION_NAME]
    #mongodb_query = {}
    #mongo_data = list(mongodb_collection.find(mongodb_query, {'_id': 0}).limit(10))


    tweets_location = {}
    for row in  postgresql_data:
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location

    retweets_counter = {}
    for tweet_id in tweets_location:
        text = mongodb_collection.find_one({"Tweet Id": '"' + str(tweet_id) + '"'},
                             {'Screen Name': 1, 'Retweets Received': 1, 'Tweet Content': 1, '_id': 0})
        if text is not None:
            retweets_counter[text['Tweet Content']] = text['Retweets Received']

    sorted_retweets_counter = sorted(
        retweets_counter.items(), key=operator.itemgetter(1), reverse=True)

    # Storing the top 'n' tweets by retweets in a dictionary
    top_n_tweets = {}
    for i, tuple in enumerate(sorted_retweets_counter[:n], 1):
        tweet_content = tuple[0]
        retweets_count = tuple[1]
        top_n_tweets[i] = {
            'Retweets': retweets_count,
            'Tweet': tweet_content
        }


    # Combine and return data
    combined_data = {
        "retweets": top_n_tweets
    }

    return jsonify(combined_data)


if __name__ == '__main__':
    app.run(debug=True)
