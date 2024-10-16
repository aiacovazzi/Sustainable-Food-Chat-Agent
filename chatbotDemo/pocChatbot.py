import service.langChainService as lcs
import constants as p
import service.foodHistoryService as history
import service.userDataService as user
import dto.responseClass as rc
import utils
import json

userData = user.getUserData("John Doe")
userDataDict = json.loads(userData)
userName = userDataDict["name"]
firstInteraction = True
if(userData ==  None):
    print("User data is empty")
    #TODO: get user data from user
    #Save data

print("START")
while(True):
    print("BASE INTERACTION") 
    openUserPrompt = "Who are you?" 
    if(not firstInteraction):
        openUserPrompt = "Hello E-Mealio! Here I am again."
           
    response = lcs.execute_chain(p.STARTING_PROMPT, openUserPrompt, 0.9)
    print(response.answer)
    firstInteraction = not(firstInteraction) 
    baseUserPrompt = p.USER_PROMPT.format(user_data=userData)

    #action detection
    while(response.action == p.TASK_1_HOOK):   
            #read from keyboard
            qry = input("Tell me something: ")
            response = lcs.execute_chain(p.STARTING_PROMPT, qry, 0.6)    
            print(response.answer)

    #action execution   
    if(response.action == p.TASK_2_HOOK):
        print("FOOD SUGGESTION") 
        while(response.action == p.TASK_2_HOOK): 
            response = lcs.execute_chain(p.TASK_2_PROMPT, qry, 0.1)
            if(response.action == p.TASK_2_10_HOOK):
                print(response.action)
                #call recommender
                #manage suggestion
                #ask confimation
                #update history
            else:
                print(response.answer)
                qry = input("Tell me something: ")

    if(response.action == p.TASK_3_HOOK):
        print("RECIPE IMPROVEMENT") 
        response = lcs.execute_chain(p.TASK_3_PROMPT, qry, 0.1)
        if(response.action != None):
            print(response.answer)
            #call recommender in improvement mode
            #manage suggestion
            #ask confimation
            #update history

    if(response.action == p.TASK_4_HOOK):
        print("USER DATA") 
        qry = baseUserPrompt + qry
        response = lcs.execute_chain(p.TASK_4_PROMPT, qry, 0.8)
        print(response.answer)

    if(response.action == p.TASK_4_10_HOOK):
        print("UPDATE USER DATA?") 
        qry = input()
        response = lcs.execute_chain(p.TASK_4_10_PROMPT, qry, 0.1)
        print(response.answer)

    if(response.action == p.TASK_4_20_HOOK):
        print("UPDATE USER DATA") 
        response.answer = "TOKEN 1"
        #manage update loop + info update
    
    if(response.action == p.TASK_5_HOOK):
        print("FOOD HISTORY") 
        foodHistory = utils.escape_curly_braces(history.getFoodHistory(userName))
        response = lcs.execute_chain(p.TASK_5_PROMPT.format(food_history=foodHistory), qry, 0.6)
        print(response.answer)