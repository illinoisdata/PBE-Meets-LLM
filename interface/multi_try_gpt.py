import json
import openai
import io
import contextlib
import prompt 
from collections import defaultdict
import time
import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str)
    parser.add_argument('--model', default='gpt-4o',  type=str)
    parser.add_argument('--prompt_type', default='base', choices=['base, knowledge'], type=str)
    parser.add_argument('--test_file',default='foofah', choices=['foofah, prose'], type=str)
    parser.add_argument('--specific_error', default=True,  type=bool)
    parser.add_argument('--round_number', default= 10,  type=int)
    args = parser.parse_args()
    return args

# prompts
TEMPLATE_WITH_FUNC_LOOP = prompt.TEMPLATE_WITH_FUNC_LOOP
LOOP_FINAL = prompt.LOOP_FINAL
RETRY = prompt.RETRY
KG_BASE_PROMPT = prompt.TEMPLATE_WITH_FUNC
TEMPLATE_WITH_FUNC_CALL = prompt.TEMPLATE_WITH_FUNC_CALL
ERROR_IDENTIFIER = prompt.ERROR_IDENTIFIER
RETRY_WITH_ERROR = prompt.RETRY_WITH_ERROR

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


def model_output(content, prompt_type, model, chat_history=None, error = False):
   
     ##### Set chat history system prompt base on experiment type
    if error:
        chat_history = []
    elif chat_history is None:
        if prompt_type == 'base':
            chat_history = []
        else:
            chat_history = [{"role": "system", "content": KG_BASE_PROMPT}]

    ## gpt & claude
    settings = {
            "model": model,
            "temperature": 0,
            "seed": 1,
        }
    #Append the current user's message to the history
    chat_history.append({"role": "user", "content": content})

    # Send the entire conversation history to the model
    response = client.chat.completions.create(
        messages=chat_history, stream=False, **settings
    )
    
    # Process the model's response
    if response.choices:
        client_response = response.choices[0].message.content
        if error:
            return client_response, response.usage.total_tokens
        chat_history.append({"role": "assistant", "content": client_response})
        return client_response, chat_history, response.usage.total_tokens
    else:
        return None, chat_history, None



def run_exp_on_file(path,prompt_type, model, specific_error, round_num):
    tmp_dic = defaultdict(list)
    input_data, test_data = read_in_data(path)
    token_used = 0
    time_used = 0


    content = TEMPLATE_WITH_FUNC_CALL.format(
             input_list = input_data[0],
            output_list = input_data[1],
        )
    start_time = time.time()
    answer, chat_history, tmp_token = model_output(content,prompt_type, model)
    end_time = time.time()
    time_used += end_time - start_time
    token_used += tmp_token
 
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
    num_try = 0
    tmp_dic[num_try] = [code, generated_output]
    if specific_error:
        while generated_output != input_data[1] and num_try < round_num:
            num_try += 1
                        
            print('generating errors')
            error_content = ERROR_IDENTIFIER.format(
                correct_output = input_data[1],
                generated_output = generated_output
            )
            start_time = time.time()
            errors,tmp_token = model_output(error_content, prompt_type, model, chat_history, error = True)
            end_time = time.time()
            time_used += end_time - start_time
            token_used += tmp_token
            mid_time = time.time()
            print('error time', mid_time - start_time)
            tmp_dic['errors'].append(errors)

            # retry with error identified
            print('retrying with error')
            retry_with_error_content = RETRY_WITH_ERROR.format(
                code_history = code,
                error = errors,
                generated_output = generated_output
            )
            start_time = time.time()
            answer, chat_history,tmp_token = model_output(retry_with_error_content, prompt_type, model, chat_history)
            end_time = time.time()
            time_used += end_time - start_time
            token_used += tmp_token
            end_time = time.time()
            print('retry time', end_time - mid_time)
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
            print('retry', num_try)
            tmp_dic[num_try] = [code, generated_output]
    else:
        while generated_output != input_data[1] and num_try < 10:
            num_try += 1
            retry_content = RETRY.format(
                code_history = code,
                test_list = input_data[1],
                generated_output = generated_output
            )
            start_time = time.time()
            answer, chat_history, tmp_token = model_output(retry_content,prompt_type, model, chat_history)
            end_time = time.time()
            time_used += end_time - start_time
            token_used += tmp_token
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
            print('retry', num_try)
            tmp_dic[num_try] = [code, generated_output]
                # pass the test input to the code
    final_content = LOOP_FINAL.format(
            code_history = code,
            test_list = test_data[0]
        )
    start_time = time.time()
    answer, chat_history, tmp_token = model_output(final_content,prompt_type, model,chat_history)
    end_time = time.time()
    time_used += end_time - start_time
    token_used += tmp_token
    code = answer.split('```python')[1]
    code = code.split('```')[0]
    code_result = run_code(code)
    if isinstance(code_result, str):
        try:
            generated_output = eval(code_result)
        except:
            generated_output = 'DOUBLE CHECK' + ', '.join(map(str, code_result))
    else:
        generated_output = 'DOUBLE CHECK' + ', '.join(map(str, code_result))
    tmp_dic['final'] = [code, generated_output]
    tmp_dic['full_chat_history'] = chat_history
    tmp_dic['time_use'] = end_time - start_time
    tmp_dic['token_used'] = token_used

    return tmp_dic

def main(prompt_type, model, test_file, specific_error, round_num):
    input_folder = os.path.join("..", "data", test_file)
    output_folder = os.path.join("..", "output", f"multi_try_{model}_{prompt_type}_{test_file}")

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for sub_file in os.listdir(input_folder):
        if sub_file == '.DS_Store':
            continue

        print('Processing file:', sub_file)

        input_path = os.path.join(input_folder, sub_file)
        output = run_exp_on_file(input_path, prompt_type, model, specific_error, round_num)

        output_path = os.path.join(output_folder, f"{sub_file[:-4]}.json")
        with open(output_path, 'w') as file:
            json.dump(output, file, indent=2)

    return

if __name__ == "__main__":
    args = parse_arguments()
    client = openai.Client(api_key= args.api_key)
    main(args.prompt_type, args.model, args.test_file, args.specific_error, args.round_number)