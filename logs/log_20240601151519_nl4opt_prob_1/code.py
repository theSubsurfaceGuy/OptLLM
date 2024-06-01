
import json
import numpy as np
import math

import gurobipy as gp

 # Define model
model = gp.Model('model')

with open("data/nl4opt/prob_1/data.json", "r") as f:
    data = json.load(f)


MaxColor = data["MaxColor"] # scalar parameter
MaxBW = data["MaxBW"] # scalar parameter
MaxTotal = data["MaxTotal"] # scalar parameter
ProfitColor = data["ProfitColor"] # scalar parameter
ProfitBW = data["ProfitBW"] # scalar parameter
ColorPrintersProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ColorPrintersProduced")
BWPrintersProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BWPrintersProduced")

# Change the variable to be integer
ColorPrintersProduced.vtype = gp.GRB.INTEGER

# Add constraints for the number of color printers produced
model.addConstr(0 <= ColorPrintersProduced, name="MinColorPrinters")
model.addConstr(ColorPrintersProduced <= MaxColor, name="MaxColorPrinters")

# Change the type of the variable to integer to satisfy the integer constraint
BWPrintersProduced.vtype = gp.GRB.INTEGER

# Add constraint for the number of black and white printers produced 
model.addConstr(0 <= BWPrintersProduced, "BW_Printers_Produced_Lower_Bound")
model.addConstr(BWPrintersProduced <= MaxBW, "BW_Printers_Produced_Upper_Bound")

# Add constraint for restricting produced color printers to non-negative numbers
model.addConstr(ColorPrintersProduced >= 0, name="non_negativity_color_printers")

# Add non-negativity constraint for number of black and white printers produced
model.addConstr(BWPrintersProduced >= 0, name="nonnegative_BWPrinters")

# Add production limit constraint
model.addConstr(ColorPrintersProduced <= MaxColor, name="production_limit")

# Add constraint for maximum black and white printers produced per day
model.addConstr(BWPrintersProduced <= MaxBW, name="max_BWPrinters")

# Add a constraint for maximum total number of printers produced per day
model.addConstr(ColorPrintersProduced + BWPrintersProduced <= MaxTotal, name="max_total_production")

# Add color printer production capacity constraint
model.addConstr(ColorPrintersProduced <= MaxColor, name="color_printer_capacity")

# Add black and white printers production capacity constraint
model.addConstr(BWPrintersProduced <= MaxBW, name="bw_printers_capacity")

# Add constraint for maximum number of printers adapted by the machine per day
model.addConstr(ColorPrintersProduced + BWPrintersProduced <= MaxTotal, name="max_capacity")

# Set objective
model.setObjective(ProfitColor * ColorPrintersProduced + ProfitBW * BWPrintersProduced, gp.GRB.MAXIMIZE)

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

