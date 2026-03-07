def find_square(num):
    """Calculates and returns the square of a number."""
    result = num * num
    return result

def add_numbers(num1, num2):
    """Adds two numbers and returns the sum."""
    sum_result = num1 + num2
    return sum_result

def greet_with_default(name="Guest"):
    """Greets a person by name, or 'Guest' if no name is provided."""
    print(f"Welcome, {name}!")

# Call with an argument (overrides default)
greet_with_default("Alice")

# Call without an argument (uses default)
greet_with_default()


# Call the function with two values and print the result directly
total = add_numbers(5, 4)
print(f"The sum is: {total}")

