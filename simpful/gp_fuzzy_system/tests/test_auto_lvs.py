import os
import pandas as pd
from simpful.gp_fuzzy_system._auto_lvs import FuzzyLinguisticVariableProcessor, run_optuna

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

if __name__ == "__main__":
    # Define paths for the input data
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

    # Initialize the FuzzyLinguisticVariableProcessor with the provided paths and options
    processor = FuzzyLinguisticVariableProcessor(
        file_path=file_path, 
        terms_dict_path=terms_dict_path, 
        verbose=verbose, 
        exclude_columns=exclude_columns, 
        mf_type=mf_type
    )

    # Run Optuna optimization
    run_optuna(processor)

    # Retrieve and inspect all linguistic variables
    variable_store = processor.process_dataset()
    all_variables = variable_store.get_all_variables()

    # Display all variables to inspect the results
    print("\nAll Linguistic Variables:")
    for name, variable in all_variables.items():
        print(f"Variable Name: {name}, Variable: {variable}")
