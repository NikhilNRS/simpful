import unittest
import sys
from pathlib import Path
import unittest
import re

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

import unittest
import gp_utilities

features = []

class TestLogicalOperatorMutation(unittest.TestCase):
    def test_find_no_operators(self):
        sentence = "if (gdp_growth IS High) then (Outcome IS Positive)"  # Lowercase logical words
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 0, "No operators should be found in lowercase.")
        self.assertEqual(results, {}, "Results dictionary should be empty when operators are in lowercase.")

    def test_find_single_operator(self):
        sentence = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) THEN (Outcome IS Negative)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertIn('AND', results, "AND should be found in uppercase.")
        self.assertEqual(results['AND']['count'], 1, "One AND should be found.")
        self.assertEqual(results['AND']['indices'], [sentence.find('AND')], "Index of AND should be correctly identified.")

    def test_find_multiple_operators(self):
        sentence = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) OR (inflation_rate IS Low) AND (NOT (market_trend IS Positive))"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 3, "Three different operators should be found, all in uppercase.")
        expected_operators = {'AND': 2, 'OR': 1, 'NOT': 1}
        for op, expected_count in expected_operators.items():
            self.assertIn(op, results, f"{op} should be correctly identified.")
            self.assertEqual(results[op]['count'], expected_count, f"{op} should occur {expected_count} times.")
            self.assertIsInstance(results[op]['indices'], list, "Indices should be listed.")

    def test_detailed_operator_indices(self):
        sentence = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) OR (inflation_rate IS Low) OR (market_trend IS Negative)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(results['OR']['count'], 3, "Three ORs should be found.")
        self.assertEqual(len(results['OR']['indices']), 3, "There should be three indices for OR.")
        # Dynamically find each 'OR' index
        indices = []
        start = 0
        while start < len(sentence):
            idx = sentence.find('OR', start)
            if idx == -1:
                break
            indices.append(idx)
            start = idx + 1  # Update start position to beyond the last found 'OR'
        self.assertEqual(results['OR']['indices'], indices, "Indices of OR should match expected positions.")

    
    def test_case_sensitivity(self):
        sentence = "if (gdp_growth IS High) then (Outcome IS Positive)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 0, "No operators should be found in lowercase.")
        self.assertEqual(results, {}, "Results dictionary should be empty when operators are in lowercase.")


    def test_no_operator_present(self):
        sentence = "IF (gdp_growth IS High) THEN (Outcome IS Positive)"
        mutated = gp_utilities.mutate_logical_operator(sentence, features, verbose=True)
        self.assertEqual(sentence, mutated, "Sentence should remain unchanged when no logical operators are present.")

    # def test_not_insertion(self):
    #     sentence = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (Outcome IS Negative)"
    #     expected = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (Outcome IS Negative)"
    #     # Clearly specify where and what to insert
    #     mutate_target = {'operator': 'OR', 'index': sentence.find('OR') + len('OR') + 1, 'new_operator': 'NOT'}
    #     mutated = gp_utilities.mutate_logical_operator(sentence, features, verbose=True, mutate_target=mutate_target)
    #     self.assertIn("NOT", mutated, "NOT should be inserted.")
    #     self.assertEqual(expected, mutated, "Proper NOT insertion with parentheses.")


    def test_not_removal(self):
        sentence = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (Outcome IS Negative)"
        expected = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (Outcome IS Negative)"
        # Manually specify the NOT to remove
        mutate_target = {'operator': 'NOT', 'index': sentence.find('NOT')}
        mutated = gp_utilities.mutate_logical_operator(sentence, features, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("NOT", mutated, "NOT should be removed.")
        self.assertEqual(expected, mutated, "Proper NOT removal.")

    def test_and_to_or_mutation(self):
        sentence = "IF (spy_close IS High) AND (volume IS Low) THEN (Risk IS High)"
        expected = "IF (spy_close IS High) OR (volume IS Low) THEN (Risk IS High)"
        mutate_target = {'operator': 'AND', 'index': sentence.find('AND'), 'new_operator': 'OR'}
        # Ensure arguments are in correct order and properly named
        mutated = gp_utilities.mutate_logical_operator(sentence, features, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("AND", mutated, "AND should be mutated to OR.")
        self.assertIn("OR", mutated, "Mutation should result in OR.")
        self.assertEqual(expected, mutated, "Proper mutation from AND to OR.")

    def test_or_to_and_mutation(self):
        sentence = "IF (gld_close IS Low) OR (macd IS Negative) THEN (Investment IS Bad)"
        expected = "IF (gld_close IS Low) AND (macd IS Negative) THEN (Investment IS Bad)"
        mutate_target = {'operator': 'OR', 'index': sentence.find('OR'), 'new_operator': 'AND'}
        # Ensure arguments are in correct order and properly named
        mutated = gp_utilities.mutate_logical_operator(sentence, features, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("OR", mutated, "OR should be mutated to AND.")
        self.assertIn("AND", mutated, "Mutation should result in AND.")
        self.assertEqual(expected, mutated, "Proper mutation from OR to AND.")

if __name__ == '__main__':
    unittest.main()

