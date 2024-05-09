import sys
from pathlib import Path
import unittest
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

if __name__ == '__main__':
    unittest.main()

# Run like this
# python -m unittest test_evolvable_fuzzy_system.py