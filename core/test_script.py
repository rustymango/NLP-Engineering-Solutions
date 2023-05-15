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

# question = "Given W360x33 6m column braced laterally once at the weak axis midpoint calculate the compressive resistance of the column"
# print(runCalculations(question))


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
    passed_tests = 0
    total_tests = 0

    for i, (question, expected_answer) in enumerate(test_data, 1):
        start_time = timer()
        try:
            # Call your code to get the actual_answer
            actual_answer = runCalculations(question)[0]
            # Compare the actual and expected answers
            answer_variance = abs(actual_answer - expected_answer)
            assert answer_variance <= 5, f"For '{question}', expected {expected_answer}, but got {actual_answer}"
        except AssertionError:
            # If the test fails, record the failed row
            failed_rows.append((i, question, expected_answer, actual_answer))
        end_time = timer()
        # Print the results for this row
        print(f"Test case {i}:")
        print(f"Question: {question}")
        print(f"Expected answer: {expected_answer}")
        print(f"Actual answer: {actual_answer}")
        print(f"Time elapsed: {end_time - start_time:.6f} seconds")

        if answer_variance <= 5:
            print("Passed!\n")
            passed_tests = passed_tests + 1
        else:
            print("Failed.\n")

        total_tests = total_tests + 1
    # Print the list of failed rows after all tests have run
    if failed_rows:
        print("Failed rows:")
        for i, question, expected_answer, actual_answer in failed_rows:
            print(f"Test case {i}:")
            print(f"Question: {question}")
            print(f"Expected answer: {expected_answer}")
            print(f"Actual answer: {actual_answer}\n")
    
    print(f"{passed_tests} / {total_tests} tests passed!")