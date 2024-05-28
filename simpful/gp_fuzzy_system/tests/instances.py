import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from simpful import *
from rule_generator import RuleGenerator
from evolvable_fuzzy_system import EvolvableFuzzySystem

# Initializing EvolvableFuzzySystem instances
economic_health = EvolvableFuzzySystem()
market_risk = EvolvableFuzzySystem()
investment_opportunity = EvolvableFuzzySystem()
inflation_prediction = EvolvableFuzzySystem()
market_sentiment = EvolvableFuzzySystem()
sepsis_system = EvolvableFuzzySystem()

# Load the CSV data
file_path = 'gp_data_x_train.csv'  # Adjusted to reflect the correct path within the tests directory
terms_dict_path = '../terms_dict.py'  # Adjusted to reflect the correct path within the current directory
exclude_columns = ['month', 'day', 'hour']
verbose = False

# Initialize the FuzzyLinguisticVariableProcessor
from auto_lvs import FuzzyLinguisticVariableProcessor
processor = FuzzyLinguisticVariableProcessor(file_path, terms_dict_path, verbose, exclude_columns)
variable_store = processor.process_dataset()

# Initialize instances
instances = {
    "economic_health": economic_health,
    "market_risk": market_risk,
    "investment_opportunity": investment_opportunity,
    "inflation_prediction": inflation_prediction,
    "market_sentiment": market_sentiment,
    "sepsis_system": sepsis_system
}

# Generate and add rules to each system using RuleGenerator
rg = RuleGenerator(variable_store, verbose=False)

for system_name, system in instances.items():
    rules = rg.generate_rules(2)
    for rule in rules:
        system.add_rule(rule)

# Define output functions for each system
def set_output_function(system, feature_names):
    system.set_output_function("PricePrediction", " + ".join([f"1*{name}" for name in feature_names]))

set_output_function(economic_health, economic_health.extract_features_from_rules())
set_output_function(market_risk, market_risk.extract_features_from_rules())
set_output_function(investment_opportunity, investment_opportunity.extract_features_from_rules())
set_output_function(inflation_prediction, inflation_prediction.extract_features_from_rules())
set_output_function(market_sentiment, market_sentiment.extract_features_from_rules())

if __name__ == "__main__":
    verbose_level = 0  # Default to no verbosity
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            verbose_level = 1
        if "-vv" in sys.argv:
            verbose_level = 2
        if "-vvv" in sys.argv:
            verbose_level = 3
    
    # For '-v' argument: Print all instances and their rules
    if verbose_level == 1:
        for name, instance in instances.items():
            print(f"Instance Name: {name}")
            print("Rules:")
            for rule in instance._rules:
                print(f" - {rule}")
            print()

    if verbose_level == 2:
        for name, instance in instances.items():
            print(f"Detailed Rules for {name}:")
            detailed_rules = instance.get_rules_()
            if detailed_rules:
                for rule in detailed_rules:
                    print(f" - {rule}")
            else:
                print("No rules found or get_rules method not returning correctly.")  # Debug print

    if verbose_level == 3:
        # Print out all variables to confirm they're stored correctly
        all_vars = variable_store.get_all_variables()
        for name, var in all_vars.items():
            print(f"{name}: {var}")
