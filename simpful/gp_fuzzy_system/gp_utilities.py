import numpy as np
import re
import random

def tournament_selection(population, fitness_scores, tournament_size=3):
    """Implements tournament selection."""
    selected = []
    for _ in range(len(population)):
        participants = np.random.choice(len(population), tournament_size, replace=False)
        best_participant = participants[np.argmax(fitness_scores[participants])]
        selected.append(population[best_participant])
    return selected

def roulette_wheel_selection(population, fitness_scores):
    """Implements roulette wheel selection."""
    fitness_sum = sum(fitness_scores)
    probability_distribution = [score / fitness_sum for score in fitness_scores]
    selected_indices = np.random.choice(len(population), size=len(population), p=probability_distribution)
    return [population[i] for i in selected_indices]

def find_logical_operators(sentence):
    pattern = r'\b(AND|OR|NOT)\b'
    matches = re.finditer(pattern, sentence, re.IGNORECASE)
    results = [{'operator': match.group(), 'index': match.start()} for match in matches]
    return results, len(results)

def choose_new_operator(old_operator, alternatives, context):
    if old_operator == 'NOT':
        # Removing NOT, ensure it's logical to do so
        return random.choice(list(alternatives - {'NOT'}))
    else:
        # If 'NOT' is in context, ensure its addition is logical
        if 'NOT' not in context:
            alternatives.add('NOT')
        return random.choice(list(alternatives))

def remove_not_parentheses(index, sentence, verbose):
    try:
        # Adjust to remove parentheses correctly around the condition `NOT` was negating
        start_paren = sentence.rindex('(', 0, index)
        end_paren = sentence.index(')', index + len('NOT'))
        mutated_sentence = sentence[:start_paren] + sentence[start_paren + 1:index] + sentence[index + len('NOT') + 1:end_paren] + sentence[end_paren + 1:]
    except ValueError:
        if verbose:
            print("Error removing parentheses for NOT operator.")
        mutated_sentence = sentence  # Return unchanged if parentheses can't be adjusted
    return mutated_sentence

def insert_not_operator(index, sentence, verbose):
    # Find the immediate next logical condition to apply "NOT"
    match = re.search(r'(\b\w+\b IS \b\w+\b)', sentence[index:])
    if match:
        condition_start = index + match.start()
        condition_end = condition_start + len(match.group(1))
        mutated_sentence = sentence[:condition_start] + 'NOT (' + match.group(1) + ')' + sentence[condition_end:]
        if verbose:
            print(f"Inserting NOT: Condition '{match.group(1)}' found at {condition_start}-{condition_end}, mutated to: {mutated_sentence}")
    else:
        mutated_sentence = sentence
        if verbose:
            print("No suitable condition found for NOT insertion after the operator.")
    return mutated_sentence

def remove_not_operator(index, sentence, verbose):
    try:
        start_paren = sentence.rindex('(', 0, index)
        end_paren = sentence.index(')', index)
        mutated_sentence = sentence[:start_paren] + sentence[start_paren + 1:index] + sentence[index + 4:end_paren] + sentence[end_paren + 1:]
        if verbose:
            print(f"Removed NOT: Adjusted from '{sentence[start_paren:end_paren+1]}' to '{mutated_sentence}'")
    except ValueError as e:
        mutated_sentence = sentence
        if verbose:
            print(f"Failed to remove NOT due to parsing error: {e}")
    return mutated_sentence

def adjust_not_operator(index, sentence, old_operator, new_operator, verbose):
    if old_operator == 'NOT' and new_operator == 'NOT':
        # Negating a negation essentially removes NOT
        if verbose:
            print(f"Negating a negation at index {index}, effectively removing NOT.")
        return remove_not_operator(index, sentence, verbose)
    elif old_operator == 'NOT':
        # Change from NOT to another operator (though this should be handled differently as NOT shouldn't convert directly to AND/OR)
        if verbose:
            print(f"Error: Incorrect use of adjust_not_operator to convert 'NOT' to '{new_operator}'.")
        return sentence  # Return unchanged as fallback for incorrect usage
    elif new_operator == 'NOT':
        # Insert NOT
        return insert_not_operator(index, sentence, verbose)
    else:
        # Standard operator replacement which should not happen via this function but handled in the main function
        if verbose:
            print("Error: adjust_not_operator called without NOT involved.")
        return sentence  # Return unchanged as a fallback


def mutate_logical_operator(sentence, verbose=True):
    operators, count = find_logical_operators(sentence)
    if count == 0:
        if verbose:
            print("No logical operators found to mutate.")
        return sentence  # No operators to mutate

    chosen = random.choice(operators)
    old_operator = chosen['operator'].upper()  # Normalize to upper case
    index = chosen['index']
    alternatives = {'AND', 'OR'}

    if old_operator == 'NOT':
        # Since 'NOT' is special, handle its removal or maintain as is
        new_operator = 'NOT'  # Simulate removal or modification scenario
    else:
        alternatives.discard(old_operator)  # Remove the current operator from possible choices
        if 'NOT' not in sentence[index - 4:index + 4]:  # Simple check around the operator position
            alternatives.add('NOT')
        new_operator = random.choice(list(alternatives))

    if verbose:
        print(f"Mutating operator: {old_operator} to {new_operator}")

    # Handle 'NOT' adjustments or standard operator replacement
    if 'NOT' in {old_operator, new_operator}:
        mutated_sentence = adjust_not_operator(index, sentence, old_operator, new_operator, verbose)
    else:
        # Direct replacement if not dealing with 'NOT'
        mutated_sentence = sentence[:index] + new_operator + sentence[index + len(old_operator):]

    if verbose:
        print(f"Original sentence: {sentence}")
        print(f"Mutated sentence: {mutated_sentence}")

    return mutated_sentence

def mutate_a_rule_in_list(rules):
    if not rules:
        return "No rules to mutate."
    # Select a random rule
    random_rule = random.choice(rules)
    # Mutate this rule
    mutated_rule = mutate_logical_operator(random_rule)
    return mutated_rule



# Example usage:
rules_list = [
    "IF (gdp_growth_annual_prcnt IS Low) AND (unemployment_rate_value IS High) THEN (PricePrediction IS PricePrediction)",
    "IF (trade_balance_value IS Low) OR (foreign_direct_investment_value IS Low) THEN (PricePrediction IS PricePrediction)"
]

# Call the function to mutate a rule
mutated_rule = mutate_a_rule_in_list(rules_list)
print("Original Rule:", rules_list[1])  # Choose the second rule as an example
print("Mutated Rule:", mutated_rule)

"""
To-Do List for Future Development of gp_utilities.py:

1. Enhance Selection Mechanisms:
   - Investigate and possibly implement more advanced selection mechanisms that better accommodate the diversity of solutions and the specific needs of evolving fuzzy systems. Consider adaptive selection strategies that can evolve over generations based on population dynamics.

2. Refine Crossover Operations:
   - Develop more sophisticated crossover mechanisms that can intelligently combine fuzzy rules from parents, taking into account the structure and semantics of the rules. Explore crossover strategies that can maintain or enhance the logical coherence of the rule sets.

3. Advance Mutation Strategies:
   - Implement a wider range of mutation strategies to effectively explore the solution space. This includes mutating not only the variables within rules but also the operators and the structure of the rules themselves. Consider adaptive mutation rates or context-sensitive mutations that respond to the current state of the evolutionary process.

4. Implement Rule Representation and Management:
   - Given the requirement for rules to contain an arbitrary number of variables connected by logic operators, ensure that the utilities support the creation, manipulation, and evaluation of such complex rule structures. This may involve developing a more flexible internal representation of rules within `EvolvableFuzzySystem`.

5. Data-Driven Fuzzy Set and Rule Generation:
   - Develop utilities for automatically generating fuzzy sets and rules based on data, as required by the project. This includes inferring optimal fuzzy sets and membership functions from data and creating initial rule sets that reflect data-driven insights.

6. Support for Takagi-Sugeno-Kang (TSK) Models:
   - Ensure that the utilities facilitate the evolution of fuzzy systems based on TSK models, particularly for applications involving regression-based outcomes. This might include specific crossover and mutation strategies tailored for TSK rule structures.

7. Feature Selection Through Genetic Programming:
   - Integrate feature selection mechanisms within the genetic programming process to identify and prioritize the most informative variables. This involves developing strategies to evaluate the utility of variables within the context of evolving fuzzy systems and adjusting the genetic operations to favor systems that make effective use of the most relevant variables.

8. Scalability and Computational Efficiency:
   - Continuously assess and enhance the scalability and computational efficiency of the genetic operations. Explore parallelization, optimization of genetic operations, and efficient data handling to accommodate large datasets and complex fuzzy system models.

9. Logging and Analysis Tools:
   - Develop comprehensive logging and analysis tools to monitor the progress of the genetic algorithm, analyze the evolution of fuzzy systems over generations, and extract insights into the efficacy of different genetic operations and strategies.

This to-do list sets the direction for enhancing and expanding the capabilities of the genetic programming utilities in `gp_utilities.py`, ensuring they align with the intricate requirements of evolving data-driven fuzzy systems for complex design problems.
"""
