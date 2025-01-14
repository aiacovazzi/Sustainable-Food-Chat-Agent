from pymongo import MongoClient
import jsonpickle
import persistence.MongoConnectionManager as mongo

db = mongo.get_connection()
collection = db['users']

def save_user(userJson):
    user = jsonpickle.decode(userJson)
    collection.insert_one(user)

def update_user(userJson):
    user = jsonpickle.decode(userJson)
    collection.update_one({"id":user['id']}, {"$set": user}, upsert=False)

def getUserByUserId(userId):
    user = collection.find_one({"id":userId})
    return user