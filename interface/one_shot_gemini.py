import json
import io
import contextlib
import prompt 
from collections import defaultdict
import ast
import os
from google.genai import types
import time
from google import genai
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str)
    parser.add_argument('--model', default='gemini-2.0-flash',  type=str)
    parser.add_argument('--prompt', default='base', choices=['base, knowledge'], type=str)
    parser.add_argument('--test_file',choices=['foofah, prose'], type=str)

    args = parser.parse_args()
    return args


BASE = prompt.TEMPLATE_C
KG_BASE_PROMPT = prompt.TEMPLATE_WITH_FUNC

def run_code(code):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code)

        captured_output = output.getvalue()
    except:
        captured_output = []
    return captured_output

def serialize(obj):
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    if hasattr(obj, 'text'):
        return obj.text
    if hasattr(obj, '__str__'):
        return str(obj)
    return obj

def read_in_data(file_name):
    """Reads test data from the specified JSON file."""
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"File not found: {file_name}")

    with open(file_name, 'rb') as f:
        test_data = json.load(f)

    required_keys = ['InputTable', 'OutputTable', 'TestingTable', 'TestAnswer']
    for key in required_keys:
        if key not in test_data:
            raise KeyError(f"Missing key '{key}' in {file_name}")

    input_data = [test_data['InputTable'], test_data['OutputTable']]
    output_data = [test_data['TestingTable'], test_data['TestAnswer']]

    return input_data, output_data



def model_output(content, prompt_type, model, chat_history=None):
   
    ##### Set chat history system prompt base on experiment type
    if chat_history is None:
        if prompt_type == 'base':
            chat_history = []
        else:
            chat_history = [{"role": "system", "content": KG_BASE_PROMPT}]


    chat_history = [types.Content(role="user", parts=[types.Part(text=content)])]


    response = client.models.generate_content(
        model=model,
        contents= chat_history,
        config=types.GenerateContentConfig(
            temperature=0,
        )
    )

    if response.candidates:
        result_text = response.text
        chat_history.append({"role": "assistant", "content": result_text})
        return result_text, chat_history
    else:
        return None, chat_history

def run_exp_on_file(path,prompt_type, model):
    tmp_dic = defaultdict(list)
    input_data, test_data = read_in_data(path)
    content = BASE.format(
                        input_list = input_data[0],
                        output_list = input_data[1],
                        test_list = test_data[0]
                )
    start_time = time.time()
    answer, chat_history = model_output(content,prompt_type, model)
    end_time = time.time()
    if '```python' in answer:
        code = answer.split('```python')[1]
        code = code.split('```')[0]
        code_result = run_code(code)
        if isinstance(code_result, str):
            generated_output = ast.literal_eval(code_result)
        else:
            generated_output = code_result
    else:
            code = 'Invalid'
            generated_output = []


    tmp_dic['final'] = [serialize(code), serialize(generated_output)]
    tmp_dic['full_chat_history'] = serialize(chat_history)
    tmp_dic['time_use'] = end_time - start_time


    return tmp_dic
                                
            

def main(prompt_type, model, test_file):
    input_folder = os.path.join("..", "data", test_file)
    output_folder = os.path.join("..", "output", f"{model}_{prompt_type}_{test_file}")

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for sub_file in os.listdir(input_folder):
        if sub_file == '.DS_Store':
            continue

        print('Processing file:', sub_file)

        input_path = os.path.join(input_folder, sub_file)
        output = run_exp_on_file(input_path, prompt_type, model)

        output_path = os.path.join(output_folder, f"{sub_file[:-4]}.json")
        with open(output_path, 'w') as file:
            json.dump(output, file, indent=2)

    return

if __name__ == "__main__":
    args = parse_arguments()
    client = genai.Client(api_key=args.api_key)
    
    main(args.prompt_type, args.model, args.test_file)