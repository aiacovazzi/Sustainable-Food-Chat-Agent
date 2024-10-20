import json
userData = """{
    "id":"547874162",
    "name": "John Doe",
    "dateOfBirth": "01/01/2000"
}"""

def getUserData(userName):
    if(userName == None):
        print("User data is empty")
        return None
    else:
        return userData
    