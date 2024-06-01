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
    for key in ["assignments", "total_cost"]:
        if key not in output:
            error_list.append(f"The output field '{key}' is missing")

    if not isinstance(output["assignments"], list):
        error_list.append("The output field 'selected_translators' should be a list")

    if not isinstance(output['total_cost'], (int, float)):
        error_list.append("The 'total_cost' should be a number.")

    for i, assignment in enumerate(output["assignments"]):
        for assign in assignment:
            if not isinstance(assign, int):
                error_list.append(f"{i+1}: Consultant assignment is not an integer. Value: {assign}")

    # Check if each consultant does not exceed max projects
    max_projects = data['max_projects_per_consultant']
    for j, assignment in enumerate(output['assignments']):
        if sum(assignment) > max_projects:
            error_list.append(f"Consultant {j+1} is assigned more than {max_projects} projects.")

    # Check if each project is assigned only once
    project_assignments = np.zeros(len(data['additional_costs']))
    for assignment in output['assignments']:
        for i, project in enumerate(assignment):
            project_assignments[i] += project

    for i, count in enumerate(project_assignments):
        if count < 1:
            error_list.append(f"Project {i+1} is not assigned.")
        if count > 1:
            error_list.append(f"Project {i+1} is assigned more than once.")

    # Check total_cost is correct
    total_cost = 0
    for j, assignment in enumerate(output['assignments']):
        if sum(assignment) > 0:
            total_cost += data['fixed_costs'][j]  # fixed cost for hiring consultant j
        for i, project in enumerate(assignment):
            if project > 0:
                total_cost += data['additional_costs'][i][j]  # additional cost for project

    if not np.isclose(total_cost, output['total_cost'], atol=eps):
        error_list.append(f"Total cost in the output is incorrect. Expected {total_cost}, but got {output['total_cost']}")
    return error_list


if __name__ == "__main__":
    print(run())
