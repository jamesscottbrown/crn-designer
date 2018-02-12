import json
from sympy import Symbol, exp
from CRNSynthesis.symbolicLNA import *
from CRNSynthesis import iSATParser

def getProblem(crn_sketch_string, specification_string):

    crn_details = CRNbuilder(crn_sketch_string)
    input_species = get_input_species(specification_string)
    crn = CRNSketch(crn_details.required_reactions, crn_details.optional_reactions, input_species)

    isLNA, requiredDerivatives, specification = construct_specification(specification_string)

    flow = crn.flow(isLNA, requiredDerivatives)
    return iSATParser.constructISAT(crn, specification, flow, costFunction='')


def construct_specification(specification_string):
    spec = json.loads(specification_string)

    derivatives = []
    isLNA = False
    for subplot in spec["subplot_geoms"]:
        variable_name = subplot["variable_name"]

        if variable_name.startswith("E(") or variable_name.startswith("Var("):
            isLNA = True

        if "'" in variable_name:
            derivatives.append(convert_derivative_name(variable_name))


    # TODO: convert derivatives to the required format


    # TODO: process the modes and intervals

    specification = []

    return isLNA, derivatives, specification


def convert_derivative_name(name):
    num_primes = len(name) - len(name.replace("'", ""))

    is_variance = False
    if name.index("E(") == 0:
        variable = name[2:-1]  # strip of 'E(' from start, and ')' from end
    elif name.index("Var(") == 0:
        variable = name[4:-1]  # strip of 'Var(' from start, and ')' from end
        is_variance = True
    else:
        variable = name

    variable = variable.replace("'", "")

    return {"variable": variable, "order": num_primes, "is_variance": is_variance} # TODO: set name


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
            input_odes[Symbol(base_variable_name)] = InputSpecies(Symbol(base_variable_name), start_value, flow)

    return input_odes


class CRNbuilder:
    # Constructs a CRNSketch object from JSON serialization of a diagram

    def __init__(self, crn_sketch):
        self.choice_index = 0

        crn_data = json.loads(crn_sketch)
        print crn_data

        stoichiometries = {}
        for stoich in crn_data["stoichiometries"]:
            stoichiometries[stoich["name"]] = stoich

        # one dict stores both species and species variables
        speciesVariables = {}
        for sv in crn_data["speciesVariables"]:
            speciesVariables[sv["name"]] = LambdaChoice([Species(x) for x in sv["species"]], len(speciesVariables))
        for sv in crn_data["species"]:
            speciesVariables[sv["name"]] = Species(sv["name"], initial_min=sv["initial_min"], initial_max=sv["initial_min"])


        rate_constants = {}
        for rc in crn_data["rates"]:
            rate_constants[rc["name"]] = RateConstant(rc["name"], rc["min"], rc["max"])

        for constraint in crn_data["constraints"]:
            pass

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
                        actual_reactant = filter(lambda x: x["id"] == or_link["target_id"], crn_data["nodes"])[0]
                        alternatives.append(self.getTerm(actual_reactant["label"], or_link["stoichiometry"], stoichiometries, speciesVariables))

                    reactant_objects.append(Or(alternatives))

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
                    or_product_links = filter(lambda x: x["source_id"] == reactant["id"], crn_data["links"])
                    for or_link in or_product_links:
                        actual_product = filter(lambda x: x["id"] == or_link["source_id"], crn_data["nodes"])[0]
                        alternatives.append(self.getTerm(actual_product["label"], link["stoichiometry"], stoichiometries, speciesVariables))

                    product_objects.append(Or(alternatives))

                else:
                    product_objects.append(self.getTerm(product["label"], link["stoichiometry"], stoichiometries, speciesVariables))

            reaction_rate = rate_constants[reaction["label"]]

            if "required" in reaction.keys() and reaction["required"]:
                required_reaction_objects.append(Reaction(reactant_objects, product_objects, reaction_rate))
            else:
                optional_reaction_objects.append(Reaction(reactant_objects, product_objects, reaction_rate))

        self.required_reactions = required_reaction_objects
        self.optional_reactions = optional_reaction_objects

    def getTerm(self, species_name, stoichiometry, stoichiometries, speciesVariables):

        # Create a Term object from a species name (which may be an actual species or speciesVariable) and stoichiometry
        # (which may be a numerical value, a stoichiometricVariable, or '?')

        species = speciesVariables[species_name] # replace name with species object

        if stoichiometry in stoichiometries.keys():
            return Term(species, Choice(self.choice_index, stoichiometries[species]["min"], stoichiometries[species]["max"]))
            self.choice_index += 1
            # why second stoichiomery argument?

        elif stoichiometry == '?':
            return Term(species, Choice(self.choice_index, 0, 2))
            self.choice_index += 1

        else:
            return Term(species, stoichiometry)
