
import copy
import math
import re

from bsml.easings import ez, easings
from bsml.Structure import Structure

class Track:
    def __init__(self, blueprint):
        # The blueprint holding the function to create wall Structures.
        self.blueprint = blueprint
        # A map of previously-used parameters from a plan, used to fill in unfinished plans upon creation.
        self.base = {}
        # A map of names mapped to their respective plans.
        self.plans = {}
        # A map of names mapped to dicts of plans mapped to beat offset values.
        self.superplans = {}
        # A list of the Structures created by the blueprint for this track.
        self.structures = []
        
    def define(self, params, name, fromPlanName=None):
        """ Define a new plan with a given name, based on a pre-existing plan if specified. """
        # Update the current set of parameters to feed to the blueprint with new parameters.
        fromPlan = {} if not fromPlanName in self.plans else self.plans[fromPlanName]
        
        # Create a full set of parameters mapped to the given name, and put it into a list to account for superplans.
        self.plans[name] = copy.deepcopy({**fromPlan, **params})
        print("Track: defined new plan %s: %s" % (name, self.plans[name]))
    
    def use(self, name):
        """ Overwrite values on the current set of full params. """
        self.base = {**self.base, **self.plans[name]}
    
    def create(self, name, beat, tStart=None, tEnd=None):
        """ At a given beat, create a new Structure based on the a given plan (or superplan). """
        planListsWithOffsets = self.getPlans(name)
        #print("self.plans after self.getPlans: %s" % self.plans)
        
        dist = 0 if not tStart else beat - tStart
        t = 0 if not tStart else dist / (tEnd - tStart)
        #print("planListsWithOffsets: %s" % planListsWithOffsets)
        
        walls = Structure()
        
        for subBeat in planListsWithOffsets:
            #print("subBeat: %s" % subBeat)
            for plan in planListsWithOffsets[subBeat]:
                print("plan: %s" % plan)
                cPlan = {"beat": beat + subBeat, "t": t}
                tempStruc = Structure()
                for argName in plan:
                    arg = plan[argName]
                    cPlan[argName] = self.evaluate(arg, cPlan, t)
                evaldBase = {}
                for argName in self.base:
                    arg = self.base[argName]
                    evaldBase[argName] = self.evaluate(arg, cPlan, t)
            
                tempStruc.addWall(self.blueprint.create(**{**evaldBase, **cPlan}))
                if "mirror" in cPlan and cPlan["mirror"]:
                    tempStruc.mirror()
                walls.addStructure(tempStruc)
        
        self.structures.append(walls)
    
    def evaluate(self, argStr, cPlan, progress):
        #print("evaluating %s" % argStr)
        wordPattern = re.compile(r"[a-zA-Z_]+")
        for word in re.findall(wordPattern, argStr):
            #print(word)
            if word in easings:
                argStr = argStr.replace(word, str(ez(progress)))
            else:
                argStr = argStr.replace(word, str(cPlan[word]) if word in cPlan else self.base[word], 1)
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
    
    def getPlans(self, targetName, beat=0, ret=None):
        """ Return a dict of lists of plans mapped to beat offsets. """
        #print("getting plans under target name %s" % targetName)
        if ret == None:
            # ok fuck python
            # https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
            ret = {}
        for planName in self.plans:
            splitName = planName.split(".")
            if len(splitName) == 1: continue
            if splitName[0] == targetName:
                #print("getting subplan of %s: %s" % (targetName, planName))
                ret = self.getPlans(planName, beat, ret)
        if targetName in self.plans:
            if not beat in ret:
                #print("making new list for beat %s" % beat)
                ret[beat] = []
            ret[beat].append(copy.deepcopy(self.plans[targetName]))
        elif targetName in self.superplans:
            ret = self.getPlans(targetName, beat, ret)
        #print("Track: getPlans returns: %s" % ret)
        return ret
