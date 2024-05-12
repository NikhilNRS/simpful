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
    # This pattern looks for logical operators and considers the whole sentence structure.
    pattern = r'\b(AND|OR|NOT)\b'
    matches = re.finditer(pattern, sentence, re.IGNORECASE)
    results = [{'operator': match.group(), 'index': match.start()} for match in matches]
    return results, len(results)


def find_logical_operators(sentence):
    pattern = r'\b(AND|OR|NOT)\b'
    matches = re.finditer(pattern, sentence, re.IGNORECASE)
    results = [{'operator': match.group(), 'index': match.start()} for match in matches]
    return results, len(results)

def choose_new_operator(old_operator, sentence):
    alternatives = {'AND', 'OR'}
    if 'NOT' not in sentence:  # Allow adding NOT if it's not already in the rule
        alternatives.add('NOT')
    alternatives.discard(old_operator)
    return random.choice(list(alternatives))

def handle_not_operator(index, old_operator, new_operator, sentence, verbose):
    # We need to insert NOT directly before a condition with parentheses
    next_condition = re.search(r'\b\w+\b IS \b\w+\b', sentence[index + len(old_operator):])
    if next_condition:
        condition_start = next_condition.start()
        new_operator = 'NOT ('
        end_part = ')' + sentence[index + len(old_operator) + condition_start:]
        mutated_sentence = sentence[:index + len(old_operator) + condition_start] + new_operator + end_part
    else:
        if verbose:
            print("No valid condition found for NOT operator insertion.")
        mutated_sentence = sentence  # If no valid next condition, return the sentence unchanged
    return mutated_sentence

def remove_not_parentheses(index, old_operator, new_operator, sentence, verbose):
    try:
        open_paren_index = sentence.rindex('(', 0, index)
        close_paren_index = sentence.index(')', index)
        mutated_sentence = (sentence[:open_paren_index] +
                            sentence[open_paren_index+1:index] +
                            new_operator +
                            sentence[index+len(old_operator)+1:close_paren_index] +
                            sentence[close_paren_index+1:])
    except ValueError:
        if verbose:
            print("Error removing parentheses for NOT operator.")
        mutated_sentence = sentence
    return mutated_sentence

def mutate_logical_operator(sentence, verbose=True):
    operators, count = find_logical_operators(sentence)
    if count == 0:
        if verbose:
            print("No logical operators found to mutate.")
        return sentence  # No operators to mutate

    chosen = random.choice(operators)
    old_operator = chosen['operator'].upper()  # Normalize to upper case
    index = chosen['index']
    new_operator = choose_new_operator(old_operator, sentence)

    if verbose:
        print(f"Mutating operator: {old_operator} to {new_operator}")

    # Handling the insertion of NOT specifically to ensure correct syntax
    if new_operator == 'NOT':
        mutated_sentence = handle_not_operator(index, old_operator, new_operator, sentence, verbose)
    elif old_operator == 'NOT':
        mutated_sentence = remove_not_parentheses(index, old_operator, new_operator, sentence, verbose)
    else:
        end_part = sentence[index + len(old_operator):]
        mutated_sentence = sentence[:index] + new_operator + end_part

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
