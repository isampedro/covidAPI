from typing import Collection
import pandas as pd
from pymongo import MongoClient
import json
import sys

def main():
    if len(sys.argv) > 0:
        file_path = sys.argv[1]
    else:
        file_path = "./COVID.csv"
    print("Importing data from " + file_path)
    db_name = "covid"
    collection_name = "tweets"
    try:
        print(str(mongoimport(file_path, db_name, collection_name)) + " documents were added.")
    except:
        print("No such file or directory.")

def mongoimport(csv_path, db_name, coll_name, db_url='localhost', db_port=27017):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    client = MongoClient(db_url, db_port)
    ###  To delete database
    # client.drop_database('covid')
    db = client[db_name]
    coll = db[coll_name]
    ### To drop collection
    coll.drop()
    data = pd.read_csv(csv_path)
    payload = json.loads(data.to_json(orient='records'))
    coll.delete_many({})
    coll.insert_many(payload)
    return coll.count_documents({})

if __name__ == "__main__":
    main()
