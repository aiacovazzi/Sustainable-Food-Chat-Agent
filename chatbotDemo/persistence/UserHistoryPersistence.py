from pymongo import MongoClient
import jsonpickle

client = MongoClient('localhost', 27017)
db = client['emealio_food_db']
collection = db['users_food_history']

def save_user_history(userHistoryJson):
    userHistory = jsonpickle.decode(userHistoryJson)
    collection.insert_one(userHistory)

def get_user_history(userId):
    #get the user history of the week, given that the status is accepted
    fullUserHistory = collection.find({"userId": userId})
    return jsonpickle.encode(fullUserHistory)

def clean_temporary_declined_suggestions(userId):
    #clean the temporary declined suggestions
    collection.delete_many({"userId": userId, "status": "temporary_declined"})

def get_temporary_declined_suggestions(userId):
    fullUserHistory = collection.find({"userId": userId, "status": "temporary_declined"})
    return jsonpickle.encode(fullUserHistory)