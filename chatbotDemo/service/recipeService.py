import math

def compute_recipe_sustainability_score(recipe):
    ingredients = recipe.listOfFoods
    alpha = 0.8
    beta = 0.2
    max_overall_sustainability = 0.8689
    cfp_score = compute_normalized_cfp_sustainability(ingredients)
    wfp_score = compute_normalized_wfp_sustainability(ingredients)

    overall_sustainability = alpha * cfp_score + beta * wfp_score
    normalized_overall_sustainability = overall_sustainability / max_overall_sustainability
    recipe.sustainabilityScore = normalized_overall_sustainability

def compute_normalized_cfp_sustainability(ingredients):
    normalized_cfps = []
    max_cfp = 78.8
    for ingredient in ingredients:
        normalized_cfps.append(ingredient.cfp/max_cfp)
    #order cfps in descending order
    normalized_cfps.sort(reverse=True)

    cfp_score = 0
    for i in range(len(normalized_cfps)):
        cfp_score += normalized_cfps[i] * math.e ** (-i)
    
    return cfp_score

def compute_normalized_wfp_sustainability(ingredients):
    normalized_wfps = []
    max_wfp = 731000
    for ingredient in ingredients:
        normalized_wfps.append(ingredient.wfp/max_wfp)
    #order wfps in descending order
    normalized_wfps.sort(reverse=True)

    wfp_score = 0
    for i in range(len(normalized_wfps)):
        wfp_score += normalized_wfps[i] * math.e ** (-i)
    
    return wfp_score