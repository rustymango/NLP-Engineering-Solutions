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
    y axis at 8.2 feet and 5000mm, calculate Cr"
question4 = "Design an unbraced column to withstand a compressive resistance of \
    850kN"

# timer
start_time = timer()

# create custom pipeline?
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
# eRuler = nlp.add_pipe("entity_ruler", before="ner")

## custom pattern to determine axis bracing
# lateral bracing orientations
axis = ["weak", "strong", "y", "x"]

matchPatterns = [{"LOWER": {"IN": axis}}, {"LOWER": "axis"}]
matcher.add("axisBracing", [matchPatterns])

### check for key words
### identify key verbs and associated numbers --> custom pipeline with\
###-->POS, matcher/entity ruler --> hashmap

# hashmap of tokens by POS
doc = nlp(question3)
docFinal = {}
# assume status of bracing as unbraced
bracing = False

for token in doc:
    str_token = str(token.text)

    # determine braced or unbraced through lemmatization in og loop to save time
    if str(token.lemma_) == "brace" or str(token.lemma_) == "support":
        bracing = True
    # remove unnecessary tokens + add key value pair as "POS: [TOKEN]"
    elif token.pos_ not in docFinal and token.pos_ not in ["SPACE", "X", "PUNCT"]:
        docFinal[str(token.pos_)] = [str_token]
    elif token.pos_ in docFinal:
        docFinal[str(token.pos_)].append(str_token)

# check bracing axis
matches = matcher(doc)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]
    span = doc[start:end]
    
    braced_axis = span.text

print(docFinal)

## identifies values and units --> joins and appends to final doc
# loads blank spacy pipeline, need to integrate into main but main overlaps
question = question3
nlp_unitExtraction = spacy.blank("en")
doc = nlp_unitExtraction(question)

og_ents = list(doc.ents)
# filtered = filter_spans(og_ents)
# doc.ents = filtered
units = ["inches", "in", "ft", "feet", "millimeters", "mm", "meters", "m",\
    "kN", "lbs", "pounds", "kip"]

# determine unit + value
span_ents = []
pattern = r"(\d+\.?\d*)(\s*)(?:("+'|'.join(units)+r"))"

# works as intended, finds matches
for match in re.finditer(pattern, doc.text):
    start, end = match.span()
    span = doc.char_span(start, end)
    if span is not None:
        span_ents.append((span.start, span.end, span.text))

# print (span_ents)
# applies POS label to units
for ent in span_ents:
    start, end, name = ent
    per_ent = Span(doc, start, end, label="UNITS")
    og_ents.append(per_ent)

# appends units to hashmaps
docFinal["UNITS"] = []

for ent in og_ents:
    docFinal["UNITS"].append(str(ent.text))

    # print(ent.text, ent.label_)

print(docFinal)

##### !!!!!!!!!!!!!!!!!!!!!!!!!!!

## assign convert units + assign values to design variables
# converts values to SI --> find max value = length of member
# !!! try to use number from "UNITS" than "NUM"
number_index = 0

for value in docFinal["UNITS"]:
    docFinal["NUM"][number_index] = float(docFinal["NUM"][number_index])

    if "in" in value or "inches" in value:
        docFinal["NUM"][number_index] = docFinal["NUM"][number_index]*0.0254
    elif "ft" in value or "feet" in value:
        docFinal["NUM"][number_index] = docFinal["NUM"][number_index]*0.3048
    elif "mm" in value or "millimeter" in value:
        docFinal["NUM"][number_index] = docFinal["NUM"][number_index]*0.001
    # bad practice, overlaps with millimeter + element length could be in diff unit
    # elif "m" in value or "meter" in value:
    #     element_length = docFinal["NUM"][number_index]

    number_index = number_index + 1

element_length = max(docFinal["NUM"])

print(docFinal)

## identify bracing mechanisms and at what points
# assumed unbraced
Lx = element_length
Ly = element_length

# determines bracing 
# only incorporates elements 
brace_locations = [brace for brace in docFinal["NUM"] if brace < element_length]

# bracing = True if braced, determined during hashmap creation
if bracing and ("y" in braced_axis or "weak" in braced_axis):
    Ly = brace_locations[0]
elif bracing:
    Lx = brace_locations[0]

## determine material and properties
material = docFinal["PROPN"][0]

## properties updated in SQL query (note: all properties in mm)
# query postgreSQL
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
Cr = 566016

# print(radius_gx, radius_gy, area)

##### MOVE TO CALCULATE TAB ONCE CODE IS ORGANIZED

## IDENTIFY WHAT NEEDS TO BE CALCULATED
# consider rule based NER (regex, spacy EntityRuler, "introduction to names entity\
#->recognition", machine learning CRF/BERT)

compressionR_vars = [element_length, Lx, Ly, radius_gx, radius_gy, area, Cr]
# flexuralR_vars = []
var_status = {"DETERMINED": [], "MISSING": []}

def checkMissing():
    for variable in compressionR_vars:
        if variable == None:
            var_status["MISSING"].append(variable)  
        # else:
        #     var_status["DETERMINED"].append(variable)

# determine calculation target
if Cr == None:
    calculation_target = "Cr"
elif len(var_status["MISSING"]) > 1:
    checkMissing()
    print(var_status["MISSING"])
else:
    checkMissing()

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

    return str(compressiveR/1000) + "kN"
    
print(calculateCR(Lx, Ly, radius_gx, radius_gy, area))

## back calculates column design if Cr given, start with lambda
# assume unbraced first, target lambda established for back calculation
targetLambda = ((Cr/(phi*area*yield_mpa))**(-stress_factor) - 1)**(1/(2*stress_factor))

def lambda_0(Ly, targetLambda):
    # lambda in terms of variables wanting to solve for: Ky, Ly
    lambda_K = Ky*Ly/radius_gy*math.sqrt(yield_mpa/(modulusE*math.pi**2))

    # lambda_K(Ly) = 0, use for solving 
    return abs(lambda_K - targetLambda)

# back calculate
res = minimize_scalar(lambda_0, args=(targetLambda))
print(res.x)

end_time = timer()
print(end_time - start_time)

## perform calculation

##### IGNORE

### NOTES
## alternative unit finding method
# pattern = re.findall(r"((\d+))(\s*)(?:("+'|'.join(units)+r"))", question)
# print(pattern)

# unitList = []
# unitValues = ["".join(unit[1:]) for unit in pattern]
# print(unitValues)