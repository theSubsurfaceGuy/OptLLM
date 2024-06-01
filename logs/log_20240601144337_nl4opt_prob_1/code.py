
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
BlackWhitePrintersProduced = model.addVar(vtype=gp.GRB.INTEGER, name="BlackWhitePrintersProduced")

# Change the variable to be integer
ColorPrintersProduced.vtype = gp.GRB.INTEGER

# Add constraints for the number of color printers produced
model.addConstr(0 <= ColorPrintersProduced, name="MinColorPrinters")
model.addConstr(ColorPrintersProduced <= MaxColor, name="MaxColorPrinters")

# No further code is required, as the integer constraint is already included in the variable's definition

# Add constraint for restricting produced color printers to non-negative numbers
model.addConstr(ColorPrintersProduced >= 0, name="non_negativity_color_printers")

# Add constraint: Number of black and white printers is non-negative
model.addConstr(BlackWhitePrintersProduced >= 0, name="non_negative_printers")

# Add production limit constraint
model.addConstr(ColorPrintersProduced <= MaxColor, name="production_limit")

# Add Black and White printer production limit constraint
model.addConstr(BlackWhitePrintersProduced <= MaxBW, name="BW_printer_production_limit")

# Add constraint for maximum total printers that can be made per day
model.addConstr(ColorPrintersProduced + BlackWhitePrintersProduced <= MaxTotal, name="max_total_printers")

# Add constraint for maximum color printers produced per day
model.addConstr(ColorPrintersProduced <= MaxColor, name="max_color_printer_production")

# Add black and white printer production limit constraint
model.addConstr(BlackWhitePrintersProduced <= MaxBW, name="BW_Printer_Production_Limit")

# Add constraint for total number of printers produced
model.addConstr(ColorPrintersProduced + BlackWhitePrintersProduced <= MaxTotal, name="production_capacity")

# Set objective
model.setObjective(ProfitColor * ColorPrintersProduced + ProfitBW * BlackWhitePrintersProduced, gp.GRB.MAXIMIZE)

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

