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
    for key in ["patterns", "total_large_rolls_used"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output['total_large_rolls_used'], (int, float)):
        error_list.append("The 'total_large_rolls_used' should be a number.")

    # Initialize a list to store the total produced rolls for each width
    total_produced = [0] * len(data["roll_width_options"])

    # Validate the patterns and amounts
    for pattern_info in output["patterns"]:
        pattern = pattern_info["pattern"]
        amount = pattern_info["amount"]

        # Check if the amount is non-negative
        if amount < -eps:
            error_list.append(f"Negative amount detected in pattern: {pattern}, Amount: {amount}")

        # Aggregate the total produced for each width
        for i, rolls in enumerate(pattern):
            total_produced[i] += rolls * amount

    # Check if all demanded roll widths are satisfied
    for i, demand in enumerate(data["demands"]):
        if not np.isclose(total_produced[i], demand, atol=eps):
            error_list.append(f"Demand for roll width {data['roll_width_options'][i]} inches not met. Required: {demand}, Produced: {total_produced[i]}")

    # Check if the total number of large rolls used is correctly calculated
    total_large_rolls_calculated = sum(pattern_info['amount'] for pattern_info in output["patterns"])
    if not np.isclose(total_large_rolls_calculated, output["total_large_rolls_used"], atol=eps):
        error_list.append(f"Total large rolls used is incorrect. Calculated: {total_large_rolls_calculated}, Reported: {output['total_large_rolls_used']}")
    return error_list


if __name__ == "__main__":
    print(run())
