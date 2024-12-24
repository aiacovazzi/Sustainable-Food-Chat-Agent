import jsonpickle

class User:
    def __init__(self, username, id, name, surname, dateOfBirth, allergies, restrictions):
        """
        username: the username of the user. Mandatory.
        id: the id of the user. Mandatory.
        name: the name of the user. Mandatory.
        surname: the surname of the user. Mandatory.
        dateOfBirth: the date of birth of the user in the format DD/MM/YYYY. Mandatory.
        allergies: a list of food that the user cannot eat. Optional.
        restrictions: a list of alimentary restrictions derived by ethics choices or religious beliefs. The possible constraints are ["vegan", "vegetarian", "islam", "hinduism", "ebraic"]. Optional.
        """
        self.username = username
        self.id = id
        self.name = name
        self.surname = surname
        self.dateOfBirth = dateOfBirth
        self.allergies = allergies
        self.restrictions = restrictions

    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj['name']
        self.surname = json_obj['surname']
        self.dateOfBirth = json_obj['dateOfBirth']
        self.allergies = json_obj['allergies']
        self.restrictions = json_obj['restrictions']
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)
    
    def to_plain_json(self):
        return jsonpickle.encode(self, unpicklable=False)