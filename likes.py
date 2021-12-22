import sys
from pymongo import MongoClient
import psycopg2
from geopy.geocoders import Nominatim
import re
import operator


def main():
    # No arguments were passed
    if len(sys.argv) < 4:
        usage()
    db_url = 'localhost'
    db_port = 27017
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
    radius = str(int(sys.argv[1])*1000)
    city = sys.argv[2]
    n = int(sys.argv[3])

    # PostGIS
    try:
        conn = psycopg2.connect(database='postgres', user='postgres',
                                password='postgres', port=5431, host='localhost')
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
    # La idea es ir metiendo los hashtags en el diccionario y tener un contador.
    tweets_location = {}

    # Table 'tweets' has a geography column 'geog'
    # curs.execute("""\
    # SELECT 'Tweet Id', ST_AsGeoJSON(geog), ST_Distance(geog, point)
    # FROM tweets, (SELECT ST_MakePoint(%s, %s)::geography AS point) AS f
    # WHERE ST_DWithin(geog, point, 1000);""", point)

    curs.execute("SELECT tweet_id, ST_X(geom), ST_Y(geom) FROM tweets WHERE ST_Distance(ST_GeometryFromText('POINT(" +
                 str(location.longitude) + ' ' + str(location.latitude) + ")', 4326)::geography, tweets.geom)<=" + str(radius))

    for row in curs.fetchall():
        tweet_id = row[0]
        location = row[1], row[2]
        tweets_location[tweet_id] = location
    likes_counter = {}
    for tweet_id in tweets_location:
        text = coll.find_one({"Tweet Id": '"' + str(tweet_id) + '"'}, {'Tweet Content': 1,
                             'Screen Name': 1, 'Likes Received': 1, '_id': 0})
        if text != None:
            likes_counter[text['Tweet Content']] = text['Likes Received']
    sorted_likes_counter = sorted(
        likes_counter.items(), key=operator.itemgetter(1), reverse=True)
    print("\nTop " + str(n) + " Tweets by likes:")
    for tuple in sorted_likes_counter[:n]:
        print(tuple[0] + ': ' + str(tuple[1]))


def usage():
    print("Usage:   > trends [radius] [city] [top N]")
    exit()


if __name__ == "__main__":
    main()
