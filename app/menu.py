import pymongo
from pymongo import MongoClient
from datetime import datetime
import sys
from functions_for_tasks import search_and_view_users, search_tweets, list_top_tweets, compose_and_insert_tweet, list_top_users

# Constant for MongoDB port
MONGO_PORT = 27017

def main_menu():
    print("\n")
    print("Welcome to the main menu. You have the following options:")
    print("1. Search for tweets")
    print("2. Search for users")
    print("3. List top tweets")
    print("4. List top users")
    print("5. Compose a tweet")
    print("6. Exit")

    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == "1":
        # Search for tweets
        print("\n")
        keywords = input("Enter keywords (comma-separated): ").split(',')
        mongo_uri = f"{MONGO_PORT}"
        print("\n")
        search_tweets(keywords, mongo_uri)

    elif choice == "2":
        # Search for users
        print("\n")
        keyword = input("Enter keyword for user search: ")
        mongo_uri = f"{MONGO_PORT}"
        print("\n")
        search_and_view_users(keyword, mongo_uri)

    elif choice == "3":
        # List top tweets
        print("\n")
        n = int(input("Enter the number of top tweets to list: "))
        mongo_uri = f"{MONGO_PORT}"
        print("\n")
        list_top_tweets(mongo_uri, n)

    elif choice == "4":
        # List top users
        print("\n")
        n = int(input("Enter the number of top users to list: "))
        mongo_uri = f"{MONGO_PORT}"
        print("\n")
        list_top_users(mongo_uri, n)

    elif choice == "5":
        # Compose a tweet
        print("\n")
        content = input("Enter the content of your tweet: ")
        mongo_uri = f"{MONGO_PORT}"
        print("\n")
        compose_and_insert_tweet(content, mongo_uri)

    elif choice == "6":
        # Exit the program
        sys.exit(0)

    else:
        print("Invalid choice. Please enter a valid number.")

# Run the main menu
while True:
    main_menu()


#NOTES: EDIT SEARCH USERS TO SAY IF NO USER HAS BEEN FOUND AND TO NOT EXIT THE PROGRAM STRAIGHT AFTER
