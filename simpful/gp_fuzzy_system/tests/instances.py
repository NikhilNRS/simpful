import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from simpful.gp_fuzzy_system.rule_generator import RuleGenerator
from simpful.gp_fuzzy_system.evolvable_fuzzy_system import EvolvableFuzzySystem
from simpful.gp_fuzzy_system.auto_lvs import FuzzyLinguisticVariableProcessor

from pathlib import Path

# Initializing EvolvableFuzzySystem instances
economic_health = EvolvableFuzzySystem()
market_risk = EvolvableFuzzySystem()
investment_opportunity = EvolvableFuzzySystem()
inflation_prediction = EvolvableFuzzySystem()
market_sentiment = EvolvableFuzzySystem()
sepsis_system = EvolvableFuzzySystem()

# Load the CSV data
file_path = os.path.join(os.path.dirname(__file__), "gp_data_x_train.csv")
terms_dict_path = os.path.join(os.path.dirname(__file__), "..", "terms_dict.py")
exclude_columns = [
    "month",
    "day",
    "hour",
    "value",
    "volume",
]  # Default exclusion list
verbose = False
mf_type = "gaussian"  # or 'triangular' or 'sigmoid'

# Initialize the FuzzyLinguisticVariableProcessor
processor = FuzzyLinguisticVariableProcessor(
    file_path,
    terms_dict_path,
    verbose,
    exclude_columns,
    mf_type,
    use_standard_terms=True,
)
# Process the dataset
variable_store = processor.process_dataset()

# Initialize instances
instances = {
    "economic_health": economic_health,
    "market_risk": market_risk,
    "investment_opportunity": investment_opportunity,
    "inflation_prediction": inflation_prediction,
    "market_sentiment": market_sentiment,
    "sepsis_system": sepsis_system,
}

# Generate and add rules to each system using RuleGenerator
rg = RuleGenerator(variable_store, output_variable="PricePrediction", verbose=False)

for system_name, system in instances.items():
    rules = rg.generate_rules(2)
    for rule in rules:
        system.add_rule(rule)

if __name__ == "__main__":
    verbose_level = 0  # Default to no verbosity
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            verbose_level = 1
        if "-vv" in sys.argv:
            verbose_level = 2
        if "-vvv" in sys.argv:
            verbose_level = 3
        if "-vvvv" in sys.argv:
            verbose_level = 4
        if "-vvvvv" in sys.argv:  # Verbosity level 5
            verbose_level = 5

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
                print(
                    "No rules found or get_rules method not returning correctly."
                )  # Debug print

    if verbose_level == 3:
        # Print out all variables to confirm they're stored correctly
        all_vars = variable_store.get_all_variables()
        for name, var in all_vars.items():
            print(f"{name}: {var}")

    if verbose_level == 4:
        # Test retrieving terms for each variable from variable_store
        all_vars = variable_store.get_all_variables()
        for name, var in all_vars.items():
            print(f"Testing variable: {name}")
            # Get the terms for this variable
            terms = var.get_terms()
            print(f"Retrieved terms for {name}: {terms}")

    if verbose_level == 5:
        # Load exclude columns from CSV and display them
        exclude_columns_csv = os.path.join(os.path.dirname(__file__), "least_important_features.csv")
        
        # Initialize the processor with the CSV exclude columns
        processor = FuzzyLinguisticVariableProcessor(
            file_path,
            terms_dict_path,
            verbose,
            exclude_columns_csv=exclude_columns_csv,  # Specify the CSV file path here
            mf_type=mf_type,
            use_standard_terms=True,
        )
        # Process the dataset again with the excluded columns from the CSV
        variable_store = processor.process_dataset()

        # Print confirmation of processing and the excluded columns from the CSV
        print(f"Processed dataset using excluded columns from {exclude_columns_csv}")
