import persistence.UserHistoryPersistence as userHistoryDB
from datetime import datetime, timedelta
import jsonpickle

def get_user_history_of_week(userId, onlyAccepted = True):
    #get the user history of the week
    fullUserHistory = userHistoryDB.get_user_history(userId)

    if fullUserHistory == None:
        return None

    fullUserHistory = jsonpickle.decode(fullUserHistory)
    #filter the user history of the week
    sysdate = datetime.today()
    previousWeek = sysdate - timedelta(days=7)
    userHistory = []
    for history in fullUserHistory:
        date = datetime.strptime(history['date'], '%Y-%m-%d %H:%M:%S')
        if date >= previousWeek and date <= sysdate and (not onlyAccepted or history['status'] == 'accepted'):
            userHistory.append(history)
    return jsonpickle.encode(userHistory)

def clean_temporary_declined_suggestions(userId):
    userHistoryDB.clean_temporary_declined_suggestions(userId)

def save_user_history(userHistoryJson):
    userHistoryDB.save_user_history(userHistoryJson)