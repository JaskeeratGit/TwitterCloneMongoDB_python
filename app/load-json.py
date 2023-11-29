import json
import pymongo
from pymongo import MongoClient
import sys

def load_json(json_file, mongo_uri):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    
    # Create or get the database
    db = client["291db"]
    
    # Drop existing collection and create a new one
    db.tweets.drop()
    tweets_collection = db["tweets"]
    
    # Create indexes
    tweets_collection.create_index([("displayname", pymongo.TEXT), ("location", pymongo.TEXT)], name="displayname_location_text_index")
    tweets_collection.create_index([("retweetCount", pymongo.DESCENDING)], name="retweetCount_index")
    tweets_collection.create_index([("likeCount", pymongo.DESCENDING)], name="likeCount_index")
    tweets_collection.create_index([("quoteCount", pymongo.DESCENDING)], name="quoteCount_index")
    tweets_collection.create_index([("followersCount", pymongo.DESCENDING)], name="followersCount_index")
    
    # Batch insert data into MongoDB
    batch_size = 1000
    batch = []

    with open(json_file, 'r', encoding='utf-8') as file:
        for line in file:
            tweet = json.loads(line)
            batch.append(tweet)

            if len(batch) == batch_size:
                tweets_collection.insert_many(batch)
                batch = []

        # Insert any remaining documents
        if batch:
            tweets_collection.insert_many(batch)

    print("Data loaded successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python load_json.py <json_file> <mongo_uri>")
        sys.exit(1)

    json_file = sys.argv[1]
    mongo_uri = sys.argv[2]

    load_json(json_file, mongo_uri)
