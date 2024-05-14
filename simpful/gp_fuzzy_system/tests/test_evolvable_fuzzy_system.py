import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import re

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from instances import economic_health, market_risk, investment_opportunity, inflation_prediction, market_sentiment, make_predictions_with_models


class TestEvolvableFuzzySystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the CSV data
        cls.test_data = pd.read_csv(Path(__file__).resolve().parent / 'selected_variables_first_100.csv')
        # Set available features for economic_health based on test data columns
        cls.available_features = cls.test_data.columns.tolist()
        # Assigning the available features to economic_health
        economic_health.available_features = cls.available_features


    def test_initialization(self):
        """Test initialization of systems."""
        self.assertIsNotNone(economic_health.fitness_score)
        self.assertEqual(economic_health.mutation_rate, 1)

    def test_clone(self):
        """Test cloning functionality ensures deep copy."""
        clone = economic_health.clone()
        self.assertNotEqual(id(economic_health), id(clone))
        self.assertEqual(len(economic_health._rules), len(clone._rules))


    def test_add_rule(self):
        """Test adding a rule to the system."""
        rule_count_before = len(economic_health._rules)
        economic_health.add_rule("IF inflation_rate_value IS High THEN PricePrediction IS PricePrediction")
        self.assertEqual(len(economic_health._rules), rule_count_before + 1)
    
    def test_mutate_feature(self):
        """Test mutation of a feature within a rule and check linguistic variables."""
        self.assertGreater(len(economic_health.get_rules()), 0, "There should be initial rules for mutation.")
        original_rules = economic_health.get_rules()
        original_variables = set(economic_health._lvs.keys())

        economic_health.mutate_feature(verbose=True)  # Verbose true to capture output if needed

        mutated_rules = economic_health.get_rules()
        mutated_variables = set(economic_health._lvs.keys())

        self.assertNotEqual(original_rules, mutated_rules, "At least one rule should be mutated after feature mutation.")
        self.assertEqual(sum(original != mutated for original, mutated in zip(original_rules, mutated_rules)), 1, "Exactly one feature in one rule should be mutated.")
        self.assertTrue(any(feature in economic_health.available_features for rule in mutated_rules for feature in re.findall(r'\b\w+\b', rule)), "Mutated features should exist within the available features list.")
        self.assertTrue(mutated_variables >= original_variables, "All necessary linguistic variables should be present after mutation.")


    def test_mutate_rule(self):
        """Test mutation of a rule with added logging to check the structure and mutation effect."""
        # Get the initial formatted state of rules for comparison
        original_formatted_rules = economic_health.get_rules()
        original_rules_str = [str(rule) for rule in original_formatted_rules]

        # Perform mutation
        economic_health.mutate_operator()

        # Fetching the state of rules after mutation
        mutated_formatted_rules = economic_health.get_rules()
        mutated_rules_str = [str(rule) for rule in mutated_formatted_rules]

        # Output for clarity in test output
        print("Original rules:", original_rules_str)
        print("Mutated rules:", mutated_rules_str)

        # Assert that the rules have changed
        self.assertNotEqual(original_rules_str, mutated_rules_str, "Rules should be mutated.")

        # Check if exactly one rule was mutated (assuming only one mutation occurs at a time)
        differences = sum(1 for original, mutated in zip(original_rules_str, mutated_rules_str) if original != mutated)
        self.assertEqual(differences, 1, "Exactly one rule should be mutated.")

    def test_crossover(self):
        """Test crossover functionality with rule swapping checks."""
        partner_system = market_risk.clone()
        offspring1, offspring2 = economic_health.crossover(partner_system)

        self.assertIsNotNone(offspring1, "Offspring 1 should be successfully created.")
        self.assertIsNotNone(offspring2, "Offspring 2 should be successfully created.")

        rules_self_before = set(economic_health.get_rules())
        rules_partner_before = set(partner_system.get_rules())
        rules_self_after = set(offspring1.get_rules())
        rules_partner_after = set(offspring2.get_rules())

        self.assertTrue(rules_self_after != rules_self_before or rules_partner_after != rules_partner_before, "Offspring rules should differ from parent rules.")
        self.assertTrue(rules_self_after.issubset(rules_self_before.union(rules_partner_before)), "All offspring 1 rules should come from one of the parents.")
        self.assertTrue(rules_partner_after.issubset(rules_self_before.union(rules_partner_before)), "All offspring 2 rules should come from one of the parents.")

        # After verifying rule swapping, check linguistic variable completeness
        economic_health.post_crossover_linguistic_verification(offspring1, offspring2)
        self.assertTrue(all(feature in offspring1._lvs for feature in offspring1.extract_features_from_rules()), "Offspring 1 should have all necessary linguistic variables.")
        self.assertTrue(all(feature in offspring2._lvs for feature in offspring2.extract_features_from_rules()), "Offspring 2 should have all necessary linguistic variables.")

    
    def test_crossover_produces_different_offspring(self):
        """Test crossover functionality ensures different offspring."""
        partner_system = market_risk.clone()
        offspring1, offspring2 = economic_health.crossover(partner_system)

        # Assert that both offspring are not None
        self.assertIsNotNone(offspring1, "First offspring should not be None")
        self.assertIsNotNone(offspring2, "Second offspring should not be None")

        # Assert that offspring have parts of both parents' rules
        self.assertNotEqual(offspring1._rules, economic_health._rules, "Offspring 1 should have different rules from economic_health")
        self.assertNotEqual(offspring2._rules, market_risk._rules, "Offspring 2 should have different rules from market_risk")

        # Check that the offspring are different from each other
        self.assertNotEqual(offspring1._rules, offspring2._rules, "The two offspring should have different rules")

        # Additional checks for linguistic variables can be done if considered necessary


    def test_evaluate_fitness(self):
        """Test fitness evaluation based on RMSE."""
        historical_data = np.array([1, 2, 3, 4, 5])
        predictions = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        fitness_score = economic_health.evaluate_fitness(historical_data, predictions)
        expected_rmse = np.sqrt(np.mean((predictions - historical_data) ** 2))
        self.assertAlmostEqual(fitness_score, expected_rmse)

    def test_predict_with_fis(self):
        """Test the predict_with_fis function to ensure it uses the rule-based features correctly."""
        # Ensure economic_health has been initialized and has rules
        self.assertTrue(economic_health._rules, "economic_health should have rules initialized")
        # Call the predict_with_fis function
        predictions = economic_health.predict_with_fis(self.test_data)
        # Ensure predictions are returned as expected
        self.assertIsInstance(predictions, list, "Should return a list of predictions")
        self.assertEqual(len(predictions), len(self.test_data), "Should return one prediction per data row")



if __name__ == '__main__':
    unittest.main()
