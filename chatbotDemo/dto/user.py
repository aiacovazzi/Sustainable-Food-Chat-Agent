import json

class User:
    def __init__(self, name, surname, dateOfBirth, allergies, restrictions):
        """
        name: the name of the user. Mandatory.
        surname: the surname of the user. Mandatory.
        dateOfBirth: the date of birth of the user in the format DD/MM/YYYY. Mandatory.
        allergies: a list of food that the user cannot eat. Optional.
        restrictions: a list of alimentary restrictions derived by ethics choices or religious beliefs. The possible constraints are ["vegan", "vegetarian", "islam", "hinduism", "ebraic"]. Optional.
        """
        self.name = name
        self.surname = surname
        self.dateOfBirth = dateOfBirth
        self.allergies = allergies
        self.restrictions = restrictions

    def __str__(self):
        return f"{{\nname: {self.name},\nsurname: {self.surname},\ndateOfBirth: {self.dateOfBirth},\nallergies: {self.allergies},\nrestrictions: {self.restrictions}\n}}"
    
    #populate fields from a json
    def from_json(self, json_string):
        #convert the string to a json object
        json_obj = json.loads(json_string)
        self.name = json_obj['name']
        self.surname = json_obj['surname']
        self.dateOfBirth = json_obj['dateOfBirth']
        self.allergies = json_obj['allergies']
        self.restrictions = json_obj['restrictions']
        return self