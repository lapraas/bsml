
class Track:
    def __init__(self, blueprint):
        # The blueprint holding the function to create wall Structures.
        self.blueprint = blueprint
        # A map of previously-used parameters from a plan, used to merge with new parameters / plan.
        self.params = {}
        # A map of names mapped to their respective plans.
        self.plans = {}
        # A list of the Structures created by the blueprint for this track.
        self.structures = []
        
    def define(self, params, name, fromPlan=None):
        """ Define a new plan with a given name, based on a pre-existing plan if specified. """
        # Update the current set of parameters to feed to the blueprint with new parameters.
        newParams = {**(self.params if not fromPlan else fromPlan), **params}
        
        self.params = newParams
            
        # Create a full set of parameters mapped to the given name, and put it into a list to account for superplans.
        self.plans[name] = [self.params]
    
    def create(self, name, beat):
        """ At a given beat, create a new Structure (or new Structures) based on the a given plan (or superplan). """
        plans = self.plans[name]
        for plan in plans:
            # Copy plan.
            tempPlan = {**plan}
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
                arg = tempPlan[argName]
                if arg in tempPlan:
                    tempPlan[argName] = tempPlan[arg]
                if not isinstance(arg, float):
                    tempPlan[argName] = float(eval(arg))
            self.structures.append(self.blueprint.create(**tempPlan))
    
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
