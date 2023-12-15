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

    # Build a list of conditions for $and with $regex for each keyword
    conditions = [{"content": {"$regex": rf'\b{re.escape(keyword)}\b', "$options": "i"}} for keyword in keywords]

    # Execute the query and retrieve matching tweets with the 'user' field
    query = {"$and": conditions}
    matching_tweets = list(tweets_collection.find(query, {"_id": 1, "date": 1, "content": 1, "user": 1, "url": 1, "replyCount": 1, "retweetCount": 1, "likeCount": 1, "quoteCount": 1}))

    # Display the matching tweets with an index
    for index, tweet in enumerate(matching_tweets, start=1):
        print(f"{index}. Tweet ID: {tweet['_id']}, Date: {tweet['date']}, Content: {tweet['content']}, Username: {tweet['user'].get('username', 'N/A')}")

    # Allow the user to select a tweet by index
    try:
        selected_index = int(input("Enter the number of the tweet to see all fields (or press Enter to skip): ").strip()) - 1
        selected_tweet = matching_tweets[selected_index] if 0 <= selected_index < len(matching_tweets) else None

        if selected_tweet:
            print("\nAll Fields for Selected Tweet:")
            for field, value in selected_tweet.items():
                print(f"{field}: {value}")
        else:
            print("Invalid selection. Tweet not found.")
    except ValueError:
        print("No tweet selected.")
    client.close()

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
        return

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
    x=True
    while x==True:
        try:
            selected_rank = int(input("Enter the rank of the tweet to see all fields (or press Enter to exit): ").strip())
            if 1 <= selected_rank <= n:
                break
            else:
                print("Invalid rank. Please enter a valid rank.")
                x = False
                return
        except ValueError:
            print("Invalid input. Please enter a valid rank.")
            x = False
            return

    # Find the selected tweet by rank
    selected_tweet = tweets_collection.find().sort([(selected_field, pymongo.DESCENDING)]).skip(selected_rank - 1).limit(1)

    # Display all fields for the selected tweet
    for tweet in selected_tweet:
        print("Selected Tweet:")
        for key, value in tweet.items():
            print(f"{key}: {value}")
    client.close()

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
    client.close()

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
                return # Exit if the user presses Enter
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
    client.close()

def compose_and_insert_tweet(content, mongo_uri):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    
    # Create or get the database
    db = client["291db"]
    
    # Get the tweets collection
    tweets_collection = db["tweets"]

    # Compose the tweet
    tweet = {
        "url": None,
        "date": datetime.now(),
        "content": content,
        "renderedContent": None,
        "id": None,
        "user": {
            "username": "291user",
            "displayname": None,
            "id": None,
            "description": None,
            "rawDescription": None,
            "descriptionUrls": None,
            "verified": None,
            "created": None,
            "followersCount": None,
            "friendsCount": None,
            "statusesCount": None,
            "favouritesCount": None,
            "listedCount": None,
            "mediaCount": None,
            "location": None,
            "protected": None,
            "linkUrl": None,
            "linkTcourl": None,
            "profileImageUrl": None,
            "profileBannerUrl": None,
            "url": None
        },
        "outlinks": None,
        "tcooutlinks": None,
        "replyCount": None,
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "conversationId": None,
        "lang": None,
        "source": None,
        "sourceUrl": None,
        "sourceLabel": None,
        "media": None,
        "retweetedTweet": None,
        "quotedTweet": None,
        "mentionedUsers": None
    }

    # Insert the tweet into the database
    tweets_collection.insert_one(tweet)

    print("Tweet inserted successfully.")
    client.close()

def list_top_users(mongo_uri, n):
    client = MongoClient('mongodb://localhost:{}/'.format(mongo_uri))
    db = client["291db"]
    tweets_collection = db["tweets"]

    # Aggregate to find top n users with the maximum followersCount
    pipeline = [
        {"$group": {
            "_id": "$user.username",
            "maxFollowersCount": {"$max": "$user.followersCount"},
            "displayname": {"$first": "$user.displayname"}
        }},
        {"$sort": {"maxFollowersCount": pymongo.DESCENDING}},
        {"$limit": n},
        {"$project": {
            "_id": 0,
            "username": "$_id",
            "displayname": 1,
            "maxFollowersCount": 1
        }}
    ]

    top_users = list(tweets_collection.aggregate(pipeline))

    # Check if there are no users
    if not top_users:
        print("No users found.")
        return

    # Print the top users with numbered options
    print(f"Top {n} users based on followersCount_index:")
    for i, user in enumerate(top_users, start=1):
        print(f"{i}. Username: {user['username']}, Displayname: {user['displayname']}, FollowersCount: {user['maxFollowersCount']}")

    # Prompt the user to select a user
    try:
        selected_option = int(input(f"Enter the number of the user to get full information (1 to {n}) or press anything except a number to exit: "))
    except ValueError:
        return

    # Get the selected user's information
    if 1 <= selected_option <= n:
        selected_user = top_users[selected_option - 1]
        username = selected_user['username']
        get_full_user_info(mongo_uri, username)
    else:
        print("Invalid selection. Please enter a valid number.")
    client.close()

"""
keywords = ["are", "farmers", "GUNDAs"]
mongo_uri = 27017
keyword = "kaur"
"""
#search_and_view_users(keyword, mongo_uri)
#search_tweets(keywords, mongo_uri)
#list_top_tweets(mongo_uri, 3)
#list_top_users(mongo_uri, 3)
#compose_and_insert_tweet(content, mongo_uri)
