import json
import io
import contextlib
import prompt 
import torch
from collections import defaultdict
import ast
import os
import time
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='meta-llama/Llama-2-13b-chat-hf',  type=str)
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


def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")
    return tokenizer, model


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

def format_prompt(chat_history):
        prompt = ""
        for msg in chat_history:
            if msg["role"] == "user":
                prompt += f"<|user|>: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"<|assistant|>: {msg['content']}\n"
            elif msg["role"] == "system":
                prompt += f"<|system|>: {msg['content']}\n"
        prompt += "<|assistant|>:"
        return prompt

def model_output(content, prompt_type, tokenizer, model, chat_history=None):

     ##### Set chat history system prompt base on experiment type
    if chat_history is None:
        if prompt_type == 'base':
            chat_history = []
        else:
            chat_history = [{"role": "system", "content": KG_BASE_PROMPT}]


    chat_history.append({"role": "user", "content": content})
    prompt = format_prompt(chat_history)

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    assistant_reply = output_text.split("<|assistant|>:")[-1].strip()


    chat_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply, chat_history, len(input_ids[0]) + len(output_ids[0])


def run_exp_on_file(path,prompt_type, model):
    tmp_dic = defaultdict(list)
    input_data, test_data = read_in_data(path)
    content = BASE.format(
                        input_list = input_data[0],
                        output_list = input_data[1],
                        test_list = test_data[0]
                )
    start_time = time.time()
    answer, chat_history = model_output(content,prompt_type, tokenizer, model)
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
    tokenizer, model = load_model(args.model)
    
    main(args.prompt_type, args.model, args.test_file)