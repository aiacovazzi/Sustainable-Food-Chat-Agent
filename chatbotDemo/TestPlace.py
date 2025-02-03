import service.ImproveRecipeService as irs
import service.domain.UserDataService as us
import service.domain.FoodHistoryService as foodHistory
import jsonpickle
import persistence.RecipePersistence as recipePersistence
from datetime import datetime, timedelta

#print(irs.get_recipe_improved('{\n  "name": "Beef and Tomato Sandwich",\n  "ingredients": [\n    "bun",\n    "cow meat",\n    "tomato",\n    "mayonnaise"\n  ]\n}'))

#print(irs.get_recipe_improved('{"name":"test","ingredients":["pasta","hashed meat","tomato paste"]}'))

#userdata = us.getUserData(547874162)
#temporaryDeclinedSuggestions = foodHistory.get_temporary_declined_suggestions(userdata.id)
#listTemp = jsonpickle.decode(temporaryDeclinedSuggestions)
#print(listTemp)

#l = recipePersistence.get_recipe_list()
#print(recipePersistence.get_most_similar_recipe("Banana and milk shake wonderful recipe")) 


users = us.get_all_users()
for user in users:
    #user = jsonpickle.encode(user)
    print(user['username'])
    if(user['username'] == 'animalemagico'):
        print(user['reminder'])
        date = datetime.strptime(user['lastInteraction'], '%Y-%m-%d %H:%M:%S')
        #trim date to only date
        date = date.date()
        print(date)
        print(datetime.now().date())