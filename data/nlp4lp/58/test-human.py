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
    for key in ["batches", "total_profit"]:
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

    if any(x < 0 for x in output["batches"]):
        error_list.append("All values in the 'batches' list should be non-negative")

    # Ensure at least the minimum required batches are produced
    for p, (produced, required) in enumerate(zip(np.array(output["batches"]), np.array(data["min_batches"]))):
        if required - produced > eps:
            error_list.append(
                f"The total batches for part {p+1} is less than the requirement"
            )

    # Ensure total profit is calculated correctly
    total_price = np.dot(
        np.array(data["prices"]).T, np.array(output["batches"])
    )
    # Calculate machine hours and labor cost
    total_cost = 0
    for m in range(len(data["machine_costs"])):
        machine_hours = sum(data["time_required"][m][p] * output["batches"][p] for p in range(len(data["prices"])))
        if m == 0:  # outsourced machine
            if machine_hours <= data["overtime_hour"] + eps:
                total_cost += machine_hours * data["standard_cost"]
            else:
                total_cost += data["overtime_hour"] * data["standard_cost"] + (machine_hours - data["overtime_hour"]) * data["overtime_cost"]
        else:
            if machine_hours > data["availability"][m] + eps:
                error_list.append(f"Total time used on machine {m+1} exceeds available time.")
        total_cost += machine_hours * data["machine_costs"][m]
    if (total_price - total_cost) - data["min_profit"] < -eps:
        error_list.append(
            f"Total profit {(total_price - total_cost)} is less than the requirement {output['min_profit']}"
        ) 
    if abs((total_price - total_cost) - output["total_profit"]) > eps:
        error_list.append(
            f"Total profit {(total_price - total_cost)} does not match the expected profit {output['total_profit']}"
        )
    return error_list


if __name__ == "__main__":
    print(run())
