# TwitterCloneMongoDB_python

This program is an experimental project made purely through prompts issued to chat GPT to achieve the following:

# Phase 1: Building a document store
For this part, you will write a program, named load-json with a proper extension (e.g. load-json.py if using Python), which will take a json file in the current directory and constructs a MongoDB collection. Your program will take as input in the command line a json file name and a port number under which the MongoDB server is running, will connect to the server and will create a database named 291db (if it does not exist). Your program then will create a collection named tweets. If the collection exists, your program should drop it and create a new collection. Your program for this phase ends after building the collection.

Data should be inserted in small batches (say 1k-10k tweets per batch) using insertMany command in MongoDB. The input file is expected to be too large to fit in memory. You may also use Mongoimport (if available on lab machines). 


# Phase 2: Operating on the document store
Write a program that supports the following operations on the MongoDB database created in Phase 1. Your program will take as input a port number under which the MongoDB server is running, and will connect to a database named 291db on the server.

Next, users should be able to perform the following tasks.

Search for tweets The user should be able to provide one or more keywords, and the system should retrieve all tweets that match all those keywords (AND semantics). A keyword matches if it appears in the content field. For each matching tweet, display the id, date, content, and username of the person who posted it. The user should be able to select a tweet and see all fields.
Search for users The user should be able to provide a keyword  and see all users whose displayname or location contain the keyword. For each user, list the username, displayname, and location with no duplicates. The user should be able to select a user and see full information about the user.
List top tweets The user should be able to list top n tweets based on any of the fields retweetCount, likeCount, quoteCount, to be selected by the user. The value of n will be also entered by the user. The result will be ordered in a descending order of the selected field. For each matching tweet, display the id, date, content, and username of the person who posted it. The user should be able to select a tweet and see all fields.
List top users The user should be able to list top n users based on followersCount with n entered by user. For each user, list the username, displayname, and followersCount with no duplicates. The user should be able to select a user and see the full information about the user.
Compose a tweet The user should be able to compose a tweet by entering a tweet content. Your system should insert the tweet to the database, set the date filed to the system date and username to "291user". All other fields will be null.
After each action, the user should be able to return to the main menu for further operations. There should be also an option to end the program.

Keyword matching. A keyword is an alphanumeric sequence of characters. You can assume multiple keywords in a tweet are separated by spaces or punctuations.  Keyword matches in (1) and (2) are case insensitive matches. Case insensitive indexes in MongoDB can be created by setting the collation option.
