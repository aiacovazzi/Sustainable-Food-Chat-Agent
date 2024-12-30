import service.langChainService as lcs
import constants as p
import service.foodHistoryService as history
import service.userDataService as user
import service.suggestRecipeService as food
import service.improveRecipeService as imp
import dto.responseClass as rc
import jsonpickle
import utils
from datetime import datetime
import service.foodHistoryService as fhService

def aswer_router(userData,userPrompt,token,memory,info):
    response = rc.Response('','','','','')
    while(response.answer==''):
        response = answer_question(userData,userPrompt,token,info,memory)
        token = response.action
        info = response.info
        memory = response.memory
        if(response.modifiedPrompt != None and response.modifiedPrompt != ''):
            userPrompt = response.modifiedPrompt
    return response   

def answer_question(userData,userPrompt,token,info,memory):
#0 USER DATA RETRIEVAL##################################################################
    if(token == p.TASK_0_HOOK):
        print("PRESENTING_USER_DATA_RETRIEVAL" )
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0, userPrompt, 0.6)
        return response
    elif(token == p.TASK_0_1_HOOK):
        print("PERFORMING_USER_DATA_RETRIEVAL" )
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_1, "User data: " + userData.to_json() + " "+ userPrompt, 0.2)
        return response
    elif(token == p.TASK_0_2_HOOK):
        print("PERFORMING_USER_DATA_EVALUATION" )

        #update user data using the information so far retrieved
        userData.from_json(info)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_2, "User data: " + info, 0.2)

        return response;
    elif(token == p.TASK_0_3_HOOK):
        print("PERSISTING_USER_DATA" )
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_3, "User data: " + userData.to_json(), 0.4)
        user.save_user(userData)
        #adjust the user prompt to the greetings in order to start the regular conversation
        userPrompt = p.USER_GREETINGS_PHRASE
        return response
########################################################################################

#1 MAIN HUB / GREETINGS#################################################################
    elif(token == p.TASK_1_HOOK):
        print("GRETINGS")
        #passing though the main hub imply starting a new conversation so I can reset the memory
        memory = None
        response = lcs.execute_chain(p.STARTING_PROMPT, userPrompt, 0.6)
        return response
########################################################################################

#FOOD SUGGESTION########################################################################
    elif(token == p.TASK_2_HOOK):
        print("FOOD_SUGGESTION_INTERACTION" )
        response = lcs.execute_chain(p.TASK_2_PROMPT, userPrompt, 0.2)
        return response
    elif(token == p.TASK_2_05_HOOK):
        print("FOOD_SUGGESTION_DATA_VERIFICATION" )
        #response = lcs.execute_chain(p.TASK_2_05_PROMPT, userPrompt, 0.1)
        json_mealdata_obj = jsonpickle.decode(info)

        #Meal type check and answer not managed by LLMS since it is straightforward
        if(json_mealdata_obj['mealType'] == None or json_mealdata_obj['mealType'] == ''):
            answer = """I need to know when you would like to eat the meal you desire.\nPlease provide a meal type between: breakfast, lunch, dinner or snack."""
            action = p.TASK_2_HOOK           
            response = rc.Response(answer,action,info,None,'')
        else:
            action = p.TASK_2_10_HOOK
            response = rc.Response('',action,info,None,'')
        return response
    elif(token == p.TASK_2_10_HOOK):
        print("PROVIDING_FOOD_SUGGESTION" )
        #call recommender system
        suggestedRecipe = food.getRecipeSuggestion(info,userData)
        info = utils.escape_curly_braces(info)
        userDataStr = utils.escape_curly_braces(userData.to_json())
        userPrompt = "Suggest me a recipe given the following constraints " + info
        if(suggestedRecipe != None):
            response = lcs.execute_chain(p.TASK_2_10_PROMPT.format(suggestedRecipe=suggestedRecipe, mealInfo=info, userData=userDataStr), userPrompt, 0.6, memory, True)
        else:
            response = lcs.execute_chain(p.TASK_2_101_PROMPT.format( mealInfo=info, userData=userDataStr), userPrompt, 0.6, memory, False)        
        #produce suggestion
        return response
    elif(token == p.TASK_2_20_HOOK):
        print("SUGGESTION_CHAT_LOOP" )
        response = lcs.execute_chain(p.TASK_2_20_PROMPT, userPrompt, 0.6, memory, True)
        return response
    elif(token == p.TASK_2_30_HOOK):
        print("SUGGESTION_ACCEPTED")
        manage_suggestion(userData,memory,"accepted")
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response('I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!',"TOKEN 1",'',None,'')
        return response
    elif(token == p.TASK_2_40_HOOK):
        print("SUGGESTION_DECLINED")
        manage_suggestion(userData,memory,"declined")
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response('I\'m sorry you didn\'t accepepet my suggestion. I hope you will find something for you next time! If I can help you with other food sustainability answer, I\'m here to help!',"TOKEN 1",'',None,'')
        return response
    elif(token == p.TASK_2_50_HOOK):
        print("REQUIRED_ANOTHER_SUGGESTION")
        manage_suggestion(userData,memory,"temporary_declined")
        originalUserPrompt = memory.messages[1].content
        response = rc.Response('',"TOKEN 1",'',None,originalUserPrompt)
        return response
########################################################################################


#RECIPE SUSTAINABILITY EXPERT###########################################################
    elif(token == p.TASK_3_HOOK):
        print("RECIPE_EXPERT" )
        response = lcs.execute_chain(p.TASK_3_PROMPT, userPrompt, 0.1)
        return response
########################################################################################

#RECIPE IMPROVEMENT#####################################################################
    elif(token == p.TASK_3_10_HOOK):
        print("RECIPE_IMPROVEMENT_EXECUTION" )
        recipes = imp.getRecipeSuggestion(info)
        response = lcs.execute_chain(p.TASK_3_10_PROMPT.format(baseRecipe=recipes[0], improvedRecipe=recipes[1]), userPrompt, 0.6)
        return response
########################################################################################

#PROFILE MANAGEMENT#####################################################################
    elif(token == p.TASK_4_HOOK):
        print("PROFILE_SUMMARY" )
        userPrompt = p.USER_PROMPT.format(user_data=userData.to_json())
        response = lcs.execute_chain(p.TASK_4_PROMPT, userPrompt, 0.8)
        return response
    elif(token == p.TASK_4_10_HOOK):
        print("ASKING_PROFILE_UPDATE" )
        response = lcs.execute_chain(p.TASK_4_10_PROMPT, userPrompt, 0.1)
        return response
    elif(token == p.TASK_4_20_HOOK):
        print("PRESENTING_PROFILE_UPDATE" )
        response = lcs.execute_chain(p.TASK_4_20_PROMPT, userPrompt, 0.1)
        return response
    elif(token == p.TASK_4_30_HOOK):
        print("PERFORMING_PROFILE_UPDATE" )
        response = lcs.execute_chain(p.TASK_4_30_PROMPT, "User data: "+ userPrompt, 0.1)
        return response
    elif(token == p.TASK_4_40_HOOK):
        print("EVALUATING_PROFILE_UPDATE" )
        userData.update_from_json(info)
        response = lcs.execute_chain(p.TASK_4_40_PROMPT, "User data: " + userData.to_json() + " "+ userPrompt, 0.1)
        return response
    elif(token == p.TASK_4_50_HOOK):
        print("PERSISTING_PROFILE_UPDATE" )
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.TASK_4_50_PROMPT, "User data: " + userData.to_json(), 0.1)
        user.update_user(userData)
        return response
########################################################################################

#HISTORY RETRIEVAL######################################################################
    elif(token == p.TASK_5_HOOK):
        print("FOOD_HISTORY" )
        userName = "Jhon Doe"
        foodHistory = utils.escape_curly_braces(history.get_user_history_of_week(userData.id))
        response = lcs.execute_chain(p.TASK_5_PROMPT.format(food_history=foodHistory), userPrompt, 0.6)
        return response
########################################################################################

#SUSTAINABILITY EXPERT##################################################################
    elif(token == p.TASK_6_HOOK):
        print("SUSTAINABILITY_EXPERT" )
        response = lcs.execute_chain(p.TASK_6_PROMPT, userPrompt, 0.8)
        return response
########################################################################################

#RECIPE CONSUPTION DIARY################################################################
    elif(token == p.TASK_7_HOOK):
        print("RECIPE_CONSUPTION_DIARY" )
        response = lcs.execute_chain(p.TASK_7_PROMPT, "Meal data: " + info +" "+userPrompt, 0.2)
        return response
    elif(token == p.TASK_7_10_HOOK):
        print("RECIPE_CONSUPTION_DIARY_DATA_VERIFICATION" )
        response = lcs.execute_chain(p.TASK_7_10_PROMPT, "Meal data: " + info, 0.3)
        return response
    elif(token == p.TASK_7_20_HOOK):
        print("RECIPE_CONSUPTION_DIARY_DATA_SAVING" )
        #calling the proper service to save the meal data computing the sustainability
        jsonRecipeAssertion = utils.extract_json(info, 0)
        fhService.build_and_save_user_history_from_user_assertion(userData, jsonRecipeAssertion)
        response = lcs.execute_chain(p.TASK_7_20_PROMPT, "Meal data: " + info, 0.1)
        return response
########################################################################################

def manage_suggestion(userData,memory,status):
    originalPrompt = utils.de_escape_curly_braces(memory.messages[0].content)
    jsonRecipe = utils.extract_json(originalPrompt, 0)
    fhService.build_and_save_user_history(userData, jsonRecipe, status)