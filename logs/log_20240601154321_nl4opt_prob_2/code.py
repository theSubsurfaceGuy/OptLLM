
import json
import numpy as np
import math

import gurobipy as gp

 # Define model
model = gp.Model('model')

with open("data/nl4opt/prob_2/data.json", "r") as f:
    data = json.load(f)


WageSenior = data["WageSenior"] # scalar parameter
WageJunior = data["WageJunior"] # scalar parameter
MinAccountants = data["MinAccountants"] # scalar parameter
MinSenior = data["MinSenior"] # scalar parameter
RatioSeniorJunior = data["RatioSeniorJunior"] # scalar parameter
MaxWageBill = data["MaxWageBill"] # scalar parameter
NumSenior = model.addVar(vtype=gp.GRB.INTEGER, name="NumSenior")
NumJunior = model.addVar(vtype=gp.GRB.INTEGER, name="NumJunior")

# No additional constraints needed as "NumSenior" is already defined as a non-negative integer variable

# Ensure the number of junior accountants is non-negative
model.addConstr(NumJunior >= 0, name="nonnegative_junior")

# Add constraint for minimum required number of accountants
model.addConstr((NumSenior + NumJunior) >= MinAccountants, name="min_accountants")

# Add the constraint for minimum number of senior accountants
model.addConstr(NumSenior >= MinSenior, name="min_senior_accountant")

# Add constraint: Number of senior accountants greater than or equal to RatioSeniorJunior times the number of junior accountants
model.addConstr(NumSenior >= RatioSeniorJunior * NumJunior, name="senior_to_junior_ratio")

# Add total weekly wage bill constraint
model.addConstr((WageSenior*NumSenior + WageJunior*NumJunior) <= MaxWageBill, name="total_wage_bill")

# No constraint needed as the variable NumSenior has already been defined 
# with the required properties (non-negative and integer) in its declaration.

# Add constraint for the minimum required number of accountants
model.addConstr((NumSenior + NumJunior) >= MinAccountants, name="min_accountants")

# Add the constraint for minimum number of senior accountants
model.addConstr(NumSenior >= MinSenior, name="min_senior_accountant")

# Add constraint for the ratio of senior to junior accountants
model.addConstr(NumSenior >= RatioSeniorJunior * NumJunior, name="senior_junior_ratio")

# Add wage bill constraint
model.addConstr((WageSenior * NumSenior + WageJunior * NumJunior) <= MaxWageBill, name="wage_bill_constraint")

# Set objective
model.setObjective((WageSenior * NumSenior) + (WageJunior * NumJunior), gp.GRB.MINIMIZE)

# Optimize model
model.optimize()



# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal

