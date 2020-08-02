
import os

from bsml.Interpreter import BSMLInterpreter

class Suite():
    def __init__(self, folderdir):
        self.structures = []
        for filename in os.listdir(folderdir):
            if filename.endswith(".bsml"):
                with open(os.path.join(folderdir, filename), "r") as trackfile:
                    interpreter = BSMLInterpreter(trackfile.read())
                    interpreter.run()
                    self.structures += interpreter.getStructures()
    
    def json(self):
        jsonWalls = []
        for structure in self.structures:
            jsonWalls += structure.json()
        return jsonWalls
