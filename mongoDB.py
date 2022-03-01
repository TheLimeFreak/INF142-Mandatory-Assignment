import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os

print(pymongo.version)

# Get you password from .env file
username = os.environ.get("USER")
password = os.environ.get("PASS")
clusterName = "inf142-mandatory-assign"

# Connect to you cluster
client = MongoClient('mongodb+srv://' + username + ':' + password + '@' + clusterName + '.awcxl.mongodb.net/demo-db?retryWrites=true&w=majority')

# Create a new database in your cluster
database = client.INF142

# Create a new collection in you database
person = database.person

personDocument = {
  "firstname": "Ola",
  "lastname": "Nordmann",
  "course": "INF142"
}

person.insert_one(personDocument)





