TEMPLATE_C= '''

    Given an example input and output dataset, learn how the transformation performed from the provided input dataset to the output dataset. 
        
    Pay attention to the size difference between the input and output dataset. Please make sure to print the output of the function.
    
    Generate python function with no explanations needed. 

    Please make sure to print the output of the function, print(output), no need to print row by row.
    Include test_list as the function input! Do not include the original input_list or output_list directly in the code.

    input dataset: {input_list}
    output dataset: {output_list}
    test set: {test_list}
    
    '''
TEMPLATE_WITH_FUNC = '''
    Given an example input and output dataset, learn the transformations applied to convert the input dataset into the output dataset. 
    These transformations may involve various data cleaning and wrangling tasks that standardize and prepare the data for analysis. 
    Here are some common transformations to consider, along with examples where appropriate, some sample reference functions are provided but you are not limited or have to use the provided functions:

    # Combine the first two rows into one by concatenation
    def combine_first_two_rows(data):
        """
        Combines the first two rows in a 2D list by concatenating them.
        Returns a new 2D list with the combined row.
        """
        if len(data) < 2:
            raise ValueError("Not enough rows to combine.")
        new_row = data[0] + data[1]
        new_data = [new_row] + data[2:]
        return new_data

    # Flip the first row and the leftmost column
    def flip_first_row_and_leftmost_col(data):
        """
        Flips the first row and the leftmost column in a 2D list.
        Returns a new 2D list with the flipped values.
        """
        if not data or not data[0]:
            return data
        num_rows = len(data)
        num_cols = len(data[0])

        # Extract first row and leftmost column
        first_row = data[0]
        leftmost_col = [data[i][0] for i in range(num_rows)]

        # Swap the values
        new_data = [[data[i][j] for j in range(num_cols)] for i in range(num_rows)]
        new_data[0] = leftmost_col
        for i in range(num_rows):
            new_data[i][0] = first_row[i] if i < len(first_row) else None  # Handle any length mismatch

        return new_data

    # Transpose the 2D list
    def transpose(data):
        """
        Transposes a 2D list, flipping rows and columns.
        """
        return [list(row) for row in zip(*data)]

    # Rotate the 2D list 90 degrees clockwise
    def rotate_90_clockwise(data):
        """
        Rotates the 2D list 90 degrees clockwise.
        """
        return [list(row) for row in zip(*data[::-1])]

    # Swap the first two columns
    def swap_first_two_columns(data):
        """
        Swaps the first two columns in a 2D list.
        """
        if len(data[0]) < 2:
            raise ValueError("Not enough columns to swap.")
        return [[row[1], row[0]] + row[2:] for row in data]

    # Add the first two rows element-wise
    def add_first_two_rows(data):
        """
        Adds the first two rows element-wise in a 2D list.
        Returns a new row and a modified 2D list.
        """
        if len(data) < 2:
            raise ValueError("Not enough rows to add.")
        new_row = [data[0][i] + data[1][i] for i in range(len(data[0]))]
        new_data = [new_row] + data[2:]
        return new_data

    # Remove duplicate elements in each row of the 2D list
    def remove_duplicates(data):
        """
        Removes duplicate elements in each row of a 2D list.
        Returns a new 2D list with duplicates removed, preserving the original order.
        """
        return [list(dict.fromkeys(row)) for row in data]


    Based on these transformations, generate a Python function that will take a new test set as input and apply the same transformation. 
    Please make sure to print the output of the function, print(output), no need to print row by row.
    Include test_list as the function input! Do not include the original input_list or output_list directly in the code.
   

    input dataset: {input_list}
    output dataset: {output_list}
    test set: {test_list}
    '''

RETRY = '''
    Given the previously generated code, its output, and the test list, 
    modify only the code in the code history—do not alter the input data—to ensure the generated output matches the correct output.
    Code history: {code_history}
    Test list: {test_list}
    Generated output: {generated_output}
'''

ERROR_IDENTIFIER = """
    Given the correct output and the generated output, identify high-level differences between the two. 
    Focus on structural issues, patterns, and anomalies rather than specific value mismatches.

    Provide only the high level errors in bullet points to help a programmer modify the code.

    Correct output: {correct_output}
    Generated output: {generated_output}
    """

RETRY_WITH_ERROR = '''
    Given the previous code and the identified high-level error,
    modify only the code in the code history—do not alter the input data—to ensure the generated output matches the correct output.
    Code history: {code_history}
    Error encountered: {error}
    Generated output: {generated_output}
'''
BASE_PROMPT_2 = '''
    You are a data scientist swpecializing in program by example, focusing on data wrangling and transformation tasks.
    Given an example input and output dataset, learn the transformations applied to convert the input dataset into the output dataset. 
    These transformations may involve various data cleaning and wrangling tasks that standardize and prepare the data for analysis.
'''
TEMPLATE_WITH_FUNC_LOOP = '''

    Based on your information, generate a Python function that will take input dataset as input and apply the same transformation. 
    Include input data as the function parameter and ensure the code only outputs the function definition.
    Make sure you include the input list in your python code as the function input.
    Make sure to print the output of the function 'print(output_list)' in the end of the code.
    
    input list: {input_list}
    output list: {output_list}
    '''
LOOP_FINAL = '''
    Given the code and the test list replace the function's input with the test list, without doing any modification to the code.
    Please make sure to print the output of the function.

    code: {code_history}
    test list: {test_list}
    '''
TEMPLATE_WITH_FUNC_CALL = '''

    Based on your information, generate a Python function that will take input dataset as input and apply the same transformation. 
    Include input data as the function parameter and ensure the code only outputs the function definition.
    You should try to include as much the example functions in your system prompt be part of your code.
    Make sure you include the input list in your python code as the function input.
    Make sure to print the output of the function 'print(output_list)' in the end of the code.
    
    input list: {input_list}
    output list: {output_list}
    '''