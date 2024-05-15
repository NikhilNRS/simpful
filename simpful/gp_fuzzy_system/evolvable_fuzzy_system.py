from simpful import FuzzySystem
import numpy as np
from copy import deepcopy
import gp_utilities
from rule_processor import format_rule 
import random
import re

class EvolvableFuzzySystem(FuzzySystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fitness_score = 0
        self.mutation_rate = 1  # Adjustable mutation rate for evolution
        self.available_features = []  # Example features

    def clone(self):
        """Creates a deep copy of the system, ensuring independent instances."""
        return deepcopy(self)

    def get_rules(self, format=True):
        """
        Fetches rules and optionally formats them using the RuleProcessor.
        """
        rules = super().get_rules()  # This gets the unformatted list of rules.
        if format:
            # Assumes format_rules is static and can be called with a list of rules.
            formatted_rules = [format_rule(rule) for rule in rules]
            return formatted_rules
        return rules

        
    def get_rules_(self):
        # Implement fetching rules without calling the rule_processor's process_rules_from_system
        return self._rules  # Assuming _rules holds the actual rules directly within the system

    def add_rule(self, rule):
        """Adds a new fuzzy rule to the system."""
        super().add_rules([rule])

    def mutate_feature(self, variable_store, verbose=False):
        """
        Mutates a feature within a rule by replacing it with another from the available features list,
        ensuring the terms are also compatible.
        """
        current_rules = self.get_rules()
        if not current_rules:
            if verbose:
                print("No rules available to mutate.")
            return
        
        rule_index = random.randint(0, len(current_rules) - 1)
        original_rule = current_rules[rule_index]
        # Example rule: "IF (feature IS term) THEN outcome"

        feature_term_pair = gp_utilities.extract_feature_term(original_rule, self.available_features)
        if not feature_term_pair:
            if verbose:
                print("No feature-term pairs found in the rule to mutate.")
            return

        feature_to_replace, current_term = feature_term_pair
        new_feature = random.choice([f for f in self.available_features if f != feature_to_replace])

        # Fetch a valid term for the new feature
        new_term = gp_utilities.get_valid_term(new_feature, current_term, variable_store)

        # Construct the mutated rule
        mutated_rule = original_rule.replace(f"{feature_to_replace} IS {current_term}", f"{new_feature} IS {new_term}")

        self.replace_rule(rule_index, mutated_rule, verbose=verbose)
        self.ensure_linguistic_variables(variable_store, verbose=verbose)

        if verbose:
            print(f"Mutated rule: Changed '{feature_to_replace} IS {current_term}' to '{new_feature} IS {new_term}' in rule.")

        
    def extract_features_from_rule(self, rule):
        """Extract unique features from a single fuzzy rule."""
        if not rule:
            print("No rule provided.")
            return []

        features_set = set()
        # Find all alphanumeric words in the rule; assume they include feature names
        words = re.findall(r'\w+', rule)
        features_in_rule = [word for word in words if word in self.available_features]
        features_set.update(features_in_rule)

        return list(features_set)
    
    def mutate_operator(self):
        """Selects a random rule, mutates it, and replaces the original with the new one."""
        current_rules = self.get_rules()  # Fetch current rules using the formatted get_rules
        if not current_rules:
            print("No rules available to mutate.")
            return  # Exit if there are no rules to mutate

        # Select a random rule to mutate
        rule_index = random.randint(0, len(current_rules) - 1)
        original_rule = current_rules[rule_index]

        # Mutate this selected rule using the extracted features
        mutated_rule = gp_utilities.mutate_logical_operator(original_rule)

        # Replace the mutated rule in the system
        self.replace_rule(rule_index, mutated_rule, verbose=True)
    
    def crossover(self, partner_system, variable_store, verbose=True):
        # Similar setup, but now uses variable_store for linguistic variables
        if not self._rules or not partner_system._rules:
            if verbose:
                print("No rules available to crossover.")
            return None, None

        # Select indices and perform cloning as before
        index_self, index_partner = gp_utilities.select_rule_indices(self._rules, partner_system._rules)
        if index_self is None or index_partner is None:
            if verbose:
                print("Failed to select rule indices.")
            return None, None

        new_self = self.clone()
        new_partner = partner_system.clone()


        gp_utilities.swap_rules(new_self, new_partner, index_self, index_partner)

        # Use variable_store for verification
        gp_utilities.verify_and_add_variables(new_self, variable_store, verbose)
        gp_utilities.verify_and_add_variables(new_partner, variable_store, verbose)

        if verbose:
            print("Completed linguistic verification post-crossover.")
            print("New self variables:", new_self._lvs.keys())
            print("New partner variables:", new_partner._lvs.keys())

        return new_self, new_partner
    
    def ensure_linguistic_variables(self, variable_store, verbose=True):
        """
        Ensure each rule's linguistic variables are present in the fuzzy system. If any are missing,
        add them from a variable store.
        """
        rule_features = self.extract_features_from_rules()
        existing_variables = set(self._lvs.keys())

        missing_variables = [feat for feat in rule_features if feat not in existing_variables]
        for feature in missing_variables:
            if variable_store.has_variable(feature):
                self.add_linguistic_variable(feature, variable_store.get_variable(feature))
                if verbose:
                    print(f"Added missing linguistic variable for '{feature}'.")
            else:
                if verbose:
                    print(f"Warning: No predefined linguistic variable for '{feature}' in the store.")


    def post_crossover_linguistic_verification(self, offspring1, offspring2, variable_store, verbose=True):
        """
        Ensures that each offspring has all necessary linguistic variables after crossover.
        Verifies and adds missing variables from their predefined set of all_linguistic_variables.
        """
        offspring1.ensure_linguistic_variables(variable_store, verbose)
        offspring2.ensure_linguistic_variables(variable_store, verbose)


    def evaluate_fitness(self, historical_data, predictions):
        """Calculates the fitness score based on a comparison metric like RMSE."""
        rmse = np.sqrt(np.mean((np.array(predictions) - np.array(historical_data)) ** 2))
        self.fitness_score = rmse
        return self.fitness_score

    def extract_features_from_rules(self):
        """Extract unique features from the current fuzzy rules."""
        current_rules = self.get_rules()
        if not current_rules:
            print("No rules to analyze.")
            return []

        features_set = set()
        for rule in current_rules:
            # Find all alphanumeric words in the rule; assume they include feature names
            words = re.findall(r'\w+', rule)
            features_in_rule = [word for word in words if word in self.available_features]
            features_set.update(features_in_rule)

        return list(features_set)
    
    def predict_with_fis(self, data, print_predictions=False):
        """
        Makes predictions for the EvolvableFuzzySystem instance using the features defined in its rules.

        :param data: pandas DataFrame containing the input data.
        :param print_predictions: Boolean, if True, prints the first 5 predictions.
        :return: List of predictions.
        """
        # Extract features used in the rules of this fuzzy system
        features_used = self.extract_features_from_rules()

        # Ensure the DataFrame contains all necessary features
        if not all(feature in data.columns for feature in features_used):
            missing_features = [feature for feature in features_used if feature not in data.columns]
            raise ValueError(f"Data is missing required features: {missing_features}")
        
        # Subset the DataFrame based on the features used in this system
        subset_data = data[features_used]

        # Initialize an empty list to store predictions
        predictions = []

        # Iterate through each row in the subset data to make predictions
        for index, row in subset_data.iterrows():
            # Set each variable in the system to its value in the current row
            for feature_name in features_used:
                self.set_variable(feature_name, row[feature_name])
            
            # Perform Sugeno inference and add the result to our predictions list
            prediction = self.Sugeno_inference(["PricePrediction"])
            predictions.append(prediction)

        # Optionally print the first 5 predictions
        if print_predictions:
            print(f"{self.__class__.__name__} Predictions:")
            for pred in predictions[:5]:  # Print the first 5 predictions as an example
                print(pred)

        return predictions

if __name__ == "__main__":
    pass



"""
Refined To-Do List for Future Enhancements:

1. Advanced Selection Mechanism:
   - Implement or integrate advanced selection mechanisms to evaluate and pick individuals according to fitness metrics such as precision, RMSE, or custom evaluation functions.

2. Dynamic Mutation of Rule Structure:
   - Expand mutation operations to allow for structural modifications of individuals, such as swapping variables within rules or changing the logical structure of conditions.

3. Scalability and Efficiency Enhancements:
   - Assess and optimize the computational efficiency and scalability of the system, ensuring it can handle large datasets and complex rule sets.

Each of these enhancements contributes directly to evolving fuzzy rule sets for data-driven solutions, aligning with the dissertation's objectives to address design problems through genetic programming. 
Focus on incremental development, ensuring each enhancement strengthens the system's ability to evolve and evaluate fuzzy rule sets effectively.
"""
