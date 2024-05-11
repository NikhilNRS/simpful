import sys
from pathlib import Path
import unittest
import numpy as np
import re

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from instances import economic_health, market_risk, investment_opportunity, inflation_prediction, market_sentiment
from simpful.rule_parsing import Functional  # Ensure Functional is properly imported if used

class TestEvolvableFuzzySystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup shared resources or configurations for tests."""
        # Adding the feature list directly in class for broader availability
        cls.available_features = [
            'gdp_growth_annual_prcnt', 'unemployment_rate_value', 
            'trade_balance_value', 'foreign_direct_investment_value', 
            'spy_close', 'volume', 'gld_close', 'macd', 'rsi', 
            'inflation_rate_value'
        ]
        # Assuming `economic_health` is already imported and setup
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
        """Test mutation of a feature within a rule."""
        # Assure there are initial rules to test
        self.assertGreater(len(economic_health.get_rules()), 0, "There should be initial rules for mutation.")

        # Get the initial state of rules for comparison
        original_rules = economic_health.get_rules()

        # Perform feature mutation
        economic_health.mutate_feature()

        # Fetch the rules after mutation
        mutated_rules = economic_health.get_rules()

        # Check that at least one rule has changed
        self.assertNotEqual(original_rules, mutated_rules, "At least one rule should be mutated after feature mutation.")

        # Verify that exactly one rule has a feature mutated
        changes = [original != mutated for original, mutated in zip(original_rules, mutated_rules)]
        self.assertEqual(sum(changes), 1, "Exactly one feature in one rule should be mutated.")

        # Ensure mutated feature is within the available features list
        mutated_feature_found = any(
            feature for rule in mutated_rules for feature in re.findall(r'\b\w+\b', rule)
            if feature in self.available_features
        )
        self.assertTrue(mutated_feature_found, "Mutated features should exist within the available features list.")

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
        """Test crossover functionality with random rule exchange."""
        partner_system = market_risk.clone()
        offspring1, offspring2 = economic_health.crossover(partner_system)

        self.assertIsNotNone(offspring1)
        self.assertIsNotNone(offspring2)

        # Extract rules to make verification easier
        rules_self_before = economic_health.get_rules()
        rules_partner_before = partner_system.get_rules()
        rules_self_after = offspring1.get_rules()
        rules_partner_after = offspring2.get_rules()

        # Check that at least one rule in the offspring is different from the parent at any index
        rule_swapped_from_self = any([rule not in rules_self_before for rule in rules_self_after])
        rule_swapped_from_partner = any([rule not in rules_partner_before for rule in rules_partner_after])

        self.assertTrue(rule_swapped_from_self, "Offspring 1 should have at least one rule not in the original economic_health system.")
        self.assertTrue(rule_swapped_from_partner, "Offspring 2 should have at least one rule not in the original market_risk system.")

        # Additional check for randomness in rule exchange (optional, for more rigorous testing)
        # Check if there's at least one rule that came from the partner system
        self.assertTrue(any(rule in rules_partner_before for rule in rules_self_after), 
                        "Offspring 1 should contain at least one rule from the partner system.")
        self.assertTrue(any(rule in rules_self_before for rule in rules_partner_after), 
                        "Offspring 2 should contain at least one rule from the economic_health system.")
    
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



    def test_evaluate_fitness(self):
        """Test fitness evaluation based on RMSE."""
        historical_data = np.array([1, 2, 3, 4, 5])
        predictions = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        fitness_score = economic_health.evaluate_fitness(historical_data, predictions)
        expected_rmse = np.sqrt(np.mean((predictions - historical_data) ** 2))
        self.assertAlmostEqual(fitness_score, expected_rmse)

if __name__ == '__main__':
    unittest.main()
