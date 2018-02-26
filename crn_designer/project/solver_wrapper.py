import json
from sympy import Symbol, exp
from CRNSynthesis.symbolicLNA import *
from CRNSynthesis import iSATParser

def getProblem(crn_sketch_string, specification_string):

    input_species = get_input_species(specification_string)

    crn_details = CRNbuilder(crn_sketch_string, input_species)
    crn = CRNSketch(crn_details.required_reactions, crn_details.optional_reactions, input_species)

    isLNA, requiredDerivatives, specification = construct_specification(specification_string)

    flow = crn.flow(isLNA, requiredDerivatives)
    return iSATParser.constructISAT(crn, specification, flow, crn_details.constraints)


def construct_specification(specification_string):
    spec = json.loads(specification_string)

    derivatives = []
    isLNA = False
    for subplot in spec["subplot_geoms"]:
        variable_name = subplot["variable_name"]

        if variable_name.startswith("E(") or variable_name.startswith("Var("):
            isLNA = True

        if "'" in variable_name:
            new_variable_name = convert_derivative_name(variable_name)
            new_variable_name["name"] = reformat_variable_name(new_variable_name)
            derivatives.append(new_variable_name)

    modes = []
    for subplot_index, subplot in enumerate(spec["subplot_geoms"]):
        if subplot["subplot_type"] == "input":
            continue

        variable = reformat_variable_name(convert_derivative_name(subplot["variable_name"]))
        for rect_index, rectangle in enumerate(subplot["rectangles"]):
            constraint = "((%s >= %s) and (%s <= %s))" % (variable, rectangle["min_val"], variable, rectangle["max_val"])

            new_mode = {"pre": [], "post": [], "during": [constraint], "locations": [(subplot_index, rect_index)],
                          "kind": rectangle["kind"], "min_time": rectangle["min_time"], "max_time": rectangle["max_time"],
                          "following": rectangle["following"], "siblings": rectangle["siblings"]};

            if new_mode["following"]:
                new_mode["following"] = (new_mode["following"]["subplot_index"], new_mode["following"]["rect_index"])

            modes.append(new_mode)
            print constraint

    # TODO: if modes are siblings, merge them into a single mode (join conditions with 'and', join locations array)

    # Merge intervals following a mode into post-conditions on that mode
    intervals = filter(lambda x: x["kind"] == "interval", modes)
    while len(intervals) > 0:
        for interval in intervals:

            if interval["following"]:

                # add the constraint imposed by this interval to the post-condition of mode being followed
                for mode in filter(lambda x: interval["following"] in x["locations"], modes):
                    mode["post"].extend(interval["during"])

                # if anything was following this interval, set it to follow what the interval is following
                pos = interval["locations"][0] # intervals not emrged, so will only have one location
                for mode in modes:
                    if pos == mode["following"]:
                        mode["following"] = interval["following"]

                intervals.remove(interval)
                modes.remove(interval)

            else:
                intervals.remove(interval)
                break # we've changed list so don't try to continue iterating over it

    # TODO: Process intervals that are followed by modes *proceeding modes*
    intervals = filter(lambda x: x["kind"] == "interval", modes)
    while len(intervals) > 0:
        for interval in intervals:
            pass

    # sort modes by start time
    modes.sort(key=lambda x: x["min_time"])

    # convert to output format, including empty modes if there are any gaps
    output_modes = []
    start_time = modes[0]["min_time"]
    for mode in modes:
        if mode["min_time"] != start_time:
            output_modes.append(('', '', ''))
        start_time = mode["max_time"]
        output_modes.append((" and ".join(mode["pre"]), " and ".join(mode["during"]), " and ".join(mode["post"])))

    return isLNA, derivatives, output_modes

def reformat_variable_name(variable):
    name = ""
    if variable["is_variance"]:
        name = "var_"
    name += variable["variable"]
    name += "_dot" * variable["order"]
    return name


def convert_derivative_name(name):
    num_primes = len(name) - len(name.replace("'", ""))
    name = name.replace("'", "")

    is_variance = False
    if "E(" in name and name.index("E(") == 0:
        variable = name[2:-1]  # strip of 'E(' from start, and ')' from end
    elif "Var(" in name and name.index("Var(") == 0:
        variable = name[4:-1]  # strip of 'Var(' from start, and ')' from end
        is_variance = True
    else:
        variable = name


    return {"variable": str(variable), "order": num_primes, "is_variance": is_variance} # TODO: set name


def get_input_species(specification_string):

    spec = json.loads(specification_string)
    input_odes = {}

    for subplot in spec["subplot_geoms"]:
        if subplot["subplot_type"] == "input":
            func = 0
            start_value = 0
            t = Symbol("t")

            for term in subplot["inputSubplot"]:

                param = term["parameters"]

                if term["type"] == "linear":

                    start_value += float(param["intercept"])
                    func += float(param["gradient"]) * t

                elif term["type"] == "sigmoidal":

                    initial_value = float(param["initial_value"])
                    midpoint_time = float(param["midpoint_time"])
                    final_value = float(param["final_value"])
                    hill_coefficient = float(param["hillCoefficient"])

                    start_value += initial_value
                    func += (final_value - initial_value) / (((midpoint_time / t) ** hill_coefficient) + 1)

                elif term["type"] == "bell":
                    initial_value = float(param["initial_value"])
                    peak_value = float(param["peak_value"])
                    peak_time = float(param["peak_time"])
                    sigma = float(param["sigma"])

                    start_value += initial_value
                    func += (peak_value - initial_value) * exp(-((t - peak_time) / sigma) ** 2)

            flow = Derivative(func, t).doit()

            base_name = subplot["base_variable_name"]
            input_odes[base_name] = InputSpecies(base_name, start_value, flow)

    return input_odes


class CRNbuilder:
    # Constructs a CRNSketch object from JSON serialization of a diagram

    def __init__(self, crn_sketch, input_species):
        self.choice_index = 0
        self.term_choice_index = 0
        self.lambda_choice_index = 0

        crn_data = json.loads(crn_sketch)
        print crn_data

        stoichiometries = {}
        for stoich in crn_data["stoichiometries"]:
            name = str(stoich["name"])
            stoichiometries[name] = Choice(self.choice_index, int(stoich["min"]), int(stoich["max"]))
            stoichiometries[name].name = name
            stoichiometries[name].symbol = symbols(name)
            self.choice_index += 1

        # one dict stores both species and species variables
        speciesVariables = {}
        for sv in crn_data["species"]:
            speciesVariables[sv["name"]] = Species(sv["name"], initial_min=sv["initial_min"], initial_max=sv["initial_max"])

        for sv in crn_data["speciesVariables"]:
            speciesVariables[sv["name"]] = LambdaChoice([speciesVariables[x] for x in sv["species"]], self.lambda_choice_index)
            self.lambda_choice_index += 1
        for sv in input_species:
            speciesVariables[sv] = input_species[sv]


        rate_constants = {}
        for rc in crn_data["rates"]:
            rate_constants[rc["name"]] = RateConstant(rc["name"], rc["min"], rc["max"])

            if rc["kineticsType"] == "Mass Action":
                rate_constants[rc["name"]+"_km"] = RateConstant(rc["name"]+"_km", rc["Km_min"], rc["Km_max"])
            elif rc["kineticsType"] in ["Hill (Activation)", "Hill (Repression)"]:
                rate_constants[rc["name"]+"_ka"] = RateConstant(rc["name"]+"_ka", rc["Ka_min"], rc["Ka_max"])
                rate_constants[rc["name"]+"_n"] = RateConstant(rc["name"]+"_n", rc["n_min"], rc["n_max"])

        self.constraints = crn_data["constraints"]

        # first get all reactions
        required_reaction_objects = []
        optional_reaction_objects = []

        reactions = filter(lambda x: x["type"] == "reaction", crn_data["nodes"])

        for reaction in reactions:
            # find reactants
            reactant_objects = []
            reactant_links = filter(lambda x: x["target_id"] == reaction["id"], crn_data["links"])
            for link in reactant_links:
                reactant = filter(lambda x: x["id"] == link["source_id"], crn_data["nodes"])[0]

                if reactant["type"] == "or-reactant":

                    alternatives = []
                    or_reactant_links = filter(lambda x: x["target_id"] == reactant["id"], crn_data["links"])
                    for or_link in or_reactant_links:
                        actual_reactant = filter(lambda x: x["id"] == or_link["source_id"], crn_data["nodes"])[0]
                        alternatives.append(self.getTerm(actual_reactant["label"], or_link["stoichiometry"], stoichiometries, speciesVariables))

                    reactant_objects.append(TermChoice(self.term_choice_index, alternatives))
                    self.term_choice_index += 1

                else:
                    reactant_objects.append(self.getTerm(reactant["label"], link["stoichiometry"], stoichiometries, speciesVariables))

            # find products
            product_objects = []
            product_links = filter(lambda x: x["source_id"] == reaction["id"], crn_data["links"])
            for link in product_links:
                product = filter(lambda x: x["id"] == link["target_id"], crn_data["nodes"])[0]

                if product["type"] == "reaction":
                    continue

                if product["type"] == "or-product":

                    alternatives = []
                    or_product_links = filter(lambda x: x["source_id"] == product["id"], crn_data["links"])
                    for or_link in or_product_links:
                        actual_product = filter(lambda x: x["id"] == or_link["target_id"], crn_data["nodes"])[0]
                        alternatives.append(self.getTerm(actual_product["label"], or_link["stoichiometry"], stoichiometries, speciesVariables))

                    product_objects.append(TermChoice(self.term_choice_index, alternatives))
                    self.term_choice_index += 1

                else:
                    product_objects.append(self.getTerm(product["label"], link["stoichiometry"], stoichiometries, speciesVariables))

            reaction_rate = rate_constants[reaction["label"]]

            kinetics_type = filter(lambda x: x["name"] == reaction_rate.name, crn_data["rates"])[0]["kineticsType"]

            if kinetics_type == "Mass Action":
                new_reaction = Reaction(reactant_objects, product_objects, reaction_rate)
            elif kinetics_type == "Michaelis-Menten":
                Km = rate_constants[reaction["label"] + "_km"]
                new_reaction = MichaelisMentenReaction(reactant_objects, product_objects, reaction_rate, Km)
            elif kinetics_type == "Hill (Activation)":
                Ka = rate_constants[reaction["label"] + "_ka"]
                n = rate_constants[reaction["label"] + "_n"]
                new_reaction = HillActivationReaction(reactant_objects, product_objects, reaction_rate, Ka, n)
            elif kinetics_type == "Hill (Repression)":
                Ka = rate_constants[reaction["label"] + "_ka"]
                n = rate_constants[reaction["label"] + "_n"]
                new_reaction = HillRepressionReaction(reactant_objects, product_objects, reaction_rate, Ka, n)

            if "required" in reaction.keys() and reaction["required"]:
                required_reaction_objects.append(new_reaction)
            else:
                optional_reaction_objects.append(new_reaction)

        self.required_reactions = required_reaction_objects
        self.optional_reactions = optional_reaction_objects

    def getTerm(self, species_name, stoichiometry, stoichiometries, speciesVariables):

        # Create a Term object from a species name (which may be an actual species or speciesVariable) and stoichiometry
        # (which may be a numerical value, a stoichiometricVariable, or '?')

        species = speciesVariables[species_name] # replace name with species object

        if stoichiometry in stoichiometries.keys():
            return Term(species, stoichiometries[stoichiometry])

        elif stoichiometry == '?':
            self.choice_index += 1
            return Term(species, Choice(self.choice_index, 0, 2))

        else:
            return Term(species, int(stoichiometry))
