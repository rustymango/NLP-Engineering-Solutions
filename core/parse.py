from timeit import default_timer as timer
import math
import re
import spacy
from spacy.pipeline import EntityRuler
from spacy.tokens import Span

# NLP Tokenization
# given problem
question1 = "Given W360x33 6m column braced laterally once at the weak axis\
    mid-section, calculate the compressive resistance of the column"
question2 = "Given W360x33 6m column braced laterally once at the weak axis\
    mid-section, calculate the compressive resistance of the column"
question3 = "Given a W360x33 column with a length of 6 inch braced twice at the weak\
    axis at 2000 feet and 2m, calculate Cr"
question4 = "Design an unbraced column to withstand a compressive resistance of \
    850kN"

# tokenize problem + POS tag + remove unneccessary tokens
nlp = spacy.load("en_core_web_sm")
unitEntity = nlp.add_pipe("entity_ruler", after="ner")

# tokenized_qDoc = [token for token in qDoc]
# print(tokenized_qDoc)

### check for key words
### identify key verbs and associated numbers --> custom pipeline with\
#-->POS, matcher/entity ruler --> hashmap

question = question3
nlp = spacy.blank("en")
doc = nlp(question)

## IDENTIFY WHAT NEEDS TO BE CALCULATED
## rule based NER (regex, spacy EntityRuler, "introduction to names entity\
#->recognition", machine learning CRF/BERT)

og_ents = list(doc.ents)
units = ["inches", "in", "ft", "feet", "millimeters", "mm", "meters", "m",\
    "kN", "lbs", "pounds", "kip"]

# unit pattern
start_time = timer()
span_ents = []
pattern = r"(\d+)(\s*)(?:("+'|'.join(units)+r"))"

for match in re.finditer(pattern, doc.text):
    start, end = match.span()
    span = doc.char_span(start, end)
    if span is not None:
        span_ents.append((span.start, span.end, span.text))

print(span_ents)

## !!!!! SLOWER
# pattern = re.findall(r"((\d+))(\s*)(?:("+'|'.join(units)+r"))", question)
# print(pattern)

# unitList = []
# unitValues = ["".join(unit[1:]) for unit in pattern]
# print(unitValues)

# time_end = timer()
# print(time_end - time_start)
## !!!!! SLOWER

end_time = timer()
print(end_time - start_time)

# patterns = [
#                 {
#                     "label": "UNITS", "pattern": [
#                         {"TEXT": {"REGEX": "((\d+))"}},
#                         {"TEXT": {"REGEX": "(?=("+'|'.join(units)+r"))"}}
#                         ]
#                 }
# ]
# unitEntity.add_patterns(patterns)

# qDoc = nlp(question1)
# for ent in qDoc.ents:
#     print (ent.text, ent.label_)

# element pattern
elements = ["beam", "column", "member"]

# lateral bracing pattern
axis = ["weak", "strong", "x", "y"]

lengths = {}

# logic for attaching tokens to required variables, try relation extraction?
# use entity ruler/regex for getting values 

# for token in qDoc:
#     str_token = str(token.text)

#     if token.pos_ == "NUM":
#         lengths[float(token)] = ""
#     elif str_token in units:
#         lengths.append(str_token)

#     # remove unnecessary tokens
#     elif token.pos_ not in tokenPOS and token.pos_ not in ["SPACE", "X", "PUNCT"]:
#         tokenPOS[str(token.pos_)] = [str_token]
#     elif token.pos_ not in ["SPACE", "X", "PUNCT"]:
#         tokenPOS[str(token.pos_)].append(str_token)

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