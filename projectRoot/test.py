import unittest
import ChatbotController as cc
import Constants as con
import dto.User as ud
import persistence.UserPersistence as up

#Collection of test cases
class TestController(unittest.TestCase):

#USER REGISTRATION TESTS
    def test_user_registration(self):
        print("Test User Registration Presentation")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello",con.TASK_0_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        #user data not changed because the system is still asking for the user data
        self.assertTrue(userData.name is None)
        self.assertTrue(len(response.answer) > 0)

    def test_user_registration_pt_2(self):
        print("Test User Registration Presentation: No Data Provided")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(userData.name == '')
        #answer not empy because the system is asking for the user data since none was provided
        self.assertTrue(len(response.answer) > 0)

    def test_user_registration_pt_3(self):
        print("Test User Registration Presentation: Partial Data Provided")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello, I'm Giacomo Rossi.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "")        
        #answer not empy because the system is asking for the user data since none was provided
        self.assertTrue(len(response.answer) > 0)

    def test_user_registration_pt_4(self):
        print("Test User Registration Presentation: All Mandatory Data Provided")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")

    def test_user_registration_pt_5(self):
        print("Test User Registration Presentation: All Mandatory and Optiona Data Provided")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990. Im allergic to peanut and fish. I Follow a vegan diet.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response, True)
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

    def test_user_registration_pt_6(self):
        print("Test User Registration Presentation: All Mandatory Data Provided; Then Provide Reminder Consent")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")
        response = cc.aswer_router(userData,"Yes I want reminders",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, True)

    def test_user_registration_pt_7(self):
        print("Test User Registration Presentation: All Mandatory Data Provided, But In Two Step; Then Negate Reminder Consent")
        userData = self.get_user_data()
        response = cc.aswer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.dateOfBirth, "")
        self.assertEqual(userData.allergies,"")
        self.assertEqual(userData.restrictions, "")


        response = cc.aswer_router(userData,"I was born on 01/01/1990, i'm also allergic to peanuts.",con.TASK_0_1_HOOK,"",None)
        self.print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertTrue("peanut" in userData.allergies)
        self.assertEqual(userData.restrictions, "")

        response = cc.aswer_router(userData,"No thanks.",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, False)

#HUB TESTS
    def test_greetings(self):
        print("Test Greetings")
        response = cc.aswer_router(self.get_user_data(),con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,None,"")
        self.print_answers(response)
        #check if the generated token is equal to the expected token, that info are empty and the answer is not empty
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
        #this means that the bot has greeted the user




#run after all the tests
    def tearDown(self):
        up.delete_user_by_user_id("0")
        print("Test completed")

#UTILITY METHODS
    def get_user_data(self):
        return ud.User("Test", 0, None, None, None, None, None, None, None, None, None)
    
    def get_valid_user_data(self):
        return ud.User("Test", 0, "Giacomo", "Rossi", "01/01/1990", "Italy", "", "", "", "", False)
    
    def print_answers(self, response, print_info = False):
        if print_info:
            print(response.answer)

if __name__ == '__main__':
    unittest.main()