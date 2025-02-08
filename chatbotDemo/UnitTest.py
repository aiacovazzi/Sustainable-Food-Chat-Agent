import unittest
import ChatbotController as cc
import Constants as con
import dto.User as ud

class TestController(unittest.TestCase):

    def test_greetings(self):
        print("Test Greetings")
        response = cc.answer_question(self.get_user_data(),con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(response.answer.__len__() > 0)

    def get_user_data(self):
        return ud.User("Test", 0, "Test", None, None, None, None, None)

if __name__ == '__main__':
    unittest.main()