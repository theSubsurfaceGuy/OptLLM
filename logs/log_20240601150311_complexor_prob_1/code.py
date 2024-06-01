
import json
import numpy as np
import math

import gurobipy as gp

 # Define model
model = gp.Model('model')

with open("data/complexor/prob_1/data.json", "r") as f:
    data = json.load(f)


CustomerCount = data["CustomerCount"] # scalar parameter
VehicleCount = data["VehicleCount"] # scalar parameter
CustomerDemand = np.array(data["CustomerDemand"]) # ['CustomerCount']
CustomerLBTW = np.array(data["CustomerLBTW"]) # ['CustomerCount']
CustomerUBTW = np.array(data["CustomerUBTW"]) # ['CustomerCount']
CustomerDistance = np.array(data["CustomerDistance"]) # ['CustomerCount', 'CustomerCount']
CustomerServiceTime = np.array(data["CustomerServiceTime"]) # ['CustomerCount']
VehicleCapacity = np.array(data["VehicleCapacity"]) # ['VehicleCount']
Load = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.CONTINUOUS, name="Load")
X = model.addVars(VehicleCount, CustomerCount, CustomerCount, vtype=gp.GRB.BINARY, name="X")
CumulativeTravelTime = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.CONTINUOUS, name="CumulativeTravelTime")
VehicleVisitCustomer = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.BINARY, name="VehicleVisitCustomer")

# Add vehicle capacity constraints
for i in range(VehicleCount):
    for j in range(CustomerCount):
        model.addConstr(Load[i, j] <= VehicleCapacity[i], name=f"vehicle_capacity_{i}_{j}")

# Add constraints for customer service within time window
for i in range(VehicleCount):
    for j in range(CustomerCount):
        model.addConstr(CumulativeTravelTime[i, j] >= CustomerLBTW[j], name="service_time_lb_"+str(i)+"_"+str(j))
        model.addConstr(CumulativeTravelTime[i, j] <= CustomerUBTW[j] * VehicleVisitCustomer[i, j], name="service_time_ub_"+str(i)+"_"+str(j))

# Add vehicle availability constraints
for i in range(VehicleCount):
    model.addConstr(sum(VehicleVisitCustomer[i, j] for j in range(CustomerCount)) <= VehicleCount, name="vehicle_availability")

# Add load computation constraints
for i in range(VehicleCount):
    for j in range(CustomerCount):
        for k in range(CustomerCount):
            model.addConstr((Load[i, j] >= Load[i, k] + CustomerDemand[j] - VehicleCapacity[i] * (1 - X[i, j, k])), name="load_computation")

# Add initial load condition constraints
for i in range(VehicleCount):
    model.addConstr(Load[i, 0] == 0, name="initial_load")

# Add Vehicle visit customer constraints
for i in range(VehicleCount):
    for j in range(CustomerCount):
        model.addConstr(gp.quicksum(X[i, j, k] for k in range(CustomerCount) if k!=j) == VehicleVisitCustomer[i, j], name="vehicle_visit_customer")

# Add vehicle capacity constraints
for i in range(VehicleCount):
    model.addConstr(gp.quicksum(Load[i, j] for j in range(CustomerCount)) <= VehicleCapacity[i], name="vehicle_capacity")

# Add a constraint to ensure that each customer is served by exactly one vehicle
for j in range(CustomerCount):
    model.addConstr(gp.quicksum(VehicleVisitCustomer[i, j] for i in range(VehicleCount)) == 1, name="one_vehicle_per_customer")

# Add time window constraints
for i in range(VehicleCount):
    for j in range(CustomerCount):
        model.addConstr(CumulativeTravelTime[i, j] >= CustomerLBTW[j], name=f"lower_time_window_{i}_{j}")
        model.addConstr(CumulativeTravelTime[i, j] <= CustomerUBTW[j], name=f"upper_time_window_{i}_{j}")

# Add vehicle direct travel constraints
for i in range(VehicleCount):
    for j in range(CustomerCount):
        for k in range(CustomerCount):
            model.addConstr(X[i, j, k] <= VehicleVisitCustomer[i, j], name="direct_travel")

# Set objective
model.setObjective(gp.quicksum(X[i, j, k] * CustomerDistance[j, k] for i in range(VehicleCount) for j in range(CustomerCount) for k in range(CustomerCount)) 
                   + gp.quicksum(CumulativeTravelTime[i, j] for i in range(VehicleCount) for j in range(CustomerCount)), gp.GRB.MINIMIZE)

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

