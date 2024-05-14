import re

def strip_parentheses(rule):
    # Remove all parentheses while preserving the characters inside them
    while '(' in rule or ')' in rule:
        rule = re.sub(r'\(([^()]*)\)', r'\1', rule)
    return rule

def find_clauses(rule):
    # Regex to find all occurrences of the pattern "word IS word"
    clauses = re.findall(r'\b(\w+)\s+IS\s+(\w+)\b', rule)
    return clauses

def reintroduce_parentheses(rule, clauses):
    for variable, value in clauses:
        # Replace each occurrence of the pattern with the same pattern encapsulated in parentheses
        pattern = f"{variable} IS {value}"
        rule = rule.replace(pattern, f"({pattern})")
    return rule

def handle_not_conditions(rule):
    # Ensure to capture "NOT" followed by a clause and wrap it correctly
    rule = re.sub(r'\bNOT\s+(\(\w+\s+IS\s+\w+\))', r'(NOT \1)', rule)
    return rule

def finalize_not_conditions(rule):
    # This function adjusts the spaces around 'NOT' conditions precisely.
    # Remove spaces between '(' and 'NOT', and ensure one space between 'NOT' and the following '('
    rule = re.sub(r'\s*\(\s*NOT\s+\(', '(NOT (', rule)

    # Correct spacing issues around other parts of conditions, like after logical operators before '('
    rule = re.sub(r'\b(AND|OR)\s*\(\s*', r'\1 (', rule)

    # Ensure there's no extra space before ')' and after '(' globally
    rule = re.sub(r'\(\s+', '(', rule)
    rule = re.sub(r'\s+\)', ')', rule)

    return rule


def format_rule(rule):
    print("Original:", rule)
    rule = strip_parentheses(rule)
    print("Stripped Parentheses:", rule)
    clauses = find_clauses(rule)
    rule = reintroduce_parentheses(rule, clauses)
    print("Parentheses Reintroduced:", rule)
    rule = handle_not_conditions(rule)
    print("Handled NOT Conditions:", rule)
    rule = finalize_not_conditions(rule)
    print("Finalized NOT Conditions:", rule)
    return rule
