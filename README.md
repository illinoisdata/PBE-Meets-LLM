# PBE Meets LLM: When Few Examples Aren’t Few-Shot Enough


**PBE-Meets-LLM** explores the intersection of Programming by Example (PBE) and Large Language Models (LLMs), aiming to enhance the capabilities of LLMs in synthesizing programs from input-output examples.

## Overview

Programming by Example is a paradigm where programs are synthesized based on provided input-output pairs. This project investigates how LLMs can be leveraged to perform PBE tasks more effectively, potentially improving upon traditional methods in terms of accuracy and generalization.


### Prerequisites

- Python 3.10
- For LLama2: [PyTorch](https://pytorch.org/)
[Transformers](https://huggingface.co/docs/transformers/index)
- For Foofah and Hybrid Docker


### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/illinoisdata/PBE-Meets-LLM.git
   cd PBE-Meets-LLM
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


## Usage

#### Run LLM based
To run experiments, use the provided scripts in the `interface/` directory. For example if one to run one shot knowledge prompt with gpt-4o model, one can use the following command:

```bash
cd interface
python one_shot_gpt.py --api_key sk-... --model gpt-4o --prompt_type knowledge --test_file foofah
```

#### Run Prose Api
nevigate to the prose-api folder under model
```
cd interface/prose
bash run.sh
```

#### Run Foofah and Hybrid model

Since Foofah was built with python2 we will  be using Docker to run it. Please follow the following files to run the experiments.
- [Foofah](https://github.com/illinoisdata/PBE-Meets-LLM/blob/main/interface/foofah_experiment/README.md)
- [Hybrid](https://github.com/illinoisdata/PBE-Meets-LLM/blob/main/interface/hybrid/README.md)

## Evaluation

All experiments are evaluated using the following exact matrics base on one_shot or multi_try the evaluation could be run by the provided scripts in the `evaluation/` directory. 
