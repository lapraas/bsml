
import copy
import math
import re

from bsml.easings import ez, easings
from bsml.Structure import Structure

class Track:
    def __init__(self, blueprintFn):
        # The blueprint holding the function to create wall Structures.
        self.blueprintFn = blueprintFn
        # A map of previously-used parameters from a plan, used to fill in unfinished plans upon creation.
        self.base = {}
        # A map of names mapped to their respective plans.
        self.plans = {}
        # A map of names mapped to dicts of plan names mapped to beat offset values.
        # {
        #   "superplanexample": {
        #     0: "planAtBeat0",
        #     1: "planAtBeat1"
        #   }
        # }
        self.superplans = {}
        # A map of plan / superplan names mapped to what animation blueprint to creat them with.
        self.animations = {}
        # A list of the Structures created by the blueprint for this track.
        self.structures = []
        
    def define(self, params, name, fromPlanName=None):
        """ Define a new plan with a given name, based on a pre-existing plan if specified. """
        # Get the plan to use as a secondary base.
        fromPlan = {} if not fromPlanName in self.plans else self.plans[fromPlanName]
        
        # Overwrite the full set of parameters based on the original full set (the base), the secondary base (fromPlan), and the given new parameters. 
        self.base = copy.deepcopy({**self.base, **fromPlan, **params})
        
        # Under the given name, add to the dict of single plans an incomplete set of parameters coming from the secondary base and the new parameters.
        self.plans[name] = copy.deepcopy({**fromPlan, **params})
        print("Track: defined new plan %s: %s" % (name, self.plans[name]))
    
    def use(self, name):
        """ Overwrite values on the current set of full params. """
        self.base = {**self.base, **self.plans[name]}
    
    def createStructWithPlan(self, planName, beat, t):
        """ Calls the blueprint function with an evaluated copy of the specified plan and returns a structure with the resulting walls. """
        # The evaluated plan. Initially has the beat and the time along range so that they can be used in self.evaluate.
        evalPlan = {"beat": beat, "t": t}
        # The structure to hold all of the walls in the structures given by the blueprint function.
        struct = Structure()
        # The plan to use. Defaults any unspecified values to the base values, assigned with self.use or self.define.
        plan = {**self.base, **self.plans[planName]}
        
        # Evaluate each item in the plan to use.
        for argName in plan:
            arg = plan[argName]
            evalPlan[argName] = self.evaluate(arg, evalPlan, t)
        
        # Call the blueprint function with the evaluated plan, then add each wall in the list returned to the structure.
        creation = self.blueprintFn(**evalPlan)
        for wall in creation:
            struct.addWall(wall)
        
        # Check to see if we need to mirror the plan.
        if "mirror" in evalPlan and evalPlan["mirror"]:
            struct.mirror()
        
        return struct
    
    def create(self, name, beat, t=0):
        """ At a given beat, create a new Structure based on the a given plan (or superplan). """
        # Get all the plans associated with the given name.
        planNamesWithOffsets = self.getPlanNameListsWithOffsets(name)
        
        walls = Structure()
        
        # Iterate through all of the beat offsets and create each plan there.
        for beatOffset in planNamesWithOffsets:
            #print("subBeat: %s" % subBeat)
            planNameList = planNamesWithOffsets[beatOffset] # Multiple plans can be created on the same beat offset
            for planName in planNameList:
                struct = self.createStructWithPlan(planName, beat + beatOffset, t)
                walls.addStructure(struct)
        
        self.structures.append(walls)
    
    def evaluate(self, argStr, evalPlan, progress):
        """ Evaluates a given arg, replacing each variable with its value, or simply returning it if it's supposed to be a string. """
        #print("evaluating %s" % argStr)
        
        # If the whole thing is surrounded by quotes, return what's inside the two quotes.
        # TODO This is bad - There may come a time when we want a list of strings, and this will need to work recursively (with regex).
        if argStr[0] in "\"'" and argStr[-1] in "\"'":
            return argStr[1:-1]
        # Match groups of letter and underscore characters to be replaced by their corresponding values.
        wordPattern = re.compile(r"[a-zA-Z_]+")
        for word in re.findall(wordPattern, argStr):
            #print(word)
            # Check to see if the matched word is an easing, then call its function if it is.
            if word in easings:
                argStr = argStr.replace(word, str(ez(word, progress)))
            # Check to see whether or not the word has been evaluated.
            elif word in evalPlan:
                argStr = argStr.replace(word, str(evalPlan[word]), 1)
            # If the word isn't an easing and the word hasn't been evaluated, grab whatever matches from the base parameters.
            elif word in self.base:
                argStr = argStr.replace(word, self.base[word], 1)
                # Since the base parameters are unevaluated, we need to recurse.
                return self.evaluate(argStr, evalPlan, progress)
            else:
                raise Exception("Unknown keyword \"%s\", surround entire arg in quotes to skip keyword evaluation" % word)
        
        return eval(argStr)
    
    def merge(self, name, superplan):
        """ Take multiple plans and combine them into a superplan (a series of plan names assigned to beats). """
        #print("Track: Merged to create plan %s" % name)
        if name in self.plans:
            self.plans.pop(name)
            print("Deleted plan for superplan with same name (%s)" % name)
        
        self.superplans[name] = superplan
    
    def assignAnim(self, planName, animCreateFn):
        self.animations[planName] = animCreateFn
    
    def getPlanNameListsWithOffsets(self, targetName, beat=0, ret=None):
        """ Return a dict of plan names (not superplan names) mapped to beat offsets. """
        if ret == None:
            # ok fuck python
            # https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
            ret = {}
        
        # We want to be able to grab multiple plans that have the same name as the targetName with an added dot suffix.
        # To do this, we iterate through all existing plan names.
        for planName in self.plans:
            splitName = planName.split(".")
            # If the plan name doesn't have a dot, we don't care about it.
            if len(splitName) == 1: continue
            if splitName[0] == targetName:
                #print("getting subplan of %s: %s" % (targetName, planName))
                # Recursively call so that we can nest dot suffixes.
                ret = self.getPlanNameListsWithOffsets(planName, beat, ret)
        # Now we do the simplest check to see if the targetName is a single plan.
        if targetName in self.plans:
            if not beat in ret:
                #print("making new list for beat %s" % beat)
                ret[beat] = []
            ret[beat].append(targetName)
        # If it's not a single plan, we check to see if it's a superplan.
        elif targetName in self.superplans:
            # A superplan is a collection of plan names mapped to beat offsets, so we have to iterate through each
            for beatOffset in self.superplans[targetName]:
                # Recursively call to account for nested superplans.
                ret = self.getPlanNameListsWithOffsets(self.superplans[targetName][beatOffset], beat + beatOffset, ret)
        
        return ret
