
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
ColorPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ColorPrinters")
BWPrinters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BWPrinters")

# Set the variable ColorPrinters to be integer
ColorPrinters.vType = gp.GRB.INTEGER

# Adjust the variable BWPrinters for integer constraint
BWPrinters.vType = gp.GRB.INTEGER

# Ensure the number of color printers is non-negative
model.addConstr(ColorPrinters >= 0, name="color_printers_nonnegative")

# Add the constraint for the number of black and white printers to be non-negative
model.addConstr(BWPrinters >= 0, name="non_negative_BWPrinters")

# Add color printer production limit constraint
model.addConstr(ColorPrinters <= MaxColor, name="color_printer_production_limit")

# Add production limit constraint for black and white printers
model.addConstr(BWPrinters <= MaxBW, name="BW_printers_limit")

# Add maximum total printers production constraint
model.addConstr(ColorPrinters + BWPrinters <= MaxTotal, name="total_production")

# Add color printer production limit constraint
model.addConstr(ColorPrinters <= MaxColor, name="production_capacity")

# Add production capacity constraint for black and white printers
model.addConstr(BWPrinters <= MaxBW, name="BW_printers_capacity")

# Add printer capacity constraint
model.addConstr(ColorPrinters + BWPrinters <= MaxTotal, name="printer_capacity")

# Set objective
model.setObjective(ProfitColor * ColorPrinters + ProfitBW * BWPrinters, gp.GRB.MAXIMIZE)

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

