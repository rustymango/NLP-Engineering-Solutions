from timeit import default_timer as timer
import math, numpy
import re, spacy
from scipy.optimize import minimize_scalar
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.matcher import Matcher

import psycopg2

# NLP Tokenization
# given problem
question1 = "Given W360x33 6m column braced laterally once at the weak axis\
 mid-section, calculate the compressive resistance of the column"
question2 = "Given W360x33 6m column braced laterally once at the weak axis\
 mid-section, calculate the compressive resistance of the column"
question3 = "Given a W360x33 column with a length of 7.0 meters braced twice at the\
 y axis at 8.2ft and 5000mm, calculate Cr"
question4 = "Design an unbraced column to withstand a compressive resistance of \
 850kN with W360x33 steel"
question5 = "An W360x33 steel column with a length of 5 meters is braced at both ends\
 . What is the maximum allowable compressive load for this column based on the \
 Johnson buckling theory?"


# timer
start_time = timer()

# create custom pipeline?
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
# applies pipeline to question
doc = nlp(question3)

## custom pattern added to pipeline to determine axis bracing
def posMap(document):
    # hashmap of tokens by POS
    docFinal = {}
    # assume status of bracing as unbraced
    bracing = False

    for token in document:
        str_token = str(token.text)

        # determine braced or unbraced through lemmatization in og loop to save time
        if str(token.lemma_) == "brace" or str(token.lemma_) == "support":
            bracing = True
        # remove unnecessary tokens + add key value pair as "POS: [TOKEN]"
        elif token.pos_ not in docFinal and token.pos_ not in ["SPACE", "X", "PUNCT"]:
            docFinal[str(token.pos_)] = [str_token]
        elif token.pos_ in docFinal:
            docFinal[str(token.pos_)].append(str_token)
    
    return docFinal, bracing

## identifies values and units --> joins and appends to final doc
# question = question3
# nlp_unitExtraction = spacy.blank("en")
# doc = nlp_unitExtraction(question)

# og_ents = [list(doc.ents)]
# filtered = filter_spans(og_ents)
# doc.ents = filtered
def findValues(docFinal):

    og_ents = []
    units = ["inches", "in", "ft", "feet", "millimeters", "mm", "meters", "m",\
        "kN", "N", "lbs", "pounds", "kip"]

    # determine unit + value
    span_ents = []
    pattern = r"(\d+\.?\d*)(\s*)(?:("+'|'.join(units)+r"))"

    # works as intended, finds matches
    for match in re.finditer(pattern, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        if span is not None:
            span_ents.append((span.start, span.end, span.text))

    # applies POS label to units
    for ent in span_ents:
        start, end, name = ent
        per_ent = Span(doc, start, end, label="UNITS")
        og_ents.append(per_ent)

    # appends units to hashmaps
    docFinal["UNITS"] = []

    for ent in og_ents:
        docFinal["UNITS"].append(str(ent.text))
    
    print(docFinal)
    
    return docFinal

## assign convert units + assign values to design variables
# converts values to SI --> find max value = length of member
def convertUnits(docFinal):
    number_index = 0
    element_lengths = []
    Cr = 0

    for value in docFinal["UNITS"]:
        unit_value = float((re.findall(r"[-+]?(?:\d*\.*\d+)", value))[0])

        if "in" in value or "inches" in value:
            docFinal["UNITS"][number_index] = unit_value*0.0254
            element_lengths.append(docFinal["UNITS"][number_index])
        elif "ft" in value or "feet" in value:
            docFinal["UNITS"][number_index] = unit_value*0.3048
            element_lengths.append(docFinal["UNITS"][number_index])
        elif "mm" in value or "millimeter" in value:
            docFinal["UNITS"][number_index] = unit_value*0.001
            element_lengths.append(docFinal["UNITS"][number_index])
        elif "m" in value or "meters" in value:
            docFinal["UNITS"][number_index] = unit_value
            element_lengths.append(docFinal["UNITS"][number_index])
        elif "lbs" in value or "pounds" in value:
            docFinal["UNITS"][number_index] = unit_value*4.45
            Cr = unit_value*4.45
        elif "kN" in value:
            docFinal["UNITS"][number_index] = unit_value*1000
            Cr = unit_value*1000
        elif "N" in value:
            docFinal["UNITS"][number_index] = unit_value
            Cr = unit_value

        number_index = number_index + 1

    if len(element_lengths) > 0:
        element_length = max(element_lengths)
    else:
        element_length = 0

    return docFinal, element_length, Cr, element_lengths

def processTokens(document):
    # tokens document/question and returns: hashmap of tokens by POS (0)\
    # and bracing boolean (1)
    docHash = posMap(document)
    findValues(docHash[0])
    return convertUnits(docHash[0]), docHash[1]

results = processTokens(doc)
docFinal = results[0][0]
element_length = results[0][1]
Cr = results[0][2]
print(Cr)
# bracing status is boolean = True if determined in POS tagging
bracing_status = results[1]
# potential braced lengths
element_lengths = results[0][3]


## identify bracing mechanisms and at what points
# assumed unbraced
Lx = element_length
Ly = element_length

# lateral bracing orientations
axis = ["weak", "strong", "y", "x"]
# checks for mentions of specific axis being braced, adds to spacy pipeline
matchPatterns = [{"LOWER": {"IN": axis}}, {"LOWER": "axis"}]
matcher.add("axisBracing", [matchPatterns])

def braceLocations(element_lengths):
    # determines bracing 

    # check bracing axis
    matches = matcher(doc)
    for match_id, start, end in matches:
        # string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]     
        braced_axis = span.text

    # bracing = True if braced, determined during hashmap creation
    if bracing_status and ("y" in braced_axis or "weak" in braced_axis):
        length = min(element_lengths)
        tag = "y"
    elif bracing_status:
        length = min(element_lengths)
        tag = "x"
    
    return length, tag

# only run bracing determination if bracing detected in question
if bracing_status:
    # print(bracing_status)
    bracing_info = braceLocations(element_lengths)

    if bracing_info[1] == "y":
        Ly = bracing_info[0]
    else:
        Lx = bracing_info[0]

## determine material and properties
material = max(docFinal["PROPN"], key=len)

## properties updated in SQL query (note: all properties in mm)
# query postgreSQL
def getMaterials(material):
    conn = None
    try:
        conn = psycopg2.connect(
            host = "localhost",
            port = 5433,
            database = "material_properties",
            user = "postgres",
            password = "facetrol1"
        )

        cur = conn.cursor()
        postgreSQL_query = "SELECT * FROM materials where material_shape = %s"
        cur.execute(postgreSQL_query, (material,))

        material_properties = cur.fetchall()

        radius_gx = float(material_properties[0][0])
        radius_gy = float(material_properties[0][1])
        area = float(material_properties[0][2])
    
    except:
        radius_gx = 0
        radius_gy = 0
        area = 0

    finally:
        if conn is not None:
            conn.close()
    
    return radius_gx, radius_gy, area

radius_gx, radius_gy, area = getMaterials(material)

# print(radius_gx, radius_gy, area)
# print(Lx,Ly, element_length, bracing_status)
# print(Cr)

##### MOVE TO CALCULATE TAB ONCE CODE IS ORGANIZED

## IDENTIFY WHAT NEEDS TO BE CALCULATED
# consider rule based NER (regex, spacy EntityRuler, "introduction to names entity\
#->recognition", machine learning CRF/BERT)

compressionR_vars = [element_length, Lx, Ly, radius_gx, radius_gy, area, Cr]
# flexuralR_vars = []
# var_status = {"DETERMINED": [], "MISSING": []}
var_status = []

# determines calculation target and/or if there are missing inputs
def checkMissing():
    for variable in compressionR_vars:
        if variable == None:
            var_status.append(variable)  
        # else:
        #     var_status["DETERMINED"].append(variable)

# determine calculation target
if Cr == 0:
    calculation_target = "Cr"
elif len(var_status) > 1:
    checkMissing()
    print(var_status)
    calculation_target = "test"
else:
    checkMissing()
    calculation_target = "test"

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
    
    ratio_Kx = Kx*Lx*1000/radius_gx
    ratio_Ky = Ky*Ly*1000/radius_gy

    if ratio_Kx > ratio_Ky:
        lambda_K = ratio_Kx*math.sqrt(yield_mpa/(modulusE*math.pi**2))
    else:
        lambda_K = ratio_Ky*math.sqrt(yield_mpa/(modulusE*math.pi**2))

    # show intermediate steps to calculate

    # answer
    compressiveR = phi*area*yield_mpa*(1 + lambda_K**(2*stress_factor))**(-1/stress_factor)

    return (str(compressiveR/1000) + "kN"), ratio_Kx, ratio_Ky, lambda_K

## back calculates column design if Cr given, start with lambda
# assume unbraced first, target lambda established for back calculation
def lambda_0(Ly, targetLambda):
    # lambda in terms of variables wanting to solve for: Ky, Ly
    radius_g = min(radius_gx, radius_gy)
    lambda_K = Ky*Ly/radius_g*math.sqrt(yield_mpa/(modulusE*math.pi**2))

    # lambda_K(Ly) = 0, use for solving 
    return abs(lambda_K - targetLambda)

# base case
if calculation_target == "Cr":
    Cr, ratio_Kx, ratio_Ky, lambda_K = calculateCR(Lx, Ly, radius_gx, radius_gy, area)
# back calculate
elif calculation_target != "Cr":
    targetLambda = ((Cr/(phi*area*yield_mpa))**(-stress_factor) - 1)**(1/(2*stress_factor))

    res = minimize_scalar(lambda_0, args=(targetLambda))
    print(res.x)


end_time = timer()
print(end_time - start_time)

##### IGNORE

### NOTES
## alternative unit finding method
# pattern = re.findall(r"((\d+))(\s*)(?:("+'|'.join(units)+r"))", question)
# print(pattern)

# unitList = []
# unitValues = ["".join(unit[1:]) for unit in pattern]
# print(unitValues)