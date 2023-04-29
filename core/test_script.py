from timeit import default_timer as timer
import math, numpy
import re, spacy
from scipy.optimize import minimize_scalar
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.matcher import Matcher
# import en_core_web_sm

import psycopg2
import pytest
import csv

from calculate import runCalculations

# timer
# start_time = timer()

# question = "Given W360x33 6m column braced laterally once at the weak axis midpoint calculate the compressive resistance of the column"
# print(runCalculations(question))

# end_time = timer()
# print("\n", end_time - start_time)

## TEST METHOD 1

# def test_back_calculate(question, expected_answer):
#     assert newfun() == expected_answer

# def test_Cr(expected_Cr):
#     Cr = calculateCR(Lx, Ly, radius_gx, radius_gy, area)
#     print(expected_Cr, Cr)
#     print("?")
#     assert Cr == expected_Cr

# @pytest.mark.parametrize("question, expected_Cr", csv.reader(open("calc_test_cases.csv")))
# def test_with_csv(question, expected_Cr):
#     print(question)
#     print(expected_Cr)
#     test_Cr(expected_Cr)

## TEST METHOD 2

@pytest.fixture
def test_data():
    test_cases = []
    with open('calc_test_cases.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            test_cases.append((row['question'], float(row['expected_answer'])))
    return test_cases

def test_yourcode(test_data, capsys):
    failed_rows = []
    for i, (question, expected_answer) in enumerate(test_data, 1):
        start_time = timer()
        try:
            # Call your code to get the actual_answer
            actual_answer = runCalculations(question)[0]
            # Compare the actual and expected answers
            assert abs(actual_answer - expected_answer) <= 1, f"For '{question}', expected {expected_answer}, but got {actual_answer}"
        except AssertionError:
            # If the test fails, record the failed row
            failed_rows.append((i, question, expected_answer, actual_answer))
        end_time = timer()
        # Print the results for this row
        print(f"Test case {i}:")
        print(f"Question: {question}")
        print(f"Expected answer: {expected_answer}")
        print(f"Actual answer: {actual_answer}")
        print(f"Time elapsed: {end_time - start_time:.6f} seconds\n")
    # Print the list of failed rows after all tests have run
    if failed_rows:
        print("Failed rows:")
        for i, question, expected_answer, actual_answer in failed_rows:
            print(f"Test case {i}:")
            print(f"Question: {question}")
            print(f"Expected answer: {expected_answer}")
            print(f"Actual answer: {actual_answer}\n")