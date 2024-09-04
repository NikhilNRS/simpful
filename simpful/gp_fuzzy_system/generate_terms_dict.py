import openai
import pandas as pd
import argparse
import re
import os


def construct_prompt(column_name, stats):
    prompt = f"""
You are an expert in fuzzy logic systems. Based on the following statistics for the column '{column_name}':
Min: {stats['min']}
Max: {stats['max']}
Mean: {stats['mean']}
Std: {stats['std']}

Suggest appropriate fuzzy terms for this column in the format of a Python list, adhering to a Likert scale. Use terms like "VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH". If the data suggests a constant or negligible change, suggest "CONSTANT". Consider using 1, 3, 4, or 5 terms based on the data distribution. Ensure the terms are ordered from smallest to largest.
"""
    return prompt


def extract_terms(response_text):
    try:
        match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if match:
            terms_str = match.group(0)
            terms = eval(terms_str)
            return [term.upper() for term in terms]
    except Exception as e:
        print(f"Error extracting terms: {e}")
    return []


def query_gpt_for_terms(column_name, stats, verbose=False):
    prompt = construct_prompt(column_name, stats)
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=prompt,
        max_tokens=200,
        temperature=0.5
    )

    response_text = response.choices[0].text.strip()
    if verbose:
        print(f"GPT-3.5-turbo-instruct-0914 suggested terms for '{column_name}': {response_text}")
    
    terms = extract_terms(response_text)
    return terms


def analyze_data_and_generate_terms(data, exclude_columns=None, verbose=False):
    skip_columns = {'year', 'month', 'day', 'hour'}
    if exclude_columns:
        skip_columns.update(map(str.lower, exclude_columns))

    terms_dict = {}
    term_order = {"CONSTANT": 0, "VERY_LOW": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4, "VERY_HIGH": 5}
    
    for column in data.columns:
        if column.lower() in skip_columns:
            continue

        if data[column].dtype in [float, int]:
            stats = {
                'min': data[column].min(),
                'max': data[column].max(),
                'mean': data[column].mean(),
                'std': data[column].std()
            }
            terms = query_gpt_for_terms(column, stats, verbose)
            
            if "CONSTANT" in terms and len(set(terms)) == 1:
                terms = ["CONSTANT"]
            else:
                valid_likert_terms = {"VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"}
                terms = [term for term in terms if term in valid_likert_terms]
                terms = list(dict.fromkeys(terms))

                if not terms:
                    terms = ["CONSTANT"]
                else:
                    terms.sort(key=lambda term: term_order[term])

            terms_dict[column] = terms

    return terms_dict


def generate_terms_dict(file_path, api_key, exclude_columns=None, verbose=False):
    openai.api_key = api_key
    data = pd.read_csv(file_path)
    
    terms_dict = analyze_data_and_generate_terms(data, exclude_columns, verbose)
    
    with open("terms_dict.py", "w") as f:
        f.write("terms_dict = {\n")
        for column, terms in terms_dict.items():
            f.write(f"    '{column}': {terms},\n")
        f.write("}\n")
    
    return terms_dict


def read_exclude_columns_from_file(file_path):
    """Helper function to read column names to exclude from a file."""
    try:
        with open(file_path, 'r') as file:
            exclude_columns = file.read().split(',')
            return [col.strip() for col in exclude_columns if col.strip()]
    except Exception as e:
        print(f"Error reading exclude columns file: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Generate terms dictionary for a dataset using GPT-3.5-turbo-instruct-0914 based on data analysis.")
    parser.add_argument("file_path", type=str, help="Path to the CSV file containing the dataset.")
    parser.add_argument("api_key", type=str, help="OpenAI API key.")
    parser.add_argument("-e", "--exclude_columns", nargs='+', help="List of columns to exclude from processing or a path to a comma-separated file with column names.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    
    args = parser.parse_args()

    exclude_columns = args.exclude_columns
    if exclude_columns and len(exclude_columns) == 1 and os.path.isfile(exclude_columns[0]):
        # If a single argument is provided and it's a file, read exclude columns from file
        exclude_columns = read_exclude_columns_from_file(exclude_columns[0])
    
    terms_dict = generate_terms_dict(args.file_path, args.api_key, exclude_columns, args.verbose)

    if args.verbose:
        print("Generated terms dictionary:")
        for column, terms in terms_dict.items():
            print(f"'{column}': {terms}")

if __name__ == "__main__":
    main()
