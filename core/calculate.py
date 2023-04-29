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

## process string input into tokenized document
# question = "Given W360x33 6m column braced laterally once at the weak axis midpoint calculate the compressive resistance of the column"

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
        print(missing_vars)
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
        Cr, ratio_Kx, ratio_Ky, lambda_K = calculateCR(Lx, Ly, radius_gx, radius_gy, area)
        return Cr
    # back calculate
    elif calculation_target != "Cr":
        targetLambda = ((Cr/(phi*area*yield_mpa))**(-stress_factor) - 1)**(1/(2*stress_factor))
        targetLambda = round(targetLambda, 3)

        res = minimize_scalar(lambda_0, args=(radius_gx, radius_gy, targetLambda))

        return res.x

### OUTPUTS

## show intermediate calculation steps
def showSteps(target, Cr, ratio_Kx, ratio_Ky, lambda_K):
    if target == "Cr":
        kRatio_formula = "Kx*Lx/rx and Ky*Ly/ry < 200 \n"
        kxRatio_num = "Kx Ratio: " + str(Kx)+"*"+str(Lx*1000)+"mm/"+str(radius_gx)+"mm = "+str(ratio_Kx)
        kyRatio_num = "Ky Ratio: " + str(Ky)+"*"+str(Ly*1000)+"mm/"+str(radius_gy)+"mm = "+str(ratio_Ky)

        lambdaK_formula = "lambda = KL/r*sqrt(Fy/(E*pi^2))"
        lambdaK_num = str(max(ratio_Kx, ratio_Ky))+"*"\
            +"sqrt("+str(yield_mpa)+"/"+"("+str(modulusE)+"pi^2)) = "+str(lambda_K)
        
        Cr_formula = "Cr = phi*Fy*A*(1 + lambda^(2*1.34))^(-1/1.34)"
        Cr_num = str(phi)+"*"+str(yield_mpa)+"MPa*"+str(area)+"mm^2*(1 + "+str(lambda_K)+"^2.68)^(-1/1.34) = "+str(Cr)+" kN"
        
        return kRatio_formula, kxRatio_num, kyRatio_num, lambdaK_formula, lambdaK_num, Cr_formula, Cr_num      
    else:
        lambda_formula = "lambda = ([Cr/(phi*Fy*A)]^(-1.34) - 1)^(1/2.68)"
        lambda_num = "(["+str(Cr)+str(phi)+"*"+str(area)+"*"+str(yield_mpa)+"]^(-1.34) - 1)^(1/2.68) = "+str(targetLambda)

        kRatio_formula = "L = [lambda/sqrt(Fy/(E*pi^2))]*r/K"
        kRatio_num = "Maximum unbraced length (Ly) = "+str(round(res.x, 2))+" mm"

        return lambda_formula, lambda_num, kRatio_formula, kRatio_num

## printing outputs
def printCalculation():
    # base case
    if calculation_target == "Cr":
        kRatio_formula, kxRatio_num, kyRatio_num, lambdaK_formula, lambdaK_num, Cr_formula, Cr_num = \
        showSteps(calculation_target, Cr, ratio_Kx, ratio_Ky, lambda_K)

        print("\n", kRatio_formula, "\n", kxRatio_num, "\n", kyRatio_num, "\n\n", lambdaK_formula, "\n", lambdaK_num, "\n\n", Cr_formula, "\n", Cr_num)
    # back calculate
    elif calculation_target != "Cr":
        lambda_formula, lambda_num, kRatio_formula, kRatio_num = showSteps(calculation_target, Cr, None, None, None)
        print("\n", lambda_formula, "\n", lambda_num, "\n\n", kRatio_formula, "\n", kRatio_num)

# end_time = timer()
# print("\n", end_time - start_time)