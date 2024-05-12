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

class TestLogicalOperatorMutation(unittest.TestCase):
    def test_no_operator_present(self):
        sentence = "IF (gdp_growth IS High) THEN (Outcome IS Positive)"
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertEqual(sentence, mutated, "Sentence should remain unchanged when no logical operators are present.")

    def test_not_insertion(self):
        sentence = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (Outcome IS Negative)"
        expected = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (Outcome IS Negative)"
        gp_utilities.random.seed(0)  # Set seed for reproducibility
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertIn("NOT", mutated, "NOT should be inserted.")
        self.assertEqual(expected, mutated, "Proper NOT insertion with parentheses.")

    def test_not_removal(self):
        sentence = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (Outcome IS Negative)"
        expected = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (Outcome IS Negative)"
        gp_utilities.random.seed(1)  # Set seed for reproducibility
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertNotIn("NOT", mutated, "NOT should be removed.")
        self.assertEqual(expected, mutated, "Proper NOT removal.")

    def test_and_to_or_mutation(self):
        sentence = "IF (spy_close IS High) AND (volume IS Low) THEN (Risk IS High)"
        expected = "IF (spy_close IS High) OR (volume IS Low) THEN (Risk IS High)"
        gp_utilities.random.seed(2)  # Set seed for reproducibility
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertNotIn("AND", mutated, "AND should be mutated to OR.")
        self.assertIn("OR", mutated, "Mutation should result in OR.")
        self.assertEqual(expected, mutated, "Proper mutation from AND to OR.")

    def test_or_to_and_mutation(self):
        sentence = "IF (gld_close IS Low) OR (macd IS Negative) THEN (Investment IS Bad)"
        expected = "IF (gld_close IS Low) AND (macd IS Negative) THEN (Investment IS Bad)"
        gp_utilities.random.seed(3)  # Set seed for reproducibility
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertNotIn("OR", mutated, "OR should be mutated to AND.")
        self.assertIn("AND", mutated, "Mutation should result in AND.")
        self.assertEqual(expected, mutated, "Proper mutation from OR to AND.")

if __name__ == '__main__':
    unittest.main()

