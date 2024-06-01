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
    for key in ["containers_unloaded", "cranes_rented", "total_cost"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    for key in ["containers_unloaded", "cranes_rented"]:
        if not isinstance(output[key], list):
            error_list.append(f"The output field '{key}' should be a list")
        if len(output[key]) != len(data["demands"]):
            error_list.append(
                f"The output field '{key}' should have the same length as the 'demands' list in the input"
            )

    if any(x < 0 for x in output["containers_unloaded"]):
        error_list.append("All values in the 'containers_unloaded' list should be non-negative")

    cranes_rented = output["cranes_rented"]
    for t, crane in enumerate(cranes_rented):
        if not isinstance(crane, int):
            error_list.append(f"Month {t+1}: Cranes rented is not an integer. Value: {crane}")

    # Check if unloaded containers do not exceed monthly unloading capacity
    containers = output["containers_unloaded"]
    capacities = data["unload_capacity"]
    for t, (amount, cap) in enumerate(zip(containers, capacities)):
        if amount - cap > eps:
            error_list.append(f"Month {t+1}: Containers unloaded exceed capacity. Unloaded: {amount}, Capacity: {cap}")

    # Check if containers in yard do not exceed storage capacity
    max_storage = data["max_container"]
    demands = data["demands"]
    current_storage = data["init_container"]
    for t, (demand, amount) in enumerate(zip(demands, containers)):
        current_storage += amount - demand
        if current_storage - max_storage > eps:
            error_list.append(f"Month {t+1}: Containers in yard exceed max storage. In yard: {current_storage}, Max storage: {max_storage}")

    # Check if cranes rented do not exceed maximum
    max_cranes = data["num_cranes"]
    for t, crane in enumerate(cranes_rented):
        if crane - max_cranes > eps:
            error_list.append(f"Month {t+1}: Cranes rented exceed max allowed. Rented: {crane}, Max allowed: {max_cranes}")

    # Check if yard is empty at the end of the last month
    if current_storage > eps:
        error_list.append(f"At the end of last month, yard is not empty. Containers left: {current_storage}")

    # Check total cost computation
    holding_costs = data["holding_cost"]
    unload_costs = data["unload_costs"]
    computed_cost = 0
    current_storage = data["init_container"]
    for t, (amount, u_cost) in enumerate(zip(containers, unload_costs)):
        current_storage += amount - demands[t]
        computed_cost += amount * u_cost + current_storage * holding_costs
    computed_cost += sum(cranes_rented) * data["crane_cost"]
    if abs(computed_cost - output["total_cost"]) > eps:
        error_list.append(f"Total cost in output doesn't match computed cost. Output: {output['total_cost']}, Computed: {computed_cost}")
    return error_list


if __name__ == "__main__":
    print(run())
