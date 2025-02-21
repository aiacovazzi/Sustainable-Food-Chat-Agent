import unittest
import ChatbotController as cc
import Constants as con
import dto.User as ud
import persistence.UserPersistence as up
import persistence.UserHistoryPersistence as uhp
import jsonpickle

#Collection of test cases
class TestController(unittest.TestCase):

#USER REGISTRATION TESTS
    def test_user_registration_entry_point(self):
        print("answer_question: Test User Registration Presentation")
        userData = self.get_user_data()
        response = cc.answer_question(userData,"Hello",con.TASK_0_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        #info data not produced because the system is asking for the user data
        self.assertTrue(response.info.strip() == '')
        self.assertTrue(len(response.answer) > 0)

    def test_user_registration_unrelated_message(self):
        print("answer_question: Test User Registration Presentation: Unrelated Message")
        userData = self.get_user_data()
        response = cc.answer_question(userData,"What time is it?",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        #info data not produced because the system is replyng to a not compliant message
        self.assertTrue(response.info.strip() == '')
        self.assertTrue(len(response.answer.strip()) != 0)

    def test_user_registration_partial_data(self):
        print("answer_question: Test User Registration Presentation: Partial Data Provided")
        userData = self.get_user_data()
        response = cc.answer_question(userData,"Hello, I'm Giacomo Rossi.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_2_HOOK)
        #info data produced but incomplete
        self.assertTrue(response.info.strip() != '')
        userData = jsonpickle.decode(response.info)
        #check if the data is correct
        self.assertEqual(userData['name'], "Giacomo")
        self.assertEqual(userData['surname'], "Rossi")
        self.assertEqual(userData['dateOfBirth'], "")        
        #answer empty becuase the response is a change of inner state, is not for the user
        self.assertTrue(len(response.answer) == 0)

    def test_user_registration_all_mandatory_data(self):
        print("answer_router: Test User Registration Presentation: All Mandatory Data Provided")
        userData = self.get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        #user data object is updated with the provided data
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")

    def test_user_registration_all_mandatory_and_optional_data(self):
        print("answer_router: Test User Registration Presentation: All Mandatory and Optiona Data Provided")
        userData = self.get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990. Im allergic to peanut and fish. I Follow a vegan diet.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        #check if the allergies are in the list
        self.assertTrue("peanut" in userData.allergies)
        self.assertTrue("fish" in userData.allergies)
        self.assertTrue("vegan" in userData.restrictions)

    def test_user_registration_multistep_with_reminder_consent(self):
        print("multistep answer_router: Test User Registration Presentation: All Mandatory Data Provided; Then Provide Reminder Consent")
        userData = self.get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")
        response = cc.answer_router(userData,"Yes I want reminders",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, True)

    def test_user_registration_multistep_with_negate_reminder_consent(self):
        print("multistep answer_router: Test User Registration Presentation: All Mandatory Data Provided, But In Two Step; Then Negate Reminder Consent")
        userData = self.get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.dateOfBirth, "")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")

        response = cc.answer_router(userData,"I was born on 01/01/1990, i'm also allergic to peanuts.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertTrue("peanut" in userData.allergies)
        self.assertEqual(userData.restrictions, "")

        response = cc.answer_router(userData,"No thanks.",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, False)

#HUB TESTS
    def test_greetings(self):
        print("answer_router: Test Greetings")
        response = cc.answer_router(self.get_user_data(),con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"","")
        self.print_answers(response)
        #check if the generated token is equal to the expected token, that info are empty and the answer is not empty
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
        #this means that the bot has greeted the user
    #HUB -> RECOMMENDATION
    def test_from_hub_to_recommendation_entry_point(self):
        print("answer_question: Test Recommendation Presentation")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat today?",con.TASK_1_HOOK,"","")
        self.print_answers(response)
        #the hub moves to the recommendation task
        self.assertEqual(response.action, con.TASK_2_HOOK)
        #info data not produced 
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test_from_hub_to_expert_improvement(self):
        print("answer_question: Expert Hub Entry Point")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"How can I improve the sustainability of a pizza?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the recommendation task
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test_from_hub_to_expert_ingredients(self):
        print("answer_question: Expert Hub Entry Point; Ingredient Expert")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"Tell me about the sustainability of bananas and pineapples.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test_from_hub_to_expert_recipe(self):
        print("answer_question: Expert Hub Entry Point; Recipe Expert")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"Compare the sustainability of a Veggie Lasagna, with a Pasta Carbonara",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test_from_hub_to_expert_recipe_with_ingredients(self):
        print("answer_question: Expert Hub Entry Point; Recipe Expert with ingredients")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"Compare the sustainability of a Sandwich made of bread, tuna, salad, mayonaise and cheese, with a Pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test_from_hub_to_expert_concept(self):
        print("answer_question: Expert Hub Entry Point; Concept Expert")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"What is cilmate change?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> FOOD ASSERTION
    def test_from_hub_to_food_assertion(self):
        print("answer_question: Food Assertion Entry Point")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"I've eat a pizza.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> PROFILE RECAP
    def test_from_hub_to_profile_recap(self):
        print("answer_question: Profile Recap Entry Point")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_4_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> FOOD HISTORY
    def test_from_hub_to_food_history(self):
        print("answer_question: Food History Entry Point")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"Can you resume my food history?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_5_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)

#RECOMMENDATION TESTS
    def test_recommendation_move_to_data_verification(self):
        print("answer_question: Test Recommendation Presentation; Move to Data Verification")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat?",con.TASK_2_HOOK,None,"")
        self.print_answers(response)
        #moves to data verification state
        self.assertEqual(response.action, con.TASK_2_05_HOOK)
        #info data produced
        self.assertTrue(response.info.strip() != '')
        jsonMealdataObj = jsonpickle.decode(response.info)
        self.assertTrue(len(jsonMealdataObj['mealType'])==0)
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)

    def test_recommendation_move_to_data_verification_with_meal_type(self):
        print("answer_question: Test Recommendation Presentation; Move to Data Verification with Meal Type")
        userData = self.get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat for dinner?",con.TASK_2_HOOK,None,"")
        self.print_answers(response)
        #moves to data verification state
        self.assertEqual(response.action, con.TASK_2_05_HOOK)
        #info data produced
        self.assertTrue(response.info.strip() != '')
        jsonMealdataObj = jsonpickle.decode(response.info)
        self.assertTrue(jsonMealdataObj['mealType']=="Dinner")
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)

    def test_reccomentation_with_answer(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

    def test_reccomentation_with_answer_conversation_and_acceptance(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Mhh, can you suggest me something else?",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        #Why this is a good recipe for me?
        #Can you list the ingredients involved?
        #Are the ingredients sustainable?
        #Ok thak you, i'll eat this one.

        response = cc.answer_router(userData,"Why this is a good recipe for me?",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you list the ingredients involved?",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"Are the ingredients sustainable?",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"Ok thank you, i'll eat this one.",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test_reccomentation_with_ingredients_answer_conversation_and_acceptance(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Suggest me something to eat that contains rice?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_HOOK)
        #answer provided, it is asking for the meal type
        self.assertTrue(len(response.answer) > 0)
        #info is not empty, it contains the meal information, in this case the ingredient
        self.assertTrue(response.info.strip() != '')
        mealData = jsonpickle.decode(response.info)
        self.assertTrue("rice" in mealData['ingredients_desired'])
        response = cc.answer_router(userData,"It is for lunch.",con.TASK_2_HOOK,response.memory,"")
        self.print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Ok thank you, i'll eat this one.",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test_reccomentation_with_answer_and_refutation(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"No thanks, I don't like it.",con.TASK_2_20_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m sorry you didn\'t accepted my suggestion. I hope you will find something for you next time! If I can help you with other food sustainability answer, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

#RECIPE IMPROVEMENT TESTS
    def test_recipe_improvement_with_answer_change_and_acceptance(self):
        print("answer_router: Test Recipe Improvement Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a greek sandwich?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to ingredient acquisition state
        self.assertEqual(response.action, con.TASK_3_15_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is not empty
        self.assertTrue(response.info.strip() != '')

        response = cc.answer_router(userData,"What do you want?.",con.TASK_3_15_HOOK,None,response.info)
        self.print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_15_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is not empty
        self.assertTrue(response.info.strip() != '')

        response = cc.answer_router(userData,"It was made of bread, yogurt and onion.",con.TASK_3_15_HOOK,None,response.info)
        self.print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you suggest me an alternative?",con.TASK_3_30_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Yes, I'll try it.",con.TASK_3_30_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, "I'm glad you accepted my improved version of the recipe! If I can help you with other food sustainability questions, I'm here to help!")
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test_recipe_improvement_with_ingredients_answer_change_and_refutation(self):
        print("answer_router: Test Recipe Improvement Presentation: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a pizza made of pizza dough, mozzarella and tomato?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"No thanks, I don't like it.",con.TASK_3_30_HOOK,response.memory,"")
        self.print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m sorry you didn\'t accepted my improved version of the recipe. If I can help you with other food sustainability answer, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

#INGREDIENT EXPERT TEST
    def test_ingredient_expert_with_answer(self):
        print("answer_router: Test Ingredient Expert: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Tell me about the sustainability of bananas and pineapples.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Why pineapples have more co2 emissions?",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        
        response = cc.answer_router(userData,"Ok thanks!",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)

#RECIPE EXPERT TEST   
    def test_recipe_expert_with_answer(self):
        print("answer_router: Test Recipe Expert: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Compare the sustainability of a Veggie Lasagna, with a Pasta Carbonara.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you resume the ingredients of both recipe explaining their sustainability?",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok clear!",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)   
 
#RECIPE EXPERT TEST WITH EXPLICIT INGREDIENTS
    def test_recipe_expert_and_ingredients_with_answer(self):
        print("answer_router: Test Recipe Expert with Ingredients: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Compare the sustainability of a Sandwich made of bread, tuna, salad, mayonaise and cheese, with a Pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you resume the ingredients of both recipe explaining their sustainability?",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok thanks.",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)  

#CONCEPT EXPERT TEST
    def test_concept_expert_with_answer(self):
        print("answer_router: Test Concept Expert: Answer Provided")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What is cilmate change?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Is meat a problem in this context?",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok, thank you for the information.",con.TASK_6_40_HOOK,response.memory,"")
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0) 

#FOOD ASSERTION TEST
    def test_from_food_assertion_without_ingredients(self):
        print("answer_question: Food Assertion without Ingredients")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"I've eat a pizza.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #given the absence of ingredients, the system moves to the food diary state asking for the ingredients
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data of the recipe produced
        self.assertTrue(response.info.strip() != '')
        #answer is asking for the ingredients
        self.assertTrue(len(response.answer) > 0)
        
        response = cc.answer_router(userData,"The pizza was made of pizza dough, tomato, mozzarella and basil.",con.TASK_7_HOOK,None,response.info)
        self.print_answers(response)
        #given the absence of meal type, the system moves to the food diary state asking for the ingredients
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data of the recipe produced
        self.assertTrue(response.info.strip() != '')
        #answer is asking for the meal type
        self.assertTrue(len(response.answer) > 0)
        

        response = cc.answer_router(userData,"The pizza was for lunch.",con.TASK_7_HOOK,None,response.info)
        self.print_answers(response)
        #produce the answer and come back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)

    def test_from_food_assertion_with_all_data(self):
        print("answer_question: Food Assertion with All Data")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)        

#PROFILE RECAP
    def test_profile_recap_with_update(self):
        print("answer_question: Profile Recap")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Yes please.",con.TASK_4_10_HOOK,None,response.info)
        self.print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_4_30_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"My surname is Bianchi",con.TASK_4_30_HOOK,None,response.info)
        self.print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)
        #the user data are updated
        self.assertEqual(userData.surname, "Bianchi")

    def test_profile_recap_with_no_update(self):
        print("answer_question: Profile Recap with No Update")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"No thanks.",con.TASK_4_10_HOOK,None,response.info)
        self.print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced (beccause goes back to the hub)
        self.assertTrue(len(response.answer) > 0)

#FOOD HISTORY
    def test_food_history_with_empty_history(self):
        print("answer_question: Food History with Empty History")
        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Can you resume my food history?",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

    def test_food_history_with_provided_history(self):
        print("answer_question: Food History with Provided History")

        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)    

        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Can you resume my food history?",con.TASK_1_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the recap of the food history is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Can you provide the sustainability of each ingredient involved?",con.TASK_5_10_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system loop back to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Ok thanks!",con.TASK_5_10_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

    def test_food_history_with_provided_history_and_change_topic(self):
        print("answer_question: Food History with Provided History and Change Topic")

        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)    

        userData = self.get_valid_user_data()
        response = cc.answer_router(userData,"Can you resume my food history?",con.TASK_1_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the recap of the food history is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"And is mayonaise sustainable?",con.TASK_5_10_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system goes to expert loop
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Ok thanks!",con.TASK_5_10_HOOK,response.memory,"")  
        self.print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)




#run after all the tests
    def tearDown(self):
        up.delete_user_by_user_id("0")
        uhp.delete_user_history("0")
        print("Test completed")

#UTILITY METHODS
    def get_user_data(self):
        return ud.User("Test", 0, None, None, None, None, None, None, None, None, None)
    
    def get_valid_user_data(self):
        return ud.User("Test", 0, "Giacomo", "Rossi", "01/01/1990", "Italy", "", "", "", "", False)
    
    def print_answers(self, response, print_info = True):
        if print_info:
            print(response.answer)

if __name__ == '__main__':
    unittest.main()