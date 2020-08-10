
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
    
    def create(self, name, beat, tStart=None, tEnd=None):
        """ At a given beat, create a new Structure based on the a given plan (or superplan). """
        # Get all the plans associated with the given name.
        planListsWithOffsets = self.getPlans(name)
        #print("self.plans after self.getPlans: %s" % self.plans)

        # When called with a range, these values are used to handle how far across the range the current function call is.
        dist = 0 if not tStart else beat - tStart
        t = 0 if not tStart else dist / (tEnd - tStart) # The percent of progress through the range.
        #print("planListsWithOffsets: %s" % planListsWithOffsets)
        
        walls = Structure()
        
        # Iterate through all of the beat offsets
        for beatOffset in planListsWithOffsets:
            #print("subBeat: %s" % subBeat)
            planList = planListsWithOffsets[beatOffset] # Multiple plans can be created on the same beat offset
            for plan in planList:
                #print("plan: %s" % plan)
                cPlan = {"beat": beat + beatOffset, "t": t}
                tempStruc = Structure()
                for argName in plan:
                    arg = plan[argName]
                    cPlan[argName] = self.evaluate(arg, cPlan, t)
                evaldBase = {}
                for argName in self.base:
                    arg = self.base[argName]
                    evaldBase[argName] = self.evaluate(arg, cPlan, t)
                
                compound = {**evaldBase, **cPlan}
                creation = self.blueprintFn(**compound)
                if type(creation) == list:
                    for wall in creation:
                        tempStruc.addWall(wall)
                else:
                    tempStruc.addWall(creation)
                if "mirror" in compound and compound["mirror"]:
                    tempStruc.mirror()
                walls.addStructure(tempStruc)
        
        self.structures.append(walls)
    
    def evaluate(self, argStr, cPlan, progress):
        #print("evaluating %s" % argStr)
        if argStr[0] in "\"'" and argStr[-1] in "\"'":
            return argStr[1:-1]
        wordPattern = re.compile(r"[a-zA-Z_]+")
        for word in re.findall(wordPattern, argStr):
            #print(word)
            if word in easings:
                argStr = argStr.replace(word, str(ez(word, progress)))
            else:
                try:
                    argStr = argStr.replace(word, str(cPlan[word]) if word in cPlan else self.base[word], 1)
                except KeyError:
                    raise Exception("Unknown keyword \"%s\", surround entire arg in quotes to skip keyword evaluation" % word)
        try:
            return eval(argStr)
        except NameError:
            return self.evaluate(argStr, cPlan, progress)
    
    def merge(self, name, superplan):
        """ Take multiple plans and combine them into a superplan (a series of plan names assigned to beats). """
        #print("Track: Merged to create plan %s" % name)
        if name in self.plans:
            self.plans.pop(name)
            print("Deleted plan for superplan with same name (%s)" % name)
        
        self.superplans[name] = superplan
    
    def assignAnim(self, superplanName, animCreateFn):
        self.animations[superplanName] = animCreateFn
    
    def getPlans(self, targetName, beat=0, ret=None):
        """ Return a dict of lists of plans mapped to beat offsets. """
        #print("getting plans under target name %s" % targetName)
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
                ret = self.getPlans(planName, beat, ret)
        # Now we do the simplest check to see if the targetName is a single plan.
        if targetName in self.plans:
            if not beat in ret:
                #print("making new list for beat %s" % beat)
                ret[beat] = []
            ret[beat].append(copy.deepcopy(self.plans[targetName]))
        # If it's not a single plan, we check to see if it's a superplan.
        elif targetName in self.superplans:
            # A superplan is a collection of plan names mapped to beat offsets, so we have to iterate through each
            for beatOffset in self.superplans[targetName]:
                # Recursively call to account for nested superplans.
                ret = self.getPlans(self.superplans[targetName][beatOffset], beat + beatOffset, ret)
        #print("Track: getPlans returns: %s" % ret)
        return ret
