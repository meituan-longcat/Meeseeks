# Meeseeks
This is a beta version of Meeseeks, most of the previous open-source material is based on beta data. Heading to https://github.com/ADoublLEN/Meeseeks for the official release. 

## 📌Introduction

Meeseeks is an instruction-following benchmark based on business data. It features a multi-turn mode that enables models to self-correct their responses based on feedback provided by Meeseeks.

🔔 Instruction-Following refers to evaluating whether a model adheres to the requirements specified in the user prompt, focusing solely on compliance with given instructions rather than the factual accuracy of the response.

## Quick Start

To run the project, you need to implement 3 different models by yourself:
- target model 
- extract model (which we recommend you using `Qwen2.5-Coder-32B-Instruct`)
- score model (which we recommend you using `Qwen2.5-32B-Instruct`)

You can either use APIs like openai, or implement your model using engines like vLLM.
Write your implement in `source/model`. Create a new class that inherits from `base_model.py` and implements `generate` method.
We provided a demo class `demo_api_model.py` which is the API we used on our own platfrom, you may use it as a reference to build your own.

After implement 3 models, you need to modify `run.py` to initialize your models, then just `python3 run.py` to start the evaluation!

Note that we only provided a multi-turn version of our evaluation script. You can modify the script to support single-turn evaluation by setting the total round to 1.
