from timeit import default_timer as timer

import math
import spacy
from scipy.optimize import minimize_scalar
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.matcher import Matcher

from nlp_model import nlp_doc, processTokens, braceLocations, getMaterials

# timer
# start_time = timer()

# nlp pipeline
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

### CALCULATIONS

# flexuralR_vars = []
# var_status = {"DETERMINED": [], "MISSING": []}

# determines calculation target and/or if there are missing inputs
def checkMissing(column_length, Lx, Ly, radius_gx, radius_gy, area, Cr):
    compressionR_vars = [column_length, Lx, Ly, radius_gx, radius_gy, area, Cr]
    var_status = []

    for variable in compressionR_vars:
        if variable == None:
            var_status.append(variable)  
        # else:
        #     var_status["DETERMINED"].append(variable)
    
    return var_status

# static inputs
modulusE = 200000
yield_mpa = 300
phi = 0.9
Kx = 1
Ky = 1

steel_class = "class C"
stress_factor = 1.34
if steel_class == "class H":
    stress_factor = 2.24

## standard case, calculates compressive resistance
def calculateCR(Lx, Ly, radius_gx, radius_gy, area):
    
    ratio_Kx = round(Kx*Lx*1000/radius_gx, 2)
    ratio_Ky = round(Ky*Ly*1000/radius_gy, 2)

    if ratio_Kx > ratio_Ky:
        lambda_K = ratio_Kx*math.sqrt(yield_mpa/(modulusE*math.pi**2))
    else:
        lambda_K = ratio_Ky*math.sqrt(yield_mpa/(modulusE*math.pi**2))
    
    lambda_K = round(lambda_K, 3)

    # show intermediate steps to calculate

    # answer
    compressiveR = phi*area*yield_mpa*(1 + lambda_K**(2*stress_factor))**(-1/stress_factor)
    compressiveR = round(compressiveR/1000, 1)

    return compressiveR, ratio_Kx, ratio_Ky, lambda_K

## back calculates column design if Cr given, start with lambda
# assume unbraced first, target lambda established for back calculation
def lambda_0(Ly, radius_gx, radius_gy, targetLambda):
    # lambda in terms of variables wanting to solve for: Ky, Ly
    radius_g = min(radius_gx, radius_gy)
    lambda_K = Ky*Ly/radius_g*math.sqrt(yield_mpa/(modulusE*math.pi**2))

    # lambda_K(Ly) = 0, use for solving 
    return abs(lambda_K - targetLambda)

def runCalculations(question):
    # process string input into tokenized document
    question = question.replace(".", " ").replace(",", " ")
    doc = nlp_doc(question)

    # bracing status is boolean = True if determined in POS tagging
    # unbraced_lengths = potential unbraced lengths
    docFinal, column_length, Cr, element_lengths, bracing_status, Lx, Ly = processTokens(doc)

    # only run bracing determination if bracing detected in question
    if bracing_status:
        # print(bracing_status)
        Lx, Ly = braceLocations(element_lengths, Lx, Ly, doc)
    
    # grab material properties
    radius_gx, radius_gy, area = getMaterials(docFinal)

    missing_vars = checkMissing(column_length, Lx, Ly, radius_gx, radius_gy, area, Cr)

    # determine calculation target
    if Cr == 0:
        calculation_target = "Cr"
    elif len(missing_vars) > 1:
        checkMissing(column_length, Lx, Ly, radius_gx, radius_gy, area, Cr)
        calculation_target = "test"
    else:
        checkMissing(column_length, Lx, Ly, radius_gx, radius_gy, area, Cr)
        calculation_target = "test"

    modulusE = 200000
    yield_mpa = 300
    phi = 0.9
    Kx = 1
    Ky = 1

    steel_class = "class C"
    stress_factor = 1.34

    # base case
    if calculation_target == "Cr":
        result, ratio_Kx, ratio_Ky, lambda_K = calculateCR(Lx, Ly, radius_gx, radius_gy, area)
        return result, calculation_target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr
    # back calculate
    elif calculation_target != "Cr":
        ratio_Kx, ratio_Ky, lambda_K, Lx, Ly = 0, 0, 0, 0, 0
        targetLambda = ((Cr/(phi*area*yield_mpa))**(-stress_factor) - 1)**(1/(2*stress_factor))
        targetLambda = round(targetLambda, 3)

        result = minimize_scalar(lambda_0, args=(radius_gx, radius_gy, targetLambda))

        return round(result.x, 2), calculation_target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr
        
# end_time = timer()
# print("\n", end_time - start_time)