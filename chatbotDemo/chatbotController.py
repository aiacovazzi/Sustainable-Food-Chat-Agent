import service.langChainService as lcs
import constants as p
import service.foodHistoryService as history
import service.userDataService as user
import service.suggestFoodService as food
import service.improveRecipeService as imp
import dto.responseClass as rc

def aswerRouter(userData,userPrompt,token):
    response = rc.Response('','','')
    info = ''
    while(response.answer==''):
        response = answerQuestion(userData,userPrompt,token,info)
        token = response.action
        info = response.info
    return response   

def answerQuestion(userData,userPrompt,token,info):
    if(token == p.TASK_0_HOOK):
        print("PRESENTING_USER_DATA_RETRIEVAL" )
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0, userPrompt, 0.6)
        return response;
    elif(token == p.TASK_0_1_HOOK):
        print("PERFORMING_USER_DATA_RETRIEVAL" )
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_1, "User data: " + str(userData) + " "+ userPrompt, 0.2)
        return response;
    elif(token == p.TASK_0_2_HOOK):
        print("PERFORMING_USER_DATA_EVALUATION" )

        #update user data using the information so far retrieved
        userData.from_json(info)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_2, "User data: " + info, 0.4)

        return response;
    elif(token == p.TASK_0_3_HOOK):
        print("PERSISTING_USER_DATA" )
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_3, "User data: " + str(userData), 0.4)

        #adjust the user prompt to the greetings in order to start the regular conversation
        userPrompt = p.USER_GREETINGS_PHRASE
        return response;
    elif(token == p.TASK_1_HOOK):
        print("GRETINGS")
        response = lcs.execute_chain(p.STARTING_PROMPT, userPrompt, 0.6)
        return response;
    elif(token == p.TASK_2_HOOK):
        print("FOOD_SUGGESTION_INTERACTION" )
        response = lcs.execute_chain(p.TASK_2_PROMPT, userPrompt, 0.1)
        return response;
    elif(token == p.TASK_2_10_HOOK):
        print("PROVIDING_FOOD_SUGGESTION" )
        #call recommender system
        suggestedRecipe = food.getRecipeSuggestion(info)
        response = lcs.execute_chain(p.TASK_2_10_PROMPT.format(suggestedRecipe=suggestedRecipe, mealType=info), userPrompt, 0.6)
        #produce suggestion
        return response;
    elif(token == p.TASK_3_HOOK):
        print("RECIPE_EXPERT" )
        response = lcs.execute_chain(p.TASK_3_PROMPT, userPrompt, 0.1)
        return response;
    elif(token == p.TASK_3_10_HOOK):
        print("RECIPE_IMPROVEMENT_EXECUTION" )
        recipes = imp.getRecipeSuggestion(info)
        response = lcs.execute_chain(p.TASK_3_10_PROMPT.format(baseRecipe=recipes[0], improvedRecipe=recipes[1]), userPrompt, 0.6)
        return response;
    elif(token == p.TASK_4_HOOK):
        print("PROFILE_SUMMARY" )
        userPrompt = p.USER_PROMPT.format(user_data=str(userData))
        response = lcs.execute_chain(p.TASK_4_PROMPT, userPrompt, 0.8)
        return response;
    elif(token == p.TASK_4_10_HOOK):
        print("ASKING_PROFILE_UPDATE" )
        response = lcs.execute_chain(p.TASK_4_10_PROMPT, userPrompt, 0.1)
        return response;
    elif(token == p.TASK_4_20_HOOK):
        print("PROFILE_UPDATE" )
        #profile update loop
        return response;
    elif(token == p.TASK_5_HOOK):
        print("FOOD_HISTORY" )
        userName = "Jhon Doe"
        foodHistory = history.getFoodHistory(userName)
        response = lcs.execute_chain(p.TASK_5_PROMPT.format(food_history=foodHistory), userPrompt, 0.6)
        return response;
    elif(token == p.TASK_6_HOOK):
        print("SUSTAINABILITY_EXPERT" )
        response = lcs.execute_chain(p.TASK_6_PROMPT, userPrompt, 0.8)
        return response;