from pymongo import MongoClient
import jsonpickle

client = MongoClient('localhost', 27017)
db = client['emealio_food_db']
collection = db['users_food_history']

def saveUserHistory(userHistoryJson):
    userHistory = jsonpickle.decode(userHistoryJson)
    collection.insert_one(userHistory)