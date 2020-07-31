
import copy
from inspect import signature
import re

class Track:
    def __init__(self, blueprint):
        # The blueprint holding the function to create wall Structures.
        self.blueprint = blueprint
        # A map of previously-used parameters from a plan, used to fill in unfinished plans upon creation.
        self.params = {}
        # A map of names mapped to their respective plans.
        self.plans = {}
        # A list of the Structures created by the blueprint for this track.
        self.structures = []
        
    def define(self, params, name, fromPlanName=None):
        """ Define a new plan with a given name, based on a pre-existing plan if specified. """
        # Update the current set of parameters to feed to the blueprint with new parameters.
        fromPlan = {} if not fromPlanName in self.plans else self.plans[fromPlanName][0]
        newParams = {**self.params, **fromPlan, **params}
        print("Track: defining new plan %s: %s" % (name, newParams))
        print("Track:   fromPlan: %s" % fromPlan)
        
        self.params = newParams
            
        # Create a full set of parameters mapped to the given name, and put it into a list to account for superplans.
        self.plans[name] = [{**copy.deepcopy({**fromPlan, **params, "name": name})}]
    
    def create(self, name, beat):
        """ At a given beat, create a new Structure (or new Structures) based on the a given plan (or superplan). """
        planList = self.plans[name]
        for plan in planList:
            # Copy plan so that we aren't overwriting keyword evaluations and making them happen multiple times
            tempPlan = {**copy.deepcopy(self.params), **copy.deepcopy(plan)}
            # Superplans have plans in them that already have their "beat" attribute defined,
            #   which means we add that value to the beat (treat it like an offset).
            if "beat" in tempPlan:
                tempPlan["beat"] += beat
            else:
                tempPlan["beat"] = beat
            
            # Allow for reuse of a value by entering that value's name in as the value.
            # For example,
            # define example start
            #     phase: 180 * (10/14)
            #     lrotz: phase (<- reused phase value)
            # end
            for argName in tempPlan:
                if argName in ["beat", "name"]: continue
                argList = tempPlan[argName]
                for index, arg in enumerate(argList):
                    if arg in tempPlan:
                        #print("replaced arg %s in tempPlan with %s, which was %s" % (argName, arg, tempPlan[arg]))
                        tempPlan[argName][index] = tempPlan[arg][index if len(tempPlan[arg]) > 1 else 0]
                    # Also evaluate arguments that aren't the easing function as math expressions, giving them access to the prior arguments used by this track.
                    elif not index == 2:
                        #print("arg %s: %s" % (argName, arg))
                        #tempPlan[argName][index] = float(eval(arg, None, singleArgTPlans[index]))
                        wordPattern = re.compile(r"[A-z]+")
                        for word in re.findall(wordPattern, arg):
                            arg = arg.replace(word, str(tempPlan[word][index if len(tempPlan[word]) > 1 else 0]))
                        tempPlan[argName][index] = eval(arg)
                        
            
            #print("Track: Created with plan base %s, real vals %s" % (plan, tempPlan))
            verbose = True
            print("Track: Created subplan %s%s" % (tempPlan.pop("name"), "" if not verbose else (": %s" % tempPlan)))
                    
            # Run the blueprint.
             
            self.structures.append(self.blueprint.create(**tempPlan))
        print("Track: Created with plan %s" % name)
    
    def merge(self, name, plansWithOffsets):
        """ Take multiple plans and combine them into a superplan. """
        superplan = []
        for beat in plansWithOffsets:
            for plan in plansWithOffsets[beat]:
                # If we're combining a superplan, we want to preserve the beat offsets for the plans in that superplan as well -
                #   this just means adding the offset to each plan of the superplan's "beat" attr.
                if not "beat" in plan:
                    plan["beat"] = beat
                else:
                    plan["beat"] += beat
                superplan.append(plan)
        print("Track: Merged to create plan %s" % name)
        self.plans[name] = superplan

    def hasPlan(self, name):
        """ Return whether or not this Track has a plan by the given name. """
        return name in self.plans
    
    def getPlan(self, name):
        """ Return a list of plans under the given name. """
        ret = []
        for paramSet in self.plans[name]:
            ret.append({**paramSet})
        return ret
