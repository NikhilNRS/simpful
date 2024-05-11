from simpful import FuzzySystem
import numpy as np
from copy import deepcopy
import gp_utilities
import random
import re

class EvolvableFuzzySystem(FuzzySystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fitness_score = None
        self.mutation_rate = 1  # Adjustable mutation rate for evolution
        self.available_features = ['gdp_growth_annual_prcnt', 'unemployment_rate_value', 'trade_balance_value', 'foreign_direct_investment_value']  # Example features


    def clone(self):
        """Creates a deep copy of the system, ensuring independent instances."""
        return deepcopy(self)

    def get_rules(self):
        """
        Fetch and format the rules, removing unnecessary parentheses.
        """
        rules = super().get_rules()
        return self.format_rules(rules)

    @staticmethod
    def format_rules(rules):
        formatted_rules = []
        pattern = r'^IF \(\((.*)\)\) THEN (.*)$'
        for rule in rules:
            match = re.match(pattern, rule)
            if match:
                condition = match.group(1)
                consequence = match.group(2)
                formatted_rule = f"IF ({condition}) THEN {consequence}"
                formatted_rules.append(formatted_rule)
            else:
                formatted_rules.append(rule)
        return formatted_rules

    def add_rule(self, rule):
        """Adds a new fuzzy rule to the system."""
        super().add_rules([rule])

    def mutate_feature(self):
            """Mutates a feature within a rule by replacing it with another from the available features list."""
            current_rules = self.get_rules()  # Fetch current rules using the formatted get_rules
            if not current_rules:
                print("No rules available to mutate.")
                return  # Exit if there are no rules to mutate
            
            # Select a random rule to mutate
            rule_index = random.randint(0, len(current_rules) - 1)
            original_rule = current_rules[rule_index]

            # Extract all words from the rule, assuming features are identifiable as whole words
            words = re.findall(r'\w+', original_rule)
            features_in_rule = [word for word in words if word in self.available_features]

            if not features_in_rule:
                print("No features found in the rule to mutate.")
                return  # Exit if the selected rule has no recognizable features

            # Choose a feature to replace
            feature_to_replace = random.choice(features_in_rule)
            # Choose a new feature, ensuring it's different from the one to replace
            new_feature = random.choice([feat for feat in self.available_features if feat != feature_to_replace])

            # Replace the feature in the rule
            mutated_rule = original_rule.replace(feature_to_replace, new_feature)

            # Replace the mutated rule in the system
            self.replace_rule(rule_index, mutated_rule, verbose=True)

    def mutate_operator(self):
        """Selects a random rule, mutates it, and replaces the original with the new one."""
        current_rules = self.get_rules()  # Fetch current rules using the formatted get_rules
        if not current_rules:
            print("No rules available to mutate.")
            return  # Exit if there are no rules to mutate

        # Select a random rule to mutate
        rule_index = random.randint(0, len(current_rules) - 1)
        original_rule = current_rules[rule_index]

        # Mutate this selected rule
        mutated_rule = gp_utilities.mutate_logical_operator(original_rule)
        
        # Replace the mutated rule in the system
        self.replace_rule(rule_index, mutated_rule, verbose=True)

    def crossover(self, partner_system):
        """Performs crossover between this system and another, exchanging rules at potentially different indices."""
        if not self._rules or not partner_system._rules:
            print("No rules available to crossover.")
            return None, None

        # Randomly select a rule index from each system
        index_self = random.randint(0, len(self._rules) - 1)
        index_partner = random.randint(0, len(partner_system._rules) - 1)

        # Use clone to ensure that we're working with independent copies
        new_self = self.clone()
        new_partner = partner_system.clone()

        # Swap the rules at the selected indices
        new_self._rules[index_self], new_partner._rules[index_partner] = \
            new_partner._rules[index_partner], new_self._rules[index_self]

        return new_self, new_partner

    def evaluate_fitness(self, historical_data, predictions):
        """Calculates the fitness score based on a comparison metric like RMSE."""
        rmse = np.sqrt(np.mean((np.array(predictions) - np.array(historical_data)) ** 2))
        self.fitness_score = rmse
        return self.fitness_score

if __name__ == "__main__":
    pass



"""
Refined To-Do List for Future Enhancements:

1. Advanced Selection Mechanism:
   - Implement or integrate advanced selection mechanisms to evaluate and pick individuals according to fitness metrics such as precision, RMSE, or custom evaluation functions.

2. Crossover Operator for Rule Exchange:
   - Refine the crossover operator to efficiently exchange rules between individuals, considering rule compatibility and aiming to preserve or enhance rule effectiveness.

3. Dynamic Mutation of Rule Structure:
   - Expand mutation operations to allow for structural modifications of individuals, such as swapping variables within rules or changing the logical structure of conditions.

4. Feature Selection Through Genetic Programming:
   - Integrate mechanisms that implicitly perform feature selection during the evolutionary process, identifying and prioritizing the most informative variables for prediction.

5. Scalability and Efficiency Enhancements:
   - Assess and optimize the computational efficiency and scalability of the system, ensuring it can handle large datasets and complex rule sets.

6. Experimentation and Evaluation Framework:
    - Develop a comprehensive framework for testing and evaluating the evolved fuzzy systems across various datasets, focusing on generalization ability and predictive accuracy.

Each of these enhancements contributes directly to evolving fuzzy rule sets for data-driven solutions, aligning with the dissertation's objectives to address design problems through genetic programming. Focus on incremental development, ensuring each enhancement strengthens the system's ability to evolve and evaluate fuzzy rule sets effectively.
"""
