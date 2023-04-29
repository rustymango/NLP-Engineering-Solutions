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
# question1 = "Given W360x33 6m column braced laterally once at the weak axis\
#  midpoint, calculate the compressive resistance of the column"
# question2 = "Given W360x33 6m column braced laterally once at the weak axis\
#  at 1/3 points, calculate the compressive resistance of the column"
# question3 = "Given a W360x33 column with a length of 7.0 meters braced twice at the\
#  y axis at 8.2ft and 5000mm, calculate Cr"
# question4 = "Design an unbraced column to withstand a compressive resistance of \
#  850kN with W360x33 steel"
# question5 = "An W360x33 steel column with a length of 5 meters is braced at both ends\
#  . What is the maximum allowable compressive load for this column based on the \
#  Johnson buckling theory?"
# question6 = "A W360x33 steel column with a length of 18 feet is unbraced about the\
#  weak axis except for a brace located at a point 5 feet from one end. What\
#  is the maximum allowable compressive load for this column based on the Johnson buckling theory?"

# create custom pipeline?
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# applies pipeline to question
def nlp_doc(question):
    doc = nlp(question)
    return doc

## creates hashmap of tokens by part of speech (POS)
def posMap(document):
    docFinal = {}
    # assume status of bracing as unbraced
    bracing = False

    for token in document:
        str_token = str(token.text)

        # determine braced or unbraced column through lemmatization of "brace" variations
        if str(token.lemma_) == "brace" or str(token.lemma_) == "support":
            bracing = True
        # remove unnecessary tokens + add key value pair as "POS: [TOKEN]"
        elif token.pos_ not in docFinal and token.pos_ not in ["SPACE", "X", "PUNCT"]:
            docFinal[str(token.pos_)] = [str_token]
        # if key already exists, append to list
        elif token.pos_ in docFinal:
            docFinal[str(token.pos_)].append(str_token)
    
    return docFinal, bracing

## identifies values and units --> joins and appends to final doc
def findValues(docFinal, doc):

    og_ents = []
    units = ["inches", "in", "ft", "feet", "millimeters", "mm", "meters", "m",\
        "kN", "N", "lbs", "pounds", "kips"]

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
        column_length = max(element_lengths)
    else:
        column_length = 0
    
    element_lengths = sorted(element_lengths)

    return docFinal, column_length, Cr, element_lengths

def processTokens(document):
    # tokenizes document/question and returns: hashmap of tokens by POS (0)\
    # and bracing boolean (1)
    docHash = posMap(document)
    # finds numbers, associates with respective units
    findValues(docHash[0], document)

    docFinal, column_length, Cr, element_lengths = convertUnits(docHash[0])
    bracing_status = docHash[1]

    # assumed braced at endpoints of column due to standard structural eng. conditions
    Lx = column_length
    Ly = column_length

    return docFinal, column_length, Cr, element_lengths, bracing_status, Lx, Ly

# bracing status is boolean = True if determined in POS tagging
# unbraced_lengths = potential unbraced lengths
# docFinal, column_length, Cr, element_lengths, bracing_status, Lx, Ly = processTokens(doc)

## identify bracing axis, mechanisms, and at what points
def braceLocations(element_lengths, Lx, Ly, doc):
    # lateral bracing orientations
    axis = ["weak", "strong", "y", "x"]
    # checks for mentions of specific axis being braced, adds to spacy pipeline
    matchPatterns = [{"LOWER": {"IN": axis}}, {"LOWER": "axis"}]
    matcher.add("axisBracing", [matchPatterns])

    # check bracing axis
    matches = matcher(doc)
    for match_id, start, end in matches:
        # string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]     
        braced_axis = span.text

    # for unspecified axis of bracing, can always assume weak axis braced
    if "braced_axis" not in locals():
        braced_axis = "y axis"

    # bracing = True if braced, determined during hashmap creation
    if ("y" in braced_axis or "weak" in braced_axis):
        # CHANGEEEEEEEEEE
        Ly_1 = min(element_lengths)
        Ly_2 = max(element_lengths) - element_lengths[len(element_lengths)-2]
        Ly = max(Ly_1, Ly_2)
        tag = "y"
    else:
        Lx_1 = min(element_lengths)
        Lx_2 = max(element_lengths) - element_lengths[len(element_lengths)-1]
        Lx = max(Lx_1, Lx_2)
        tag = "x"

    ## check for proportion or text bracing description (ie @ midpoint, 1/3, etc)
    bracing_coefficient = 1
    # proportion-based bracing intervals
    brace_points = ["1/2", "1/3", "1/4"]
    # determine non-numerical bracing description
    # only if a numerical bracing description not detected
    if max(element_lengths) == Lx and max(element_lengths) == Ly:
        for token in doc:
            str_token = token.text
            if str_token.lower().startswith("mid") or str_token in brace_points:
                bracing_coefficient = 1/2
                similarity = token.similarity(nlp(brace_points[0]))
                if similarity >= 0.3:
                    try:
                        numerator, denominator = map(float, str_token.split('/'))
                        bracing_coefficient = numerator / denominator
                    except ValueError:
                        # if the token cannot be converted, skip
                        continue
    
    # MODIFY LX OR LY BASED ON TAG/BRACING DESCRIPTION
    if tag == "y":
        Ly = Ly*bracing_coefficient
    elif tag == "x":
        Lx = Lx*bracing_coefficient

    return Lx, Ly

# # only run bracing determination if bracing detected in question
# if bracing_status:
#     Lx, Ly = braceLocations(element_lengths, Lx, Ly)

## determine material and properties
## properties updated in SQL query (note: all properties in mm)
# query postgreSQL

def getMaterials(docFinal):
    material = max(docFinal["PROPN"], key=len)
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