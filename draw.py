import matplotlib.pyplot as plt

# Read data from result2.txt
attempts = []
costs = []

with open('lplog3.txt', 'r') as file:
    attempt = 1
    for line in file:
        if line.startswith("Iteration"):
            parts = line.strip().split(',')
            for part in parts:
                if "New Cost" in part:
                    cost = float(part.split()[2])
                    costs.append(cost)
                    attempts.append(attempt)
                    attempt += 1
                    break
        if attempt > 500:
            break

# Calculate minimum costs up to each attempt
min_costs = [costs[0]]
for cost in costs[1:]:
    min_costs.append(min(min_costs[-1], cost))

# Plot: Cost vs Attempts
plt.figure(figsize=(10, 6))
plt.plot(attempts, costs, marker='o', linestyle='-', color='b', markersize=2)
plt.xlim(1, len(attempts))
plt.ylim(min(costs), max(costs))
plt.xlabel('Attempt')
plt.ylabel('Total Cost')
plt.title('Cost vs Attempts')
plt.grid(True)
plt.show()

# Plot: Minimum Cost vs Attempts
plt.figure(figsize=(10, 6))
plt.plot(attempts, min_costs, marker='o', linestyle='-', color='g', markersize=2)
plt.xlim(1, len(attempts))
plt.ylim(min(min_costs), max(min_costs))
plt.xlabel('Attempt')
plt.ylabel('Minimum Cost')
plt.title('Minimum Cost vs Attempts')
plt.grid(True)
plt.show()
