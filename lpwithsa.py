import pulp as pl
import random
import math
import time

# Parameters for simulated annealing
initial_temp = 5000000
cooling_rate = 0.99
max_iter = 1000
hess_cost = 1000000

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
initial_capacity = [0 for _ in range(n_cities + 1)]

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

def create_model(capacity):
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

    return model

def simulated_annealing(initial_capacity, initial_temp, cooling_rate, max_iter):
    current_capacity = initial_capacity[:]
    best_capacity = initial_capacity[:]
    
    def objective(capacity):
        model = create_model(capacity)
        model.solve()
        return pl.value(model.objective)
    
    current_cost = objective(current_capacity)
    best_cost = current_cost

    temperature = initial_temp
    
    added_cost = 0
    start_time = time.time()

    with open("lplog3.txt", "w") as log_file, open("lpresult2.txt", "w") as result_file:
        for iteration in range(max_iter):
            # Create a new candidate solution by modifying the current solution
            new_capacity = current_capacity[:]
            if iteration:
                city = random.randint(1, n_cities)
                current_addcost = added_cost
                if new_capacity[city] == 0:
                    new_capacity[city] = 50000
                    added_cost += hess_cost
                else:
                    new_capacity[city] = 0
                    added_cost -= hess_cost
            
            new_cost = objective(new_capacity) + added_cost
            
            # Calculate the acceptance probability
            delta_cost = new_cost - current_cost
            print(f"Delta Cost: {delta_cost}")
            print(math.exp(-delta_cost / temperature))
            print(random.random())
            if delta_cost < 0 or math.exp(-delta_cost / temperature) > random.random():
                current_capacity = new_capacity
                current_cost = new_cost
                
                # Update the best solution found so far
                if new_cost < best_cost:
                    best_capacity = new_capacity
                    best_cost = new_cost
            else:
                added_cost = current_addcost
            
            # Cool down the temperature
            temperature *= cooling_rate
            
            # Log the current state
            elapsed_time = time.time() - start_time
            log_entry = f"Iteration {iteration}, Temperature {temperature:.2f}, New Cost {new_cost}, Current Cost {current_cost:.2f}, Best Cost {best_cost:.2f}, Elapsed Time {elapsed_time:.2f} seconds\n"
            log_file.write(log_entry)
            print(log_entry)

            # if iteration >= 500:
            #     break
        
        # Write the best solution to the result file
        result_entry = f"Best Capacity: {best_capacity}\nBest Cost: {best_cost}\n"
        result_file.write(result_entry)
        print(result_entry)
        
        # Calculate the total basic cost
        total_basic_cost = cal_basic_cost()
        basic_cost_entry = f"Total Basic Cost: {total_basic_cost}\n"
        result_file.write(basic_cost_entry)
        print(basic_cost_entry)

        # Write the total execution time
        end_time = time.time()
        execution_time = end_time - start_time
        time_entry = f"Total Execution Time: {execution_time:.2f} seconds\n"
        result_file.write(time_entry)
        print(time_entry)


# Run simulated annealing
best_capacity, best_cost = simulated_annealing(initial_capacity, initial_temp, cooling_rate, max_iter)
