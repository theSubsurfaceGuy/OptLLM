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
    for key in ["batches", "setup_flags", "total_profit"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output["batches"], list):
        error_list.append("The output field 'batches' should be a list")

    if not isinstance(output["total_profit"], (int, float)):
        error_list.append("The value of 'total_profit' is not a number")

    if len(output["batches"]) != len(data["prices"]):
        error_list.append(
            "The output field 'batches' should have the same length as the 'prices' list in the input"
        )

    for p, flag in enumerate(output["setup_flags"]):
        if flag not in [0, 1]:
            error_list.append(f"Invalid setup flag value for part {p+1}.")

    if any(x < 0 for x in output["batches"]):
        error_list.append("All values in the 'batches' list should be non-negative")

    # Ensure machine time does not exceed availability
    for m in range(len(data["availability"])):
        total_time = sum(data["time_required"][m][p] * output["batches"][p] for p in range(len(data["time_required"][m])))
        if m == 0:
            total_time += sum(data["setup_time"][p] * output["setup_flags"][p] for p in range(len(data["time_required"][m])))           
        if total_time - data["availability"][m] > eps:
            error_list.append(f"Total time used on machine {m+1} exceeds available time.")

    # Ensure setup constraints
    for p in range(len(data["prices"])):
        total_time = data["time_required"][0][p] * output["batches"][p]
        available = data["availability"][0] * output["setup_flags"][p]
        if total_time - available > eps:
            error_list.append(f"Total time used for part {p+1} on machine 1 exceeds available time.")

    # Ensure total profit is calculated correctly
    total_price = np.dot(
        np.array(data["prices"]).T, np.array(output["batches"])
    )
    total_cost = (
        np.array(data["machine_costs"]) @ data["time_required"] @ np.array(output["batches"]) 
    ) 
    # setup cost
    total_cost += sum(data["setup_time"][p] * output["setup_flags"][p] * data["machine_costs"][0] for p in range(len(data["time_required"][m])))
    if abs((total_price - total_cost) - output["total_profit"]) > eps:
        error_list.append(
            f"The total profit is not correctly calculated"
        )
    return error_list


if __name__ == "__main__":
    print(run())
