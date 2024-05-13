import unittest
import sys
sys.path.append('..')
from rule_processor import RuleProcessor

class TestRuleFormatting(unittest.TestCase):
    def test_format_rules(self):
        rules = [
            "IF ((gdp_growth_annual_prcnt IS Low) AND (unemployment_rate_value IS High)) THEN (PricePrediction IS PricePrediction)",
            "IF ((trade_balance_value IS Low) OR (foreign_direct_investment_value IS Low)) THEN (PricePrediction IS PricePrediction)",
            "IF ((spy_close IS High) OR (volume IS Low)) THEN (PricePrediction IS PricePrediction)",
            "IF ((gld_close IS Low) AND (macd IS Negative)) THEN (PricePrediction IS PricePrediction)",
            "IF ((gld_close IS High) AND (foreign_direct_investment_value IS High)) THEN (PricePrediction IS PricePrediction)",
            "IF ((spy_close IS Low) AND (volume IS High)) THEN (PricePrediction IS PricePrediction)",
            "IF (inflation_rate_value IS Medium) THEN (PricePrediction IS PricePrediction)",
            "IF ((gdp_growth_annual_prcnt IS High) OR ( NOT (unemployment_rate_value IS Low))) THEN (PricePrediction IS PricePrediction)",
            "IF ((macd IS Positive) OR (rsi IS Oversold)) THEN (PricePrediction IS PricePrediction)",
            "IF ((volume IS High) AND (spy_close IS High)) THEN (PricePrediction IS PricePrediction)"
        ]

        expected_output = [
            "IF (gdp_growth_annual_prcnt IS Low) AND (unemployment_rate_value IS High) THEN (PricePrediction IS PricePrediction)",
            "IF (trade_balance_value IS Low) OR (foreign_direct_investment_value IS Low) THEN (PricePrediction IS PricePrediction)",
            "IF (spy_close IS High) OR (volume IS Low) THEN (PricePrediction IS PricePrediction)",
            "IF (gld_close IS Low) AND (macd IS Negative) THEN (PricePrediction IS PricePrediction)",
            "IF (gld_close IS High) AND (foreign_direct_investment_value IS High) THEN (PricePrediction IS PricePrediction)",
            "IF (spy_close IS Low) AND (volume IS High) THEN (PricePrediction IS PricePrediction)",
            "IF (inflation_rate_value IS Medium) THEN (PricePrediction IS PricePrediction)",
            "IF (gdp_growth_annual_prcnt IS High) OR (NOT (unemployment_rate_value IS Low)) THEN (PricePrediction IS PricePrediction)",
            "IF (macd IS Positive) OR (rsi IS Oversold) THEN (PricePrediction IS PricePrediction)",
            "IF (volume IS High) AND (spy_close IS High) THEN (PricePrediction IS PricePrediction)"
        ]


        formatted_rules = RuleProcessor.format_rules(rules)
        for actual, expected in zip(formatted_rules, expected_output):
            self.assertEqual(actual, expected, f"Expected '{expected}', got '{actual}'")

if __name__ == '__main__':
    unittest.main()
