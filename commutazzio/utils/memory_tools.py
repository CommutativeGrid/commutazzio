from pympler import asizeof

def print_memory_usage():
    # Print sizes of variables of interest
    print(f"Size of variable 'a': {asizeof.asizeof(a) / (1024 * 1024):.2f} MB")
    # ... any other variables you want to monitor


def print_memory_usage_of_all_variables(scope=globals()):
    for name, value in scope.items():
        # Filter out built-in and imported modules/functions
        if not name.startswith("__") and not callable(value):
            memory_usage = asizeof.asizeof(value) / (1024 * 1024)  # Convert to MB
            print(f"Memory usage of variable '{name}': {memory_usage:.2f} MB")
