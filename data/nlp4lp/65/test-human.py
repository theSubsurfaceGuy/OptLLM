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
    for key in ["interventions", "total_cost"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output["interventions"], list):
        error_list.append("The output field 'interventions' should be a list")

    if not isinstance(output['total_cost'], (int, float)):
        error_list.append("The 'total_cost' should be a number.")

    central_used = 0
    distributed_used = 0
    calculated_total_cost = 0

    for cluster_intervention in output['interventions']:
        i = cluster_intervention['cluster_id']
        amount = cluster_intervention['amount']
        intervention_type = cluster_intervention['type']
        method = cluster_intervention['method']

        if intervention_type not in ['isolate', 'scan']:
            error_list.append(f"Invalid intervention type '{intervention_type}' for cluster {i}.")

        if method not in ['central', 'distributed']:
            error_list.append(f"Invalid processing method '{method}' for cluster {i}.")

        cost_per_hour = data['costs'][method]
        cost = amount * cost_per_hour
        calculated_total_cost += cost

        if method == 'central':
            central_used += amount
        else:
            distributed_used += amount

    if central_used > data['max_hours']['central_max_hours'] + eps:
        error_list.append(f"Central processing time exceeded: {central_used} > {data['max_hours']['central_max_hours']}")

    if distributed_used > data['max_hours']['distributed_max_hours'] + eps:
        error_list.append(f"Distributed processing time exceeded: {distributed_used} > {data['max_hours']['distributed_max_hours']}")

    if not np.isclose(calculated_total_cost, output['total_cost'], atol=eps):
        error_list.append(f"Total cost mismatch: calculated {calculated_total_cost}, reported {output['total_cost']}")
    return error_list


if __name__ == "__main__":
    print(run())
