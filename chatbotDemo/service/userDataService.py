# This file is used to get user data from the database
import dto.user as user
def getUserData(userName):
    if(userName == None):
        print("User data is empty")
        return None
    else:
        #...

        # Create a user object
        userData = user.User("John", "Doe", "01/01/1990", None, None)
        return userData
    