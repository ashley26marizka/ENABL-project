#include <iostream>
#include <iomanip>
#include <stdexcept>

/*
 * Resource Utilization & Completion Time Calculator
 *
 * Formulas:
 *   total_capacity (tasks/hour) = resources * capacity_per_resource
 *   completion_hours             = task_volume / total_capacity
 *   utilization_pct              = (task_volume / (total_capacity * completion_hours)) * 100
 *                                = 100% when fully loaded (by definition)
 *
 * When task_volume < total_capacity the job finishes in under 1 hour and
 * utilization reflects the fraction of capacity actually used.
 *
 *   utilization_pct = (task_volume / total_capacity) * 100
 */

struct Input {
    double task_volume;
    double resources;
    double capacity_per_resource;
};

Input prompt_user() {
    Input in{};
    std::cout << "=== Resource Utilization & Completion Time Calculator ===\n\n";

    std::cout << "Enter total task volume (number of scenarios to process): ";
    std::cin >> in.task_volume;
    if (in.task_volume <= 0) throw std::invalid_argument("Task volume must be positive");

    std::cout << "Enter number of available resources (workers/servers): ";
    std::cin >> in.resources;
    if (in.resources <= 0) throw std::invalid_argument("Resources must be positive");

    std::cout << "Enter processing capacity per resource (tasks/hour): ";
    std::cin >> in.capacity_per_resource;
    if (in.capacity_per_resource <= 0) throw std::invalid_argument("Capacity per resource must be positive");

    return in;
}

int main() {
    try {
        Input in = prompt_user();

        double total_capacity    = in.resources * in.capacity_per_resource;
        double completion_hours  = in.task_volume / total_capacity;
        double completion_mins   = completion_hours * 60.0;
        double utilization_pct   = (in.task_volume / total_capacity) * 100.0;
        if (utilization_pct > 100.0) utilization_pct = 100.0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "\n--- Results ---\n";
        std::cout << "Total capacity          : " << total_capacity   << " tasks/hour\n";
        std::cout << "Estimated completion    : " << completion_hours << " hour(s) ("
                  << completion_mins << " minutes)\n";
        std::cout << "Resource utilization    : " << utilization_pct  << "%\n";

        if (utilization_pct < 50.0)
            std::cout << "Note: Resources are under-utilized. Consider reducing workers.\n";
        else if (utilization_pct > 90.0)
            std::cout << "Note: Resources are near full capacity. Consider adding workers.\n";

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
