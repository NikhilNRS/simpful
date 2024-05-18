import unittest
import sys
from pathlib import Path
from instances import *
import gp_utilities

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

class TestLogicalOperatorMutation(unittest.TestCase):
    def test_find_no_operators(self):
        sentence = "if (gdp_growth IS High) THEN (PricePrediction IS PricePrediction)"  # Lowercase logical words
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 0, "No operators should be found in lowercase.")
        self.assertEqual(results, {}, "Results dictionary should be empty when operators are in lowercase.")

    def test_find_single_operator(self):
        sentence = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) THEN (PricePrediction IS PricePrediction)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertIn('AND', results, "AND should be found in uppercase.")
        self.assertEqual(results['AND']['count'], 1, "One AND should be found.")
        self.assertEqual(results['AND']['indices'], [sentence.find('AND')], "Index of AND should be correctly identified.")

    def test_find_multiple_operators(self):
        sentence = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) OR (inflation_rate IS Low) AND (NOT (market_trend IS Positive)) THEN (PricePrediction IS PricePrediction)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 3, "Three different operators should be found, all in uppercase.")
        expected_operators = {'AND': 2, 'OR': 1, 'NOT': 1}
        for op, expected_count in expected_operators.items():
            self.assertIn(op, results, f"{op} should be correctly identified.")
            self.assertEqual(results[op]['count'], expected_count, f"{op} should occur {expected_count} times.")
            self.assertIsInstance(results[op]['indices'], list, "Indices should be listed.")

    def test_detailed_operator_indices(self):
        sentence = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) OR (inflation_rate IS Low) OR (market_trend IS Negative) THEN (PricePrediction IS PricePrediction)"
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
        sentence = "if (gdp_growth IS High) then (Outcome IS Positive) THEN (PricePrediction IS PricePrediction)"
        results = gp_utilities.find_logical_operators(sentence)
        self.assertEqual(len(results), 0, "No operators should be found in lowercase.")
        self.assertEqual(results, {}, "Results dictionary should be empty when operators are in lowercase.")


    def test_no_operator_present(self):
        sentence = "IF (gdp_growth IS High) THEN (PricePrediction IS PricePrediction)"
        mutated, valid = gp_utilities.mutate_logical_operator(sentence, verbose=True)
        self.assertEqual(sentence, mutated, "Sentence should remain unchanged when no logical operators are present.")
        self.assertFalse(valid, "The mutation should be invalid when no logical operators are present.")


    def test_not_insertion(self):
        sentence = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (PricePrediction IS PricePrediction)"
        expected = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (PricePrediction IS PricePrediction)"
        # Clearly specify where and what to insert
        mutate_target = {'operator': 'OR', 'index': sentence.find('OR') + len('OR') + 1, 'new_operator': 'NOT'}
        mutated, valid = gp_utilities.mutate_logical_operator(sentence, verbose=True, mutate_target=mutate_target)
        self.assertIn("NOT", mutated, "NOT should be inserted.")
        self.assertEqual(expected, mutated, "Proper NOT insertion with parentheses.")
        self.assertTrue(valid, "The mutation should be valid.")
    
    def test_not_already_present_removal(self):
        sentence = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) OR (inflation_rate IS Low) AND (NOT (market_trend IS Positive)) THEN (PricePrediction IS PricePrediction)"
        # Define the mutate_target where 'NOT' is already present and should be removed instead
        mutate_target = {
        'operator': 'AND',
        'index': sentence.find("NOT"),
        'new_operator': 'NOT'
        }
        expected = "IF (gdp_growth IS Low) AND (unemployment_rate IS High) OR (inflation_rate IS Low) AND (market_trend IS Positive) THEN (PricePrediction IS PricePrediction)"
        mutated, valid = gp_utilities.mutate_logical_operator(sentence, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("NOT (market_trend IS Positive)", mutated, "NOT should be removed.")
        self.assertEqual(mutated, expected, "The sentence should have 'NOT' correctly removed.")
        self.assertTrue(valid, "The mutation should be valid.")


    def test_not_removal(self):
        sentence = "IF (gdp_growth IS Low) OR (NOT (unemployment_rate IS High)) THEN (PricePrediction IS PricePrediction)"
        expected = "IF (gdp_growth IS Low) OR (unemployment_rate IS High) THEN (PricePrediction IS PricePrediction)"
        # Manually specify the NOT to remove
        mutate_target = {'operator': 'NOT', 'index': sentence.find('NOT')}
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("NOT", mutated, "NOT should be removed.")
        self.assertEqual(expected, mutated, "Proper NOT removal.")

    def test_and_to_or_mutation(self):
        sentence = "IF (spy_close IS High) AND (volume IS Low) THEN (PricePrediction IS PricePrediction)"
        expected = "IF (spy_close IS High) OR (volume IS Low) THEN (PricePrediction IS PricePrediction)"
        mutate_target = {'operator': 'AND', 'index': sentence.find('AND'), 'new_operator': 'OR'}
        # Ensure arguments are in correct order and properly named
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("AND", mutated, "AND should be mutated to OR.")
        self.assertIn("OR", mutated, "Mutation should result in OR.")
        self.assertEqual(expected, mutated, "Proper mutation from AND to OR.")

    def test_or_to_and_mutation(self):
        sentence = "IF (gld_close IS Low) OR (macd IS Negative) THEN (PricePrediction IS PricePrediction)"
        expected = "IF (gld_close IS Low) AND (macd IS Negative) THEN (PricePrediction IS PricePrediction)"
        mutate_target = {'operator': 'OR', 'index': sentence.find('OR'), 'new_operator': 'AND'}
        # Ensure arguments are in correct order and properly named
        mutated = gp_utilities.mutate_logical_operator(sentence, verbose=True, mutate_target=mutate_target)
        self.assertNotIn("OR", mutated, "OR should be mutated to AND.")
        self.assertIn("AND", mutated, "Mutation should result in AND.")
        self.assertEqual(expected, mutated, "Proper mutation from OR to AND.")


class TestSelectRuleIndices(unittest.TestCase):
    def test_select_indices_with_actual_rules(self):
        # Correct usage with two separate rule lists
        index_self, index_partner = gp_utilities.select_rule_indices(economic_health._rules, market_risk._rules)
        self.assertIsNotNone(index_self, "Should select a valid index for self")
        self.assertIsNotNone(index_partner, "Should select a valid index for partner")
        self.assertTrue(0 <= index_self < len(economic_health._rules), "Index for self should be within range")
        self.assertTrue(0 <= index_partner < len(market_risk._rules), "Index for partner should be within range")


class TestSwapRules(unittest.TestCase):
    def test_swap_rules_with_actual_systems(self):
        system1 = economic_health.clone()
        system2 = market_risk.clone()

        # Store pre-swap rules for comparison
        pre_swap_rule1 = system1._rules[0]
        pre_swap_rule2 = system2._rules[0]

        # Perform the swap
        gp_utilities.swap_rules(system1, system2, 0, 0)

        # Test the results
        self.assertEqual(system1._rules[0], pre_swap_rule2, "Rule at index 0 of system1 should be swapped from system2")
        self.assertEqual(system2._rules[0], pre_swap_rule1, "Rule at index 0 of system2 should be swapped from system1")

class TestVerifyAndAddVariables(unittest.TestCase):
    def test_verify_and_add_variables_with_actual_system(self):
        # Use a system with missing variables in the set of rules
        system = economic_health.clone()
        system._rules = ["IF (non_existent_var IS Low) THEN (PricePrediction IS PricePrediction)"]

        # Assume non_existent_var is not in system._lvs but in all_linguistic_variables
        all_linguistic_variables = {'non_existent_var': spy_close_lv}  # Use an actual linguistic variable for the test

        # Run the verification
        gp_utilities.verify_and_add_variables(system, all_linguistic_variables, verbose=True)

        # Check if the variable was added
        self.assertIn('non_existent_var', system._lvs, "non_existent_var should have been added to the system's linguistic variables")

if __name__ == '__main__':
    unittest.main()

