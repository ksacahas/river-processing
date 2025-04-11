def parse_list_of_strings(input_list):
    # This function takes a list of strings representing lists of integers,
    # removes the square brackets, splits the strings into individual components,
    # converts them to integers, and returns a list of lists of integers.
    result = []
    for item in input_list:
        # Remove brackets and split the string into numbers
        numbers = [int(num) for num in item.strip('[]').split()]
        # Append the list of numbers to the result
        result.append(numbers)
    return result
