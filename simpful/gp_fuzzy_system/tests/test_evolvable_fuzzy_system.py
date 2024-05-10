import sys
from pathlib import Path
import unittest
import numpy as np

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from instances import economic_health, market_risk, investment_opportunity, inflation_prediction, market_sentiment
from simpful.rule_parsing import Functional  # Ensure Functional is properly imported if used

class TestEvolvableFuzzySystem(unittest.TestCase):
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
        """Test crossover functionality to ensure rules are properly exchanged."""
        partner_system = market_risk.clone()
        original_rules_self = economic_health.get_rules()
        original_rules_partner = partner_system.get_rules()

        offspring1, offspring2 = economic_health.crossover(partner_system)
        
        # Ensure offspring are created
        self.assertIsNotNone(offspring1)
        self.assertIsNotNone(offspring2)

        # Ensure the offspring systems contain the swapped rules
        offspring1_rules = offspring1.get_rules()
        offspring2_rules = offspring2.get_rules()

        # Check if offspring rules have changed from original
        self.assertNotEqual(offspring1_rules, original_rules_self)
        self.assertNotEqual(offspring2_rules, original_rules_partner)

        # More detailed check: ensure at least one rule from each parent is in the opposite offspring
        # This checks for actual content change, not just reference or length change
        self.assertTrue(any(rule in offspring2_rules for rule in original_rules_self))
        self.assertTrue(any(rule in offspring1_rules for rule in original_rules_partner))

        # Length of rules should not change
        self.assertEqual(len(offspring1_rules), len(original_rules_self))
        self.assertEqual(len(offspring2_rules), len(original_rules_partner))


    def test_evaluate_fitness(self):
        """Test fitness evaluation based on RMSE."""
        historical_data = np.array([1, 2, 3, 4, 5])
        predictions = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        fitness_score = economic_health.evaluate_fitness(historical_data, predictions)
        expected_rmse = np.sqrt(np.mean((predictions - historical_data) ** 2))
        self.assertAlmostEqual(fitness_score, expected_rmse)

if __name__ == '__main__':
    unittest.main()
