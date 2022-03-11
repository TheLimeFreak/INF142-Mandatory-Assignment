import pymongo
import os

from champlistloader import load_some_champs
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

print(f'PyMongo version: {pymongo.version}')

# Get you password from .env file
username = os.environ.get("USER")
password = os.environ.get("PASS")
clusterName = "inf142-mandatory-assign"

# Connect to you cluster
client = MongoClient('mongodb+srv://' + username + ':' + password + '@' + clusterName + '.awcxl.mongodb.net/demo-db?retryWrites=true&w=majority')

# Create a new database in your cluster
database = client.INF142

# Create a new collection in you database
champdb = database.champion

champions = load_some_champs()
for champion in champions.values():
  name, rock, paper, scissors = champion.str_tuple
  championDocument = {
    "name": name,
    "rock": float(rock),
    "paper": float(paper),
    "scissors": float(scissors)
  }
  champdb.insert_one(championDocument)