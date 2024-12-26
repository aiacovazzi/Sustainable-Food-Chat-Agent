# This file is used to get user data from the database
import dto.user as user
import persistence.UserPersistence as userDB
import jsonpickle
def getUserData(userId):
    if(userId == None):
        print("User data is empty")
        return None
    else:
        userDbData = userDB.getUserByUserId(userId)
        if(userDbData == None):
            return None
        userJson = jsonpickle.encode(userDbData)
        userData = user.User(None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        return userData
    
def save_user(userData):
    userDB.save_user(userData.to_plain_json())

def update_user(userData):
    userDB.update_user(userData.to_plain_json())