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
    for key in ["visit_order", "total_distance"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output["visit_order"], list):
        error_list.append("The output field 'visit_order' should be a list")

    if not isinstance(output["total_distance"], (int, float)):
        error_list.append("The 'total_distance' should be a number.")

    # Check visit_order
    if (
        output["visit_order"][0] != data["start_city"]
        or output["visit_order"][-1] != data["start_city"]
    ):
        error_list.append(
            f"The visit order must start and end with the start city {data['start_city']}."
        )

    if len(set(output["visit_order"][1:-1])) != len(output["visit_order"]) - 2:
        error_list.append(
            "The visit order must include each city exactly once, excluding the start city."
        )

    # Check total_distance
    if output["total_distance"] < 0:
        error_list.append("Total distance cannot be negative.")

    total_distance = 0
    for i in range(len(output["visit_order"]) - 1):
        total_distance += data["distances"][output["visit_order"][i]][
            output["visit_order"][i + 1]
        ]
    if not np.isclose(total_distance, output["total_distance"], atol=eps):
        error_list.append(
            f"Total distance is incorrect. Calculated: {total_distance}, Reported: {output['total_distance']}."
        )

    # Check that all cities in visit_order are in the distances mapping
    for city in output["visit_order"]:
        if city not in data["distances"]:
            error_list.append(
                f"City {city} in visit order not found in distances mapping."
            )
    return error_list


if __name__ == "__main__":
    print(run())
