from pymongo import MongoClient
import jsonpickle

def save_user(userJson):
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    collection = db['users']
    user = jsonpickle.decode(userJson)
    collection.insert_one(user)

def update_user(userJson):
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    collection = db['users']
    user = jsonpickle.decode(userJson)
    collection.update_one({"id":user['id']}, {"$set": user}, upsert=False)

def getUserByUserId(userId):
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    collection = db['users']
    user = collection.find_one({"id":userId})
    return user