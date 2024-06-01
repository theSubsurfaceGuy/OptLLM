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
    for key in ["paths", "total_time"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")
            
    # Check 2
    if "paths" in output and not all(isinstance(i, tuple) for i in output["paths"]):
        error_list.append("All entries in 'paths' should be tuples representing intersections.")

    # Check 3
    if output["paths"][0] != (1, 1):
        error_list.append("The path should start at the intersection of 1th Avenue and 1th Street.")

    # Check 4
    W, N = len(data["west_time"][0]) + 1, len(data["north_time"]) + 1
    if output["paths"][-1] != (N, W):
        error_list.append(f"The path should end at the intersection of {W}th Avenue and {N}th Street.")

    # Check 5 and 6
    total_time = 0
    for idx in range(1, len(output["paths"])):
        n1, w1 = output["paths"][idx-1]
        n2, w2 = output["paths"][idx]

        if n1 == n2:  # Moving west
            total_time += data["west_time"][int(n1)-1][int(w1)-1]
        elif w1 == w2:  # Moving north
            total_time += data["north_time"][int(n1)-1][int(w1)-1]
        else:
            error_list.append(f"Invalid move from {output['paths'][idx-1]} to {output['paths'][idx]}.")

    # Check 7
    if abs(total_time - output["total_time"]) > eps:
        error_list.append(f"Calculated total time ({total_time}) does not match provided total_time ({output['total_time']}).")

    # Check if "total_time" is negative
    if output["total_time"] < -eps:
        error_list.append("Total time cannot be negative.")

    return error_list


if __name__ == "__main__":
    print(run())
