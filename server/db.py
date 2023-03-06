from flask import Flask
from flask_pymongo import pymongo
from app import app

client = pymongo.MongoClient("mongodb+srv://mihnea:mihnea99@realmcluster.xxgrb.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database('realmcluster')
user_collection = pymongo.collection.Collection(db, 'user_collection')
collection = db['collection']


