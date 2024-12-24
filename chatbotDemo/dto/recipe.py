import jsonpickle

class Food:
    def __init__(self, name, cfp, wfp):
        self.name = name
        self.cfp = cfp
        self.wfp = wfp
    
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.cfp = json_obj.cfp
        self.wfp = json_obj.wfp
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)

class Recipe:
    def __init__(self, name, id, listOfFoods, sustainabilityScore, instructions, description, removedConstraints):
        self.name = name
        self.id = id
        self.listOfFoods = listOfFoods
        self.sustainabilityScore = sustainabilityScore
        self.instructions = instructions
        self.description = description
        self.removedConstraints = removedConstraints
        
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.id = json_obj.id
        self.listOfFoods = json_obj.listOfFoods
        self.sustainabilityScore = json_obj.sustainabilityScore
        self.instructions = json_obj.instructions
        self.description = json_obj.description
        self.removedConstraints = json_obj.removedConstraints
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)