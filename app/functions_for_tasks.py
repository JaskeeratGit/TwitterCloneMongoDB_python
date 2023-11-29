import pymongo
from pymongo import MongoClient
import sys
from datetime import datetime
import re

def search_tweets(keywords, mongo_uri):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    
    # Create or get the database
    db = client["291db"]

    # Get the tweets collection
    tweets_collection = db["tweets"]

    # Build a case-insensitive regex for ma tching keywords as separate words in the content
    query = {"content": {"$regex": r'\b' + r'\b.*\b'.join(map(re.escape, keywords)) + r'\b', "$options": "i"}}

    # Execute the query and retrieve matching tweets
    matching_tweets = tweets_collection.find(query, {"_id": 1, "date": 1, "content": 1, "username": 1})

    # Display the matching tweets
    for tweet in matching_tweets:
        print("Tweet ID:", tweet["_id"])
        print("Date:", tweet["date"])
        print("Content:", tweet["content"])
        # Use get method to handle the case where 'username' key may not exist
        print("Username:", tweet.get("username", "N/A"))
        print("\n")

def list_top_tweets(mongo_uri, n):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    # Connect to the database
    db = client["291db"]
    tweets_collection = db["tweets"]

    # Display menu for selecting the field to order by
    print("Select a field to order by:")
    print("1. retweetCount")
    print("2. likeCount")
    print("3. quoteCount")

    # Get user choice
    user_choice = input("Enter the number corresponding to the field: ").strip()

    # Map user choice to field
    field_mapping = {"1": "retweetCount", "2": "likeCount", "3": "quoteCount"}
    selected_field = field_mapping.get(user_choice)

    # Check if the choice is valid
    if selected_field is None:
        print("Invalid choice. Please enter a valid number.")
        sys.exit(1)

    # Create an index dictionary for mapping user input to the corresponding index
    index_dict = {
        "retweetCount": "retweetCount_index",
        "likeCount": "likeCount_index",
        "quoteCount": "quoteCount_index"
    }

    # Check if the selected field is valid
    if selected_field not in index_dict:
        print("Invalid field selected.")
        return

    # Get the index name based on the selected field
    index_name = index_dict[selected_field]

    # Get the top n tweets based on the selected field
    top_tweets = tweets_collection.find().sort([(selected_field, pymongo.DESCENDING)]).limit(n)

    # Display the information for each top tweet
    for i, tweet in enumerate(top_tweets, start=1):
        print(f"{i}. Tweet ID: {tweet.get('id', 'N/A')}, Date: {tweet.get('date', 'N/A')}, Content: {tweet.get('content', 'N/A')}, Username: {tweet.get('user', {}).get('username', 'N/A')}, {selected_field}: {tweet.get(selected_field, 'N/A')}")

    # Allow the user to select a tweet and see all fields
    selected_tweet_id = input("Enter the Tweet ID to see all fields: ").strip()

    # Find the selected tweet by ID
    selected_tweet = tweets_collection.find_one({"id": int(selected_tweet_id)})

    # Display all fields for the selected tweet
    if selected_tweet:
        print("Selected Tweet:")
        for key, value in selected_tweet.items():
            print(f"{key}: {value}")
    else:
        print("Tweet not found.")

def get_full_user_info(mongo_uri, username):
    #Connect to MongoDB database
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))    
    db = client["291db"]
    tweets_collection = db["tweets"]

    # Find user by username
    user_info = tweets_collection.find_one({"user.username": username})

    # Print the full user information
    if user_info:
        print("\nFull user information:")
        for key, value in user_info['user'].items():
            print(f"{key}: {value}")
        # Add more fields as needed
    else:
        print("User not found.")

def search_and_view_users(keyword, mongo_uri):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    
    # Create or get the database
    db = client["291db"]

    # Get the tweets collection
    tweets_collection = db["tweets"]

    # Build a query for the keyword using a case-insensitive regex
    regex_pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    query = {
        "$or": [
            {"user.displayname": {"$regex": regex_pattern}},
            {"user.location": {"$regex": regex_pattern}}
        ]
    }

    # Projection to include all fields
    projection = {"_id": 0}

    # Execute the query and retrieve matching users
    matching_users = tweets_collection.find(query, projection).sort([("user.followersCount", pymongo.DESCENDING)])

    # Display the matching users
    unique_users = {}  # To store unique users with max followersCount
    for user in matching_users:
        username = user["user"]["username"]
        followers_count = user["user"]["followersCount"]
        
        if username not in unique_users or followers_count > unique_users[username]["user"]["followersCount"]:
            unique_users[username] = user

    for i, user in enumerate(unique_users.values(), 1):
        print(f"{i}. Username: {user['user']['username']}, Display Name: {user['user']['displayname']}, Location: {user['user']['location']}")

    # Prompt user to select a user
    if unique_users:
        while True:
            user_choice = input("\nSelect a user (enter the corresponding number) or press Enter to exit: ")
            if not user_choice:
                sys.exit(0)  # Exit if the user presses Enter
            if re.match("^[1-9][0-9]*$", user_choice):
                user_choice = int(user_choice)
                if 1 <= user_choice <= len(unique_users):
                    selected_user = list(unique_users.values())[user_choice - 1]
                    username = selected_user["user"]["username"]
                    get_full_user_info(mongo_uri, username)
                    break
                else:
                    print("Invalid input. Please enter a valid number.")
            else:
                print("Invalid input. Please enter a valid number.")

def compose_and_insert_tweet(content, mongo_uri):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    
    # Create or get the database
    db = client["291db"]
    
    # Get the tweets collection
    tweets_collection = db["tweets"]

    # Compose the tweet
    tweet = {
        "content": content,
        "date": datetime.now(),  # Use datetime class explicitly
        "username": "291user",
        "displayname": None,
        "location": None,
        "followersCount": None,
        "likeCount": None,
        "quoteCount": None,
        "retweetCount": None
    }

    # Insert the tweet into the database
    tweets_collection.insert_one(tweet)

    print("Tweet inserted successfully.")

#keywords = ["are"]
#mongo_uri = 27017
#content = "AYO THIS GUY IS CRACKED"
#keyword = "kaur"

#search_and_view_users(keyword, mongo_uri)
#search_tweets(keywords, mongo_uri)
#list_top_tweets(mongo_uri, 3)
#list_top_users(mongo_uri, 3)
#compose_and_insert_tweet(content, mongo_uri)
