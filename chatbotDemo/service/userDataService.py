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
        userJson = jsonpickle.encode(userDbData)
        userData = user.User("","","","","","","")
        userData.from_json(userJson)
        return userData