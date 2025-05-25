from flask import Flask, request, jsonify
import openai
import json
import io
import contextlib
import os

app = Flask(__name__)

# Initialize OpenAI client (Ensure your API key is set correctly)
client = openai.Client(
      api_key='sk-FRZYCa7wg6YGc6vDvAa8gNaQ5RsRgesoOt9nhJqJ3A21zqPF',
      base_url = "https://api.feidaapi.com/v1")

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

def read_in_data(file_name):
        test_data = None
        input_data = [''] * 2
        output_data = [''] * 2
        with open(file_name, 'rb') as f:
            test_data = json.load(f)
            
        input_data[0] = test_data['InputTable']
        input_data[1] = test_data['OutputTable']
        output_data[0] = test_data['TestingTable']
        output_data[1] = test_data['TestAnswer']


        return input_data, output_data
def get_content(input):
    input_data, output_data = read_in_data(input)
    content = TEMPLATE_C.format(
                        input_list = input_data[0],
                        output_list = input_data[1],
                        test_list = output_data[0]
                        )
    return content

def run_code(code):
    output = io.StringIO()

    # Use contextlib.redirect_stdout to redirect print statements to the StringIO object
    try:
        with contextlib.redirect_stdout(output):
            exec(code)

        # Get the output as a string
        captured_output = output.getvalue()
    except:
        captured_output = []
    return captured_output

@app.route('/get_output', methods=['POST'])
def get_output():
    try:
        print('Received request')

        # Get JSON input from client
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON input"}), 400

        input = data.get('input')


        if not input:
            return jsonify({"error": "Missing 'content' field"}), 400

        settings = {
            "model": "gpt-4o",
            "temperature": 0,
            "seed": 1,
        }
        content = get_content(input)
        # Initialize chat history
        chat_history = [{"role": "user", "content": content}]

        # Call OpenAI API
        response = client.chat.completions.create(
            messages=chat_history, stream=False, **settings
        )

        # Process the response
        if response.choices:
            answer = response.choices[0].message.content
            chat_history.append({"role": "assistant", "content": answer})

            if '```python' in answer:
                code = answer.split('```python')[1]
                code = code.split('```')[0]
                code_result = run_code(code)
                if isinstance(code_result, str):
                    try:
                        generated_output = eval(code_result)
                    except:
                        generated_output = code_result
                else:
                    generated_output = code_result
            else:
                code = 'Invalid'
                generated_output = []
            # Return a proper JSON response
            return jsonify({
                "response": generated_output,
                "chat_history": chat_history
            })
        else:
            return jsonify({"error": "No valid response from the model"}), 500
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500  # Return an error message

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
