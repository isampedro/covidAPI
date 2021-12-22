from typing import Collection
from numpy.core.numeric import NaN
import pandas as pd
from pymongo import MongoClient
import json
import sys
import psycopg2
from geopy.geocoders import Nominatim
import math


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "./COVID.csv"
    print("Importing data from " + file_path)
    db_name = "postgres"
    collection_name = "tweets"
    try:
        print(str(mongoimport(file_path, db_name, collection_name)) +
            " documents were added.")
        postgisimport(file_path, db_name, collection_name, 5431)
    except Exception as e:
        print(str(e))
        print("No such file or directory.")


def postgisimport(csv_path, db_name, table_name, db_port=5431):
    geolocator = Nominatim(
        user_agent="covidAPI")
    conn = psycopg2.connect(
        dbname=db_name, port=db_port, user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    df = pd.read_csv(csv_path)

    for i, row in df.iterrows():
        if(i % 500 == 0):
            conn.commit()
            print("nice")
        if not math.isnan(row.Lat) and not math.isnan(row.Long):
            cur.execute("INSERT INTO " + table_name + " VALUES (" + str(row['Tweet Id'].strip('"')) +
                        "," + "ST_GeomFromText('POINT(" + str(row.Long) + ' ' + str(row.Lat) + ")', 4326))")
        elif row['Tweet Location'] != NaN:
            try:
                location = geolocator.geocode(row['Tweet Location'])
            except Exception as e:
                print(e)
            if location != None:
                long = location.longitude
                lat = location.latitude
                cur.execute("INSERT INTO " + table_name + " VALUES (" + row['Tweet Id'].strip('"') +
                            "," + "ST_GeomFromText('POINT(" + str(long) + ' ' + str(lat) + ")', 4326))")

    return cur.execute("SELECT COUNT(*) FROM" + table_name)


def mongoimport(csv_path, db_name, coll_name, db_url='localhost', db_port=27017):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    client = MongoClient(db_url, db_port)
    # To delete database
    # client.drop_database('covid')
    db = client[db_name]
    coll = db[coll_name]
    # To drop collection
    coll.drop()
    data = pd.read_csv(csv_path)
    payload = json.loads(data.to_json(orient='records'))
    coll.delete_many({})
    coll.insert_many(payload)
    return coll.count_documents({})


if __name__ == "__main__":
    main()
