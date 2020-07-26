
# Import all files in the blueprint folder, each of which contain a .create function.
from blueprints import *
# Sift out the blueprint names from the random stuff in globals() to create a list with all of them.
bpnames = [x for x in dir() if not x.startswith("__")]

from Track import Track

class BSMLException(Exception):
    """ Generic exception class to specify an exception while interpreting. """
    pass


class BSMLInterpreter:
    """ An interpreter for the Beat Saber markup language. """
    def __init__(self, text):
        # Text to interpret.
        self.text = text
        # Each line of the text.
        self.lines = []
        # Populate .lines
        for semicsplit in text.split(";"):
            self.lines += semicsplit.split("\n")
        # Each argument block in the text as a list of lines mapped to the line they start on.
        self.blocks = {}
        # A list of created Tracks.
        self.tracks = {}
        # The last-used track name.
        self.lastTrack = None
        # The last-used plan name.
        self.lastPlan = None
        # An index pointer for .lines.
        self.ptr = 0
    
    def run(self):
        """ Run the text given to the interpreter. """
        
        # Current block start line index
        cBlockStart = None
        
        # Find all the comments, "start" and "end" keywords, and remove them.
        # When a "start" keyword is found, set the current block start to the current line and start adding subsequent lines to a list of lines in .blocks.
        # When an "end" keyword is found, stop adding lines to the list in .blocks.
        
        # Iterate through .lines (without a for loop because we're altering .lines)
        while self.ptr < len(self.lines):
            # Current line
            line = self.lines[self.ptr]
            # Find a comment or blank line.
            if line.strip().startswith("#") or not line.strip():
                self.lines.pop(self.ptr)
                self.ptr -= 1
            # Find a "start" keyword.
            elif line.endswith("start"):
                self.lines[self.ptr] = line.replace("start", "")
                cBlockStart = self.ptr
                self.blocks[cBlockStart] = []
            # Find an "end" keyword.
            elif line.endswith("end"):
                self.lines[self.ptr] = line.replace("end", "")
                if not self.lines[self.ptr].strip():
                    self.lines.pop(self.ptr)
                    self.ptr -= 1
                cBlockStart = None
            # Find a line in between a "start" and an "end" keyword.
            elif cBlockStart != None:
                self.lines.pop(self.ptr)
                self.ptr -= 1
                self.blocks[self.ptr].append(line)
            
            self.ptr += 1
        
        # Execute based on the remaining non-block lines. Keywords documented in the conditional string.
        self.ptr = 0
        # Again, iterate through .lines (no alterations this time)
        for line in self.lines:
            # Each word in the line.
            tokens = [tok.strip() for tok in line.strip().split(" ")]
            # Operator keyword to be matched in the conditional string.
            op = tokens[0]
            # Each argument to the operator, supplied to the function called for the operator.
            args = tokens[1:]
            #print("%s: %s" % (op, args))
            
            # Create a new track, with a specified blueprint and a name.
            if op == "track":
                self.newTrack(blueprint=args[0], name=args[1])
            # Define a new plan, for a specified track (by name) and based on a preexisting plan if it exists.
            elif op == "define":
                self.define(name=args[0], block=self.blocks[self.ptr], fromPlan=None if len(args) <= 2 else args[2])
            # Create a new structure, based on a specified track's plan.
            elif op == "create":
                self.create(name=args[0], beat=args[1])
            # Take a list of tracks' plans and create a super-plan, with a given name.
            elif op == "merge":
                self.merge(name=args[0], block=self.blocks[self.ptr])
            
            self.ptr += 1
    
    
    def splitNames(self, name):
        """ Split apart a name in the format `track`:`plan` and return the track name, then the plan name, both .strip()'d. """
        splitName = name.split(":")
        # If there is no track name (no semicolon), assume we are using the last track name and return it.
        return self.lastTrack if len(splitName) < 2 else splitName[0].strip(), splitName[0].strip() if len(splitName) < 2 else splitName[1].strip()
    
    def newTrack(self, blueprint, name):
        """ Callback for the "track" keyword.
            Create a new track with a given blueprint function and name. """
        if not blueprint in bpnames:
            raise BSMLException("Blueprint of name %s not found" % (blueprint,))
        # The blueprint function that will do the creating of the walls.
        blueprintFn = globals()[blueprint] # yes, it's disgusting; yes, it works
        self.tracks[name] = Track(blueprintFn)
        self.lastTrack = name
    
    def define(self, name, block, fromPlan=None):
        """ Callback for the "define" keyword.
            Create a new plan with a given name. """
        # A list of parameters.
        args = {}
        self.lastTrack, self.lastPlan = self.splitNames(name)
        for line in block:
            #print("paramsSet line: %s" % line)
            # The value to put into the create arguments as a key.
            key = line.split(":")[0].strip()
            # A list of values to be assigned to the key in the arguments.
            vals = []
            # Populate the `vals` list by iterating through a "," separated list.
            for val in line.split(":")[1].split(","):
                val = val.strip()
                # Convert `val` into a float if possible.
                floatable = True
                for char in val:
                    if not char in "1234567890.-": floatable = False
                if floatable: val = float(val)
                vals.append(val)
            args[key] = vals
        
        # Get a fromPlan to base the new plan on from the name, if it exists.
        if fromPlan != None:
            fromTrackName, fromPlanName = self.splitNames(fromPlan)
            # Since getPlan returns a list (to account for super-plans), we want to use only the first plan returned.
            fromPlan = self.tracks[fromTrackName].getPlan(fromPlanName)[0]
        
        # Call the Track's .define with the parsed arguments.
        self.tracks[self.lastTrack].define(args, self.lastPlan, fromPlan)
    
    def create(self, name, beat):
        """ Callback for the "create" keyword.
            Create a new structure based on the plans under the given name at the given beat."""
        self.lastTrack, self.lastPlan = self.splitNames(name)
        
        # Call the Track's .create with the parsed arguments.
        self.tracks[self.lastTrack].create(self.lastPlan, float(beat))
    
    def merge(self, name, block):
        """ Callback for the "merge" keyword.
            Merge a series of plans together under one name to make a super-plan. """
        self.lastTrack, self.lastPlan = self.splitNames(name)
        #print("merge start for %s's %s" % (self.lastTrack, self.lastPlan))
        planOffsets = {}
        # Parse the lines containing the plans we want to merge.
        for line in block:
            line = line.strip()
            # The name of the plan will be followed by the beat offset at which it will be placed in relation to the create beat, like "piano:hit at 0"
            splitline = [v.strip() for v in line.split(":")]
            beat = float(splitline[0])
            #print(splitline)
            mergeTrack, mergePlan = self.splitNames(":".join(splitline[1:]))
            #print("merging track %s's %s" % (mergeTrack, paramSetName))
            if not self.tracks[mergeTrack].hasPlan(mergePlan):
                raise BSMLException("Track `%s` has no defined param set `%s`" % (mergeTrack, mergePlan))
            # Set the given plan to the given beat
            planOffsets[beat] = self.tracks[mergeTrack].getPlan(mergePlan)
        
        # Call the Track's .merge with the prepared arguments
        self.tracks[self.lastTrack].merge(self.lastPlan, planOffsets)
    
    def getStructures(self):
        """ Get a list of all structures in all of the Tracks. """
        structures = []
        for trackName in self.tracks:
            track = self.tracks[trackName]
            structures += track.structures
        
        return structures
            
