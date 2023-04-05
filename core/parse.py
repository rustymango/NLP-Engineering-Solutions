from timeit import default_timer as timer
import math
import re
import spacy
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.matcher import Matcher

# NLP Tokenization
# given problem
question1 = "Given W360x33 6m column braced laterally once at the weak axis\
    mid-section, calculate the compressive resistance of the column"
question2 = "Given W360x33 6m column braced laterally once at the weak axis\
    mid-section, calculate the compressive resistance of the column"
question3 = "Given a W360x33 column with a length of 6 meters braced twice at the weak\
    axis at 8.2 feet and 2.5m, calculate Cr"
question4 = "Design an unbraced column to withstand a compressive resistance of \
    850kN"

# create custom pipeline?
nlp = spacy.load("en_core_web_sm")
unitEntity = nlp.add_pipe("entity_ruler", after="ner")

# patterns = [
#                 # determine what needs to be calculated
#                 {
#                     "label": "UNITS", "pattern": [
#                         {"TEXT": {"REGEX": "((\d+))"}},
#                         {"TEXT": {"REGEX": "(?=("+'|'.join(units)+r"))"}}
#                         ]
#                 }
# ]
# unitEntity.add_patterns(patterns)

### check for key words
### identify key verbs and associated numbers --> custom pipeline with\
#-->POS, matcher/entity ruler --> hashmap
doc = nlp(question3)
docFinal = {}

for token in doc:
    str_token = str(token.text)

    # remove unnecessary tokens + add key value pair as "POS: [TOKEN]"
    if token.pos_ not in docFinal and token.pos_ not in ["SPACE", "X", "PUNCT"]:
        docFinal[str(token.pos_)] = [str_token]
    elif token.pos_ in docFinal:
        docFinal[str(token.pos_)].append(token)

question = question3
nlp_unitExtraction = spacy.blank("en")
doc = nlp_unitExtraction(question)

# tokenized_Doc = [token for token in doc]
# print(tokenized_Doc)

## IDENTIFY WHAT NEEDS TO BE CALCULATED
## rule based NER (regex, spacy EntityRuler, "introduction to names entity\
#->recognition", machine learning CRF/BERT)

og_ents = list(doc.ents)
units = ["inches", "in", "ft", "feet", "millimeters", "mm", "meters", "m",\
    "kN", "lbs", "pounds", "kip"]

# determine unit + value
start_time = timer()
span_ents = []
pattern = r"(\d+\.?\d*)(\s*)(?:("+'|'.join(units)+r"))"

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

    # print(ent.text, ent.label_)

print(docFinal)

end_time = timer()
print(end_time - start_time)

# element pattern
elements = ["beam", "column", "member"]

# lateral bracing pattern
axis = ["weak", "strong", "x", "y"]

lengths = {}

# material

# braced or unbraced, how many times, and at what locations, on what axis

# length of column

# link to material properties, if missing, specify in output

# material properties
# material = []
# modulusE = 200000
# yield_mpa = 300
# radius_gx = 0
# radius_gy = 0
# phi = 0.9
# area = 0
# steel_class = ""

# element_length = 0
# unbraced_Lx = 0
# unbraced_Ly = 0

### NOTES
## alternative unit finding method
# pattern = re.findall(r"((\d+))(\s*)(?:("+'|'.join(units)+r"))", question)
# print(pattern)

# unitList = []
# unitValues = ["".join(unit[1:]) for unit in pattern]
# print(unitValues)

# time_end = timer()
# print(time_end - time_start)