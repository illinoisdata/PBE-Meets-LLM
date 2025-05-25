import json
import os
from collections import defaultdict
import pandas as pd
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_folder', default='gpt-4o_base_foofah', type=str)
    parser.add_argument('--exp_data', default='foofah',
                        choices=['foofah', 'prose'],
                        type=str)

    args = parser.parse_args()

    return args

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

def eval(output_folder, exp_data):
    directory_path =  "../output/" + output_folder
    acc = defaultdict(list)

    for filename in os.listdir(directory_path):
        if filename == '.DS_Store':
            continue

        try:
            file_number = filename[:-5]
        except IndexError:
            print(f"Unexpected filename format: {filename}")
            continue

        file_path = os.path.join(directory_path, filename)
        if exp_data == 'foofah':
            correct_output_path = f'../data/foofah/{file_number}.txt'
        elif exp_data == 'prose':
            correct_output_path = f'../data/prose/{file_number}.txt'
        
        if not os.path.exists(correct_output_path):
            print(f"Correct output file not found: {correct_output_path}")
            continue

        try:
            _, test_data = read_in_data(correct_output_path)
            with open(file_path, 'r') as f:
                output = json.load(f)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Error processing {filename}: {e}")
            continue

        with open(file_path, 'r') as f:
            output = json.load(f)
        final_result = output['final'][1]

        ans = test_data[1]

        if not isinstance(final_result, list) or not all(isinstance(row, list) for row in final_result):
            print(f"Invalid format in final_result for file: {filename}")
            continue

        if not isinstance(ans, list) or not all(isinstance(row, list) for row in ans):
            print(f"Invalid format in ans for file: {filename}")
            continue

        acc_temp = 0
        for k in range(min(len(final_result),len(ans))):
            for m in range(min(len(final_result[k]),len(ans[k]))):
                if final_result[k][m] == ans[k][m]:
                    acc_temp += 1
        total_values = sum(len(inner_list) for inner_list in ans)
        test_case_acc = acc_temp/total_values
                
        acc[file_number] = [len(output)-2, test_case_acc]

    acc = sorted(acc.items())
    combine_by_dataset(acc, exp_data, output_folder)

    return acc

def combine_by_dataset(eval_result, exp_data, output_folde):
   
    acc_dict = defaultdict(lambda: [0, 0])
    if exp_data == 'foofah':
        ######## foofah
        for key, value in eval_result:
            dataset = key[:-2]
            acc_dict[dataset][0] += value[0] / 5
            acc_dict[dataset][1] += value[1] / 5
    elif exp_data == 'prose':
        ####### prose
        for key, value in eval_result:
            dataset = key.split('.')[0]
            acc_dict[dataset][0] += 1
            acc_dict[dataset][1] += value[1]

        acc_dict = {k: [v[0], v[1] / v[0]] for k, v in acc_dict.items()}
    
    df = pd.DataFrame(acc_dict).transpose()
    df.columns = ['# of tries', 'Combined Accuracy']
    df.to_excel(output_folde + '_accuracy.xlsx')
    return acc_dict
    


if __name__ == '__main__':
    args = parse_arguments()
    output_folder = args.output_folder
    exp_data = args.exp_data
    
    eval(output_folder, exp_data)
    
    print('----------------------')
    print('Evaluation Done')
