import json
import numpy as np

eps = 1e-03


def parse_json(json_file, keys):
    if isinstance(json_file, list):
        for v in json_file:
            parse_json(v, keys)
    elif isinstance(json_file, dict):
        for k, v in json_file.items():
            if isinstance(v, dict) or isinstance(v, list):
                parse_json(v, keys)
            if k not in keys:
                keys.append(k)


def run():
    with open("data.json", "r") as f:
        data = json.load(f)

    with open("output.json", "r") as f:
        output = json.load(f)

    all_json_keys = []
    parse_json(output, all_json_keys)

    error_list = []

    # Check if all the required keys are present in the output.
    for key in ["selected_translators", "total_cost"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output["selected_translators"], list):
        error_list.append("The output field 'selected_translators' should be a list")

    valid_ids = [translator['id'] for translator in data['translators']]
    for translator_id in output['selected_translators']:
        if translator_id not in valid_ids:
            error_list.append("Output contains invalid translator IDs.")

    covered_languages = set()
    for translator_id in output['selected_translators']:
        translator = next((t for t in data['translators'] if t['id'] == translator_id), None)
        if translator:
            covered_languages.update(translator['languages'])
    if not covered_languages.issuperset(data['required_languages']):
        error_list.append("Not all required languages are covered by the selected translators.")

    calculated_cost = sum(translator['cost'] for translator in data['translators'] if translator['id'] in output['selected_translators'])
    if np.abs(calculated_cost - output['total_cost']) > eps:
        error_list.append(f"Incorrect total cost. Expected: {calculated_cost}, Found: {output['total_cost']}")
    return error_list


if __name__ == "__main__":
    print(run())
