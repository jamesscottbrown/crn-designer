import json
from sympy import Symbol
from CRNSynthesis.symbolicLNA import Reaction, CRNSketch, Species,  Choice, LambdaChoice

def construct_crn(crn_sketch):
    crn_data = json.loads(crn_sketch)
    print crn_data

    stoichiometries = {}
    for stoich in crn_data["stoichiometries"]:
        stoichiometries[stoich["name"]] = stoich

    speciesVariables = {}
    for sv in crn_data["speciesVariables"]:
        speciesVariables[sv["name"]] = LambdaChoice([Symbol(x) for x in sv["species"]], len(speciesVariables) )

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
            reactant = filter(lambda x: x["id"] == link["target_id"], crn_data["nodes"])[0]

            if reactant["type"] == "or-reactant":

                alternatives = []
                or_reactant_links = filter(lambda x: x["target_id"] == reactant["id"], crn_data["links"])
                for or_link in or_reactant_links:
                    actual_reactant = filter(lambda x: x["id"] == or_link["target_id"], crn_data["nodes"])[0]
                    alternatives.append(getSpeciesObject(actual_reactant["label"], or_link["stoichiometry"], stoichiometries, speciesVariables))

                reactant_objects.append(Or(alternatives))

            else:
                reactant_objects.append(getSpeciesObject(reactant["label"], link["stoichiometry"], stoichiometries, speciesVariables))

        # find products
        product_objects = []
        product_links = filter(lambda x: x["source_id"] == reaction["id"], crn_data["links"])
        for link in product_links:
            product = filter(lambda x: x["id"] == link["source_id"], crn_data["nodes"])[0]
            if product["type"] == "or-product":

                alternatives = []
                or_product_links = filter(lambda x: x["source_id"] == reactant["id"], crn_data["links"])
                for or_link in or_product_links:
                    actual_product = filter(lambda x: x["id"] == or_link["source_id"], crn_data["nodes"])[0]
                    alternatives.append(getSpeciesObject(actual_product["label"], link["stoichiometry"], stoichiometries, speciesVariables))

                product_objects.append(Or(alternatives))

            else:
                product_objects.append(getSpeciesObject(product["label"], link["stoichiometry"], stoichiometries, speciesVariables))


        reaction_rate = Symbol(reaction["label"])

        if "required" in reaction.keys() and reaction["required"]: # TODO - implement
            required_reaction_objects.append(Reaction(reactant_objects, product_objects,reaction_rate))
        else:
            optional_reaction_objects.append(Reaction(reactant_objects, product_objects,reaction_rate))

    species = [Symbol(x["name"]) for x in crn_data["species"]]
    rate_constants = [RateConstant(x["name"], x["min"], x["max"]) for x in crn_data["rates"]]
    return CRNSketch(species, required_reaction_objects, optional_reaction_objects, rate_constants)



def getSpeciesObject(name, stoichiometry, stoichiometries, speciesVariables):

    # Create a Species object from a species name (which may be an actual species or speciesVariable) and stoichiometry
    # (which may be a numerical value, a stoichiometricVariable, or '?')

    name = Symbol(name)

    if stoichiometry in stoichiometries.keys():
        return Species(Choice(name, stoichiometries[name]["min"], stoichiometries[name]["max"]), 1)
        # why second stoichiomery argument?

    elif stoichiometry == '?':
        return Species(Choice(name, 0, 2), 1)

    elif name in speciesVariables.keys():
        return Species(speciesVariables[name], stoichiometry)

    # TODO: handle species and stoichiometry both variables
    # we can't currently handle case where