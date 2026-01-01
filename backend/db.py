from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["cricket_db"]

players = db.players
matches = db.matches
scorecards = db.scorecards
