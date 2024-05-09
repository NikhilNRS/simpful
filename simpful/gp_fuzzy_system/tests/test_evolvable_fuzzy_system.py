import sys
from pathlib import Path
import unittest
import numpy as np
# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from instances import economic_health, market_risk, investment_opportunity, inflation_prediction, market_sentiment

# Now, you can use these instances in your tests
class TestEvolvableFuzzySystem(unittest.TestCase):
    def test_economic_health(self):
        # This is an example test, replace with actual logic
        self.assertIsNotNone(economic_health)

    def test_market_risk(self):
        # This is an example test, replace with actual logic
        self.assertIsNotNone(market_risk)

    def test_investment_opportunity(self):
        # This is an example test, replace with actual logic
        self.assertIsNotNone(investment_opportunity)

    def test_inflation_prediction(self):
        # This is an example test, replace with actual logic
        self.assertIsNotNone(inflation_prediction)

    def test_market_sentiment(self):
        # This is an example test, replace with actual logic
        self.assertIsNotNone(market_sentiment)

    def test_initialization(self):
        """Test initialization of systems."""
        self.assertIsNotNone(economic_health.fitness_score)
        self.assertEqual(economic_health.mutation_rate, 0.01)

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
        print("Initial rules:", economic_health._rules)

        if economic_health._rules:
            # Capture the original rule for comparison; assuming each rule is a tuple (condition, action)
            original_rule = economic_health._rules[0]
            print("Original rule before mutation:", original_rule)

            economic_health.mutate_rule()

            # Capture the mutated rule
            mutated_rule = economic_health._rules[0]
            print("Mutated rule after mutation:", mutated_rule)

            # Check if mutation actually occurred
            self.assertNotEqual(original_rule, mutated_rule, "Rule should be mutated.")
        else:
            self.skipTest("No rules to mutate in the system.")

        print("Final rules after mutation:", economic_health._rules)


    def test_crossover(self):
        """Test crossover functionality."""
        partner_system = market_risk.clone()
        offspring1, offspring2 = economic_health.crossover(partner_system)
        self.assertIsNotNone(offspring1)
        self.assertIsNotNone(offspring2)
        # Check if offspring have parts of both parents' rules
        self.assertNotEqual(offspring1._rules, economic_health._rules)
        self.assertNotEqual(offspring2._rules, market_risk._rules)

    def test_evaluate_fitness(self):
        """Test fitness evaluation based on RMSE."""
        historical_data = np.array([1, 2, 3, 4, 5])
        predictions = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        fitness_score = economic_health.evaluate_fitness(historical_data, predictions)
        expected_rmse = np.sqrt(np.mean((predictions - historical_data) ** 2))
        self.assertAlmostEqual(fitness_score, expected_rmse)


if __name__ == '__main__':
    unittest.main()

# Run like this
# python -m unittest test_evolvable_fuzzy_system.py