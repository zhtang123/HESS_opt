import matplotlib.pyplot as plt

# Function to read data from cost flow result file
def read_cost_flow_data(filename):
    attempts = []
    costs = []
    times = []

    with open(filename, 'r') as file:
        for line in file:
            if 'Total Cost' in line:
                parts = line.strip().split(',')
                cost = float(parts[1].split(':')[1].strip())
                time_seconds = float(parts[2].split(':')[1].strip().split()[0])
                attempts.append(len(attempts) + 1)
                costs.append(cost)
                times.append(time_seconds)

    return attempts, costs, times

# Function to read data from pulp result file
def read_pulp_data(filename):
    attempts = []
    costs = []
    times = []

    with open(filename, 'r') as file:
        for line in file:
            if 'Best Cost' in line:
                parts = line.strip().split(',')
                cost = float(parts[3].split()[2].strip())
                time_seconds = float(parts[4].split()[2].strip())
                attempts.append(len(attempts) + 1)
                costs.append(cost)
                times.append(time_seconds)

    return attempts, costs, times

# Read data from result.txt (cost flow) and lplog2.txt (pulp)
attempts_cost_flow, costs_cost_flow, times_cost_flow = read_cost_flow_data('result.txt')
attempts_pulp, costs_pulp, times_pulp = read_pulp_data('lplog2.txt')

# Calculate minimum costs up to each attempt
min_costs_cost_flow = [costs_cost_flow[0]]
min_costs_pulp = [costs_pulp[0]]

for cost in costs_cost_flow[1:]:
    min_costs_cost_flow.append(min(min_costs_cost_flow[-1], cost))

for cost in costs_pulp[1:]:
    min_costs_pulp.append(min(min_costs_pulp[-1], cost))

# Plot: Minimum Cost vs Attempts
plt.figure(figsize=(10, 6))
plt.plot(attempts_cost_flow, min_costs_cost_flow, marker='o', linestyle='-', color='b', markersize=2, label='cost flow')
plt.plot(attempts_pulp, min_costs_pulp, marker='o', linestyle='-', color='g', markersize=2, label='pulp')
plt.xlim(1, max(len(attempts_cost_flow), len(attempts_pulp)))
plt.ylim(min(min(min_costs_cost_flow), min(min_costs_pulp)), max(max(min_costs_cost_flow), max(min_costs_pulp)))
plt.xlabel('Attempts')
plt.ylabel('Minimum Cost')
plt.title('Minimum Cost vs Attempts')
plt.legend()
plt.grid(True)
plt.show()

# Plot: Minimum Cost vs Time
plt.figure(figsize=(10, 6))
plt.plot(times_cost_flow, min_costs_cost_flow, marker='o', linestyle='-', color='b', markersize=2, label='cost flow')
plt.plot(times_pulp, min_costs_pulp, marker='o', linestyle='-', color='g', markersize=2, label='pulp')
plt.xlim(min(min(times_cost_flow), min(times_pulp)), max(max(times_cost_flow), max(times_pulp)))
plt.ylim(min(min(min_costs_cost_flow), min(min_costs_pulp)), max(max(min_costs_cost_flow), max(min_costs_pulp)))
plt.xlabel('Time (seconds)')
plt.ylabel('Minimum Cost')
plt.title('Minimum Cost vs Time')
plt.legend()
plt.grid(True)
plt.show()
