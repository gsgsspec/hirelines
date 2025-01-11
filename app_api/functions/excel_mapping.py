import pandas as pd
import json
import re

# Function to read the JSON file
def read_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

# Function to read the Excel file
def read_excel(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

# Function to validate a column based on rules (accuracy as percentage)
def validate_column(values, rules):
    """Validates a column based on the provided rules, including optional accuracy percentage."""
    valid_count = 0
    total_count = 0

    # Get the accuracy percentage from the rules (if available), default to None
    accuracy_percentage = rules.get("accuracy", None)

    for index, value in values.items():
        if pd.isna(value):
            continue  # Skip empty values
        total_count += 1

        # Apply validation rules
        if "pattern" in rules:
            pattern = rules["pattern"]
            if not re.match(pattern, str(value)):
                continue  # Skip invalid value

        if "min_length" in rules and len(str(value)) < rules["min_length"]:
            continue
        if "max_length" in rules and len(str(value)) > rules["max_length"]:
            continue

        valid_count += 1

    if accuracy_percentage is not None and total_count > 0:
        required_valid_rows = (accuracy_percentage / 100) * total_count
        return valid_count >= required_valid_rows  # Return True if column meets the accuracy requirement
    else:
        return valid_count == total_count  # All values must be valid if no accuracy is specified

# Function to process the JSON mapping and validate the Excel data
def validate_excel_with_json(json_file_path, excel_file_path):
    # Step 1: Load JSON mappings
    json_data = read_json(json_file_path)
    if not json_data:
        return {}

    column_mappings = json_data.get("column_mappings", {})

    # Step 2: Load Excel data
    excel_data = read_excel(excel_file_path)
    if excel_data is None:
        return {}

    # Step 3: Process and generate JSON output
    output = {}

    for json_key, rules in column_mappings.items():
        validations = rules.get("validations", {})
        if not validations:
            output[json_key] = []  # No validations defined, return empty list
            continue

        matching_columns = []
        for column_index, column_name in enumerate(excel_data.columns):
            if validate_column(excel_data[column_name], validations):
                matching_columns.append(column_index)

        # If no matching columns, return an empty list for that key
        output[json_key] = matching_columns

    return output  # Return the JSON object directly

# # File paths stored in variables
# json_file_path = "mapping.json"  # Path to your JSON file
# excel_file_path = "candidate_upload_template.xlsx"  # Path to your Excel file

# # Example Usage
# result = validate_excel_with_json(json_file_path, excel_file_path)
# print(json.dumps(result, indent=4))
