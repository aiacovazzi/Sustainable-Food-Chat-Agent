import json
foodHistory = {
    "user": "John Doe",
    "foods" : [
          {
               "recipe":"Lasagna",
               "eatedIn":"2024-10-11",
               "mealCategory":"Dinner",
          },
          {
                "recipe":"Pizza",
                "eatedIn":"2024-10-10",
                "mealCategory":"Dinner",
          },
          {
                "recipe":"Spaghetti",
                "eatedIn":"2024-10-10",
                "mealCategory":"Lunch",
          },
          
     ]
}
def getFoodHistory(userName):
    if(userName == None):
        print("User data is empty")
        return None
    else:
        return json.dumps(foodHistory)
    