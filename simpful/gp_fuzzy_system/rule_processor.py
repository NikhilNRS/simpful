import re

class RuleProcessor:
    @staticmethod
    def format_rules(rules):
        formatted_rules = []
        pattern = r'^IF \(\((.*)\)\) THEN \((.*) IS (.*)\)$'
        for rule in rules:

            # Normalize the rule to ensure consistent spacing
            rule = re.sub(r'\s+\(', ' (', rule)  # Remove extra spaces before '('
            rule = re.sub(r'\)\s+', ') ', rule)  # Remove extra spaces after ')'
            rule = re.sub(r'NOT\s*\(', 'NOT (', rule)  # Correctly format 'NOT' with the following '('

            # Adjust the rule to remove any spaces directly before "NOT ("
            rule = re.sub(r'\(\s*NOT', '(NOT', rule)
            match = re.match(pattern, rule)
            if match:
                condition = match.group(1)
                consequence_variable = match.group(2)
                consequence_value = match.group(3)
                formatted_rule = f"IF ({condition}) THEN ({consequence_variable} IS {consequence_value})"
                formatted_rules.append(formatted_rule)
            else:
                formatted_rules.append(rule)  # Append original for review if no match

        return formatted_rules
