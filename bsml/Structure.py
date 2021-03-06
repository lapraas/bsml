
class Structure():
    def __init__(self, walls=None):
        # i've never seen the fucking compounding kwarg behavior in python and it's fucked me twice tonight
        # https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
        self.walls = walls if walls else []
        
    def addWall(self, wall):
        self.walls.append(wall)
    
    def addStructure(self, structure):
        self.walls += structure.walls
    
    def mirror(self):
        temp = self.walls.copy()
        for wall in self.walls:
            temp.append(wall.mirror())
        self.walls = temp
    
    def repeat(self, times, beatOffset):
        temp = self.walls.copy()
        for x in range(1, times + 1):
            curOffset = beatOffset * x
            for wall in self.walls:
                temp.append(wall.clone(wall.beat + curOffset))
        self.walls = temp

    def json(self):
        jsonlist = []
        for wall in self.walls:
            jsonlist.append(wall.json())
        return jsonlist
