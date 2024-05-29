import pulp as pl

# Function to read data from the generated_data.txt file
def read_data(filename):
    with open(filename, 'r') as file:
        data = file.readlines()

    n = int(data[0].split()[1])
    max_demand = int(data[1].split()[1])
    max_price = int(data[2].split()[1])
    min_price = int(data[3].split()[1])
    max_transmission_cost = int(data[4].split()[1])

    demand = {}
    price = {}
    transmission_cost = {}

    demand_lines = data[6:6 + n]
    price_lines = data[7 + n:7 + 2 * n]
    transmission_cost_lines = data[8 + 2 * n:]

    for i in range(1, n + 1):
        for j in range(24):
            demand[(i, j)] = int(demand_lines[i - 1].split()[j])
            price[(i, j)] = int(price_lines[i - 1].split()[j])

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            transmission_cost[(i, j)] = int(transmission_cost_lines[i - 1].split()[j - 1])

    return n, max_demand, max_price, min_price, max_transmission_cost, demand, price, transmission_cost

# Read data from the file
filename = 'generated_data.txt'
n_cities, max_demand, max_price, min_price, max_transmission_cost, demand, cost_electricity, cost_transmission = read_data(filename)

hours = 24
capacity = [0 for _ in range(n_cities + 1)]
capacity[1] = 50000 
capacity[4] = 50000
capacity[8] = 50000

def cal_hour_cost(hour):
    sum_cost = 0
    for i in range(1, n_cities + 1):
        sum_cost += demand[(i, hour)] * cost_electricity[(i, hour)]
    return sum_cost

def cal_basic_cost():
    sum_cost = 0
    for i in range(1, n_cities + 1):
        for j in range(hours):
            sum_cost += demand[(i, j)] * cost_electricity[(i, j)]
    return sum_cost

# Create the LP model
model = pl.LpProblem("Power_System_Optimization", pl.LpMinimize)

# Decision variables
transmission = pl.LpVariable.dicts("transmission", ((i, j, k) for i in range(1, n_cities + 1) for j in range(1, n_cities + 1) for k in range(hours)), lowBound=0, cat='Continuous')
purchase = pl.LpVariable.dicts("purchase", ((i, k) for i in range(1, n_cities + 1) for k in range(hours)), lowBound=0)
remaining_energy = pl.LpVariable.dicts("remaining_energy", ((i, k) for i in range(1, n_cities + 1) for k in range(hours)), lowBound=0)

# Objective function (cost minimization)
model += pl.lpSum([purchase[(i, k)] * cost_electricity[(i, k)] + 
                   sum(transmission[(i, j, k)] * cost_transmission[(i, j)] for j in range(1, n_cities + 1) if i != j)
                   for i in range(1, n_cities + 1) for k in range(hours)])

# Constraints
for i in range(1, n_cities + 1):
    for k in range(hours):
        # Meet electricity demand
        if k > 0:
            model += pl.lpSum([transmission[j, i, k] for j in range(1, n_cities + 1)]) + purchase[i, k] - pl.lpSum([transmission[i, j, k] for j in range(1, n_cities + 1)]) == demand[(i, k)] + remaining_energy[(i, k)] - remaining_energy[(i, k-1)]
        else:
            model += pl.lpSum([transmission[j, i, k] for j in range(1, n_cities + 1)]) + purchase[i, k] - pl.lpSum([transmission[i, j, k] for j in range(1, n_cities + 1)]) == demand[(i, k)] + remaining_energy[(i, k)]

        # Manage energy storage
        if k > 0:
            model += pl.lpSum([transmission[i, j, k] for j in range(1, n_cities + 1)]) <= remaining_energy[(i, k-1)]
        else:
            model += pl.lpSum([transmission[i, j, k] for j in range(1, n_cities + 1)]) == 0

        # Capacity limit of energy storage
        model += remaining_energy[(i, k)] <= capacity[i]

# Solve the problem
model.solve()

# Print the solution
for v in model.variables():
    print(f"{v.name} = {v.varValue}")

# Solution status
print(f"Status: {pl.LpStatus[model.status]}")

# Objective value
print(f"Objective value: {pl.value(model.objective)}")

# Calculate the total basic cost
total_basic_cost = cal_basic_cost()
print(f"Total Basic Cost: {total_basic_cost}")
