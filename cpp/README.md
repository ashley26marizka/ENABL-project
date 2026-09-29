# C++ Resource Utilization Calculator

A console application that calculates **resource utilization** and **estimated completion time** for a batch of scenario processing tasks.

## Formulas

```
total_capacity (tasks/hour) = resources × capacity_per_resource
completion_hours             = task_volume ÷ total_capacity
utilization_pct              = (task_volume ÷ total_capacity) × 100
```

If `utilization_pct > 100`, it is capped at 100% (meaning the job takes longer than one hour and all resources are fully occupied).

## Inputs

| Input | Description | Example |
|---|---|---|
| `task_volume` | Total number of scenarios to process | 500 |
| `resources` | Number of available workers/servers | 4 |
| `capacity_per_resource` | Tasks each worker can handle per hour | 50 |

## Compile

```bash
# Linux / macOS
g++ -std=c++17 -O2 -o calculator main.cpp

# Windows (MSVC)
cl /EHsc /std:c++17 main.cpp /Fe:calculator.exe

# Windows (MinGW)
g++ -std=c++17 -O2 -o calculator.exe main.cpp
```

## Run

```bash
./calculator        # Linux/macOS
calculator.exe      # Windows
```

## Sample Output

```
=== Resource Utilization & Completion Time Calculator ===

Enter total task volume (number of scenarios to process): 500
Enter number of available resources (workers/servers): 4
Enter processing capacity per resource (tasks/hour): 50

--- Results ---
Total capacity          : 200.00 tasks/hour
Estimated completion    : 2.50 hour(s) (150.00 minutes)
Resource utilization    : 100.00%
```

```
Enter total task volume: 80
Enter number of available resources: 4
Enter processing capacity per resource: 50

--- Results ---
Total capacity          : 200.00 tasks/hour
Estimated completion    : 0.40 hour(s) (24.00 minutes)
Resource utilization    : 40.00%
Note: Resources are under-utilized. Consider reducing workers.
```
