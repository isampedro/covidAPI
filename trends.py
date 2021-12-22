import sys
from pymongo import MongoClient
import psycopg2
from geopy.geocoders import Nominatim
import re
import operator

def main():
    # No arguments were passed
    if len(sys.argv) < 3:
        usage()
    db_url='localhost'
    db_port=27017
    try:
        client = MongoClient(db_url, db_port)
        print("Connected to MongoDB.")
    except:
        print("Could not connect to MongoDB.")
    db_name = "covid"
    collection_name = "tweets"
    db = client[db_name]
    coll = db[collection_name]
    # TODO: Check for valid parameters
    radius = sys.argv[1]
    city = sys.argv[2]

    # PostGIS
    try:
        conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', port=5431, host='localhost')
        print("Connected to PostGIS.")
        curs = conn.cursor()
    except Exception as e:
        print(str(e))
        #print("Could not connect to PostGIS.")

    # Geolocator
    geolocator = Nominatim(user_agent="covidAPI")
    location = geolocator.geocode(city)
    point = location.longitude, location.latitude
    print("City coord: " + str(point))
    # Key --> Tweet_ID , Value --> Location(lat, long)
    tweets_location = {} # La idea es ir metiendo los hashtags en el diccionario y tener un contador.

    # Table 'tweets' has a geography column 'geog'
    # curs.execute("""\
    # SELECT 'Tweet Id', ST_AsGeoJSON(geog), ST_Distance(geog, point)
    # FROM tweets, (SELECT ST_MakePoint(%s, %s)::geography AS point) AS f
    # WHERE ST_DWithin(geog, point, 1000);""", point)

    curs.execute("SELECT tweet_id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" + str(location.longitude) + ' ' + str(location.latitude) + ")', 4326)::geography, tweets.geom)<=" + str(radius))

    for row in curs.fetchall():
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location
    hashtags_counter = {}
    for tweet_id in tweets_location:
        text = coll.find_one({"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1, '_id':0})
        if text != None:
            hashtags = re.findall(r"#(\w+)", text['Tweet Content'])
            for hashtag in hashtags:
                if hashtag in hashtags_counter:
                    hashtags_counter[hashtag] = hashtags_counter[hashtag] + 1
                else:
                    hashtags_counter[hashtag] = 1
    sorted_hashtags_counter = sorted(hashtags_counter.items(), key=operator.itemgetter(1), reverse=True)
    print("Trending hashtags:")
    for tuple in sorted_hashtags_counter:
        print(tuple[0] + ': ' + str(tuple[1]))

def usage():
    print("Usage:   > trends [radius] [city]")
    exit()

if __name__ == "__main__":
    main()