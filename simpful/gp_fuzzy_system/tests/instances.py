import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from simpful.gp_fuzzy_system.rule_generator import RuleGenerator
from simpful.gp_fuzzy_system.evolvable_fuzzy_system import EvolvableFuzzySystem
from simpful.gp_fuzzy_system._auto_lvs import FuzzyLinguisticVariableProcessor
from pathlib import Path


def read_exclude_columns_from_file(file_path):
    """Helper function to read column names to exclude from a file."""
    try:
        # Read the CSV file into a DataFrame
        exclude_columns_df = pd.read_csv(file_path, header=None)

        # Debug print to show the DataFrame
        print("Exclude Columns DataFrame:")
        print(exclude_columns_df)  # Print entire DataFrame to inspect

        # Flatten the DataFrame to a single list of column names
        exclude_columns = exclude_columns_df.values.flatten().tolist()

        # Strip whitespace and remove any empty strings
        exclude_columns = [col.strip() for col in exclude_columns if str(col).strip()]

        return exclude_columns
    except Exception as e:
        print(f"Error reading exclude columns file: {e}")
        return []

# Load the CSV data
file_path = os.path.join(os.path.dirname(__file__), 'gp_data_X_train.csv')
terms_dict_path = os.path.join(os.path.dirname(__file__), '..', 'terms_dict.py')
exclude_columns_input = os.path.join(os.path.dirname(__file__), 'least_important_features.csv')
verbose = False
mf_type = 'sigmoid'  # or 'triangular' or 'sigmoid'

# Always exclude 'month', 'day', and 'hour'
default_exclude_columns = ['month', 'day', 'hour']

# Check if exclude_columns_input is a file path and read additional columns if it exists
if os.path.isfile(exclude_columns_input):
    exclude_columns = read_exclude_columns_from_file(exclude_columns_input)
    exclude_columns = list(set(default_exclude_columns + exclude_columns))  # Combine and remove duplicates
else:
    exclude_columns = default_exclude_columns  # Only use the default exclusions


# Initialize the FuzzyLinguisticVariableProcessor
processor = FuzzyLinguisticVariableProcessor(file_path, terms_dict_path, verbose, exclude_columns, mf_type)

# Process the dataset
variable_store = processor.process_dataset()

# Initialize EvolvableFuzzySystem instances
economic_health = EvolvableFuzzySystem()
market_risk = EvolvableFuzzySystem()
investment_opportunity = EvolvableFuzzySystem()
inflation_prediction = EvolvableFuzzySystem()
market_sentiment = EvolvableFuzzySystem()
sepsis_system = EvolvableFuzzySystem()

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
    # Set available features from the variable store
    system.set_available_features_from_variable_store(variable_store)
    
    # Generate rules for the system
    rules = rg.generate_rules(2)
    print(f"Generated rules for {system_name}: {rules}")  # Debug: Print generated rules
    
    # Add the generated rules to the system
    for rule in rules:
        system.add_rule(rule)
    
    # Print the added rules for debugging
    print(f"Rules in system {system_name}: {system.get_rules_()}")  # Debug: Print the added rules
    
    # Update the output function based on the available features
    if system.available_features:
        system.set_output_function(system, system.available_features)
        print(f"Updated output function for {system_name} using features: {system.available_features}")
    else:
        print(f"Warning: No available features found for {system_name}. Output function not set.")


# Define output functions for each system
def set_output_function(system, feature_names):
    # Check if feature_names is valid and not empty
    if not feature_names or len(feature_names) == 0:
        print(f"Warning: No features extracted for {system}. Skipping output function setting.")
        return  # Skip if no valid features are found
    
    # Construct the output function
    function_str = " + ".join([f"1*{name}" for name in feature_names])
    
    # Debugging print statements
    print(f"Setting output function for {system}: {function_str}")
    
    # Set the output function in the system
    system.set_output_function("PricePrediction", function_str)




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
