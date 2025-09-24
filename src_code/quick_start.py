#!/usr/bin/env python3
"""
OG_meeseeks 快速启动脚本
使用默认配置，类似原始evaluate.py的直接运行方式
"""

import sys
import subprocess
import os

def install_requirements():
    """自动安装requirements.txt中的依赖包"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

    if os.path.exists(requirements_file):
        print("🔧 检查并安装依赖包...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file, "-q"
            ])
            print("✅ 依赖包检查完成!")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装依赖包时出错: {e}")

# 在导入其他模块之前先安装依赖
install_requirements()

import json
import time
import requests
from process_corresponding_parts import extract_content
from process_evaluation import process_all_items
from multi_round_template_added import multi_round_template_added
from LLM_APIs.qwen_api import set_qwen_url
from LLM_APIs.qwen_coder_api import set_qwen_coder_url
from LLM_APIs.tested_model_api import set_tested_model_url, call_tested_model


def test_single_api(url, api_name, test_prompt="Hello"):
    """测试单个API是否可用"""
    print(f"🔗 Testing {api_name}: {url}")

    payload = {
        "prompt": test_prompt,
        "max_new_tokens": 50,
        "temperature": 0.00,
        "top_k": 1
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=1800)

        if response.status_code == 200:
            try:
                response_json = response.json()
                if 'completions' in response_json and response_json['completions']:
                    print(f"✅ {api_name} is working")
                    return True
                else:
                    print(f"❌ {api_name} returned invalid format")
                    return False
            except json.JSONDecodeError:
                print(f"❌ {api_name} returned non-JSON response")
                return False
        else:
            print(f"❌ {api_name} returned HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ {api_name} connection failed")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {api_name} timeout")
        return False
    except Exception as e:
        print(f"❌ {api_name} error: {e}")
        return False


def test_all_apis(qwen_url, qwen_coder_url, tested_model_url):
    """测试所有三个API是否可用"""
    print("🧪 Testing API connections...")
    print("=" * 50)

    results = {}
    results['qwen'] = test_single_api(qwen_url, "Qwen API")
    results['qwen_coder'] = test_single_api(qwen_coder_url, "Qwen Coder API")
    results['tested_model'] = test_single_api(tested_model_url, "Tested Model API")

    print("=" * 50)

    all_working = all(results.values())
    if all_working:
        print("✅ All APIs are working properly!")
        return True
    else:
        print("❌ Some APIs are not working:")
        for api_name, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {api_name}: {'Working' if status else 'Failed'}")

        print("\n💡 Please check:")
        print("   - API services are running")
        print("   - URLs are correct")
        print("   - Network connectivity")
        print("   - Firewall settings")

        user_input = input("\n❓ Continue anyway? (y/N): ").strip().lower()
        return user_input in ['y', 'yes']

# 默认配置 - 基于原始evaluate.py
BATCH_SIZE = 500
ROUNDS = 2
FILE_PATH = ""

# API URLs - 基于原始evaluate.py
QWEN_URL = "http://10.164.51.197:8080"
QWEN_CODER_URL = "http://10.166.176.56:8080"
TESTED_MODEL_URL = "http://10.164.51.197:8080"  # 默认使用相同的模型

def process_in_batches(data, batch_size=BATCH_SIZE):
    """批量处理数据，调用被测模型获取响应"""
    total_items = len(data)
    for batch_start in range(0, total_items, batch_size):
        batch_end = min(batch_start + batch_size, total_items)
        current_batch = data[batch_start:batch_end]

        # Print processing progress
        print(f"📊 Processing items {batch_start}-{batch_end-1} out of {total_items} total items...")

        try:
            # Batch get questions and call model
            batch_questions = [item["question"] for item in current_batch]
            batch_responses = call_tested_model(batch_questions)

            # Assign responses back to data items
            for item, response in zip(current_batch, batch_responses):
                item["model_response"] = response

        except Exception as e:
            print(f"❌ Error occurred while processing batch {batch_start}-{batch_end-1}: {str(e)}")
            print("⚠️  Setting empty responses for failed batch...")
            # 确保即使API调用失败，也给每个item添加model_response字段
            for item in current_batch:
                if "model_response" not in item:
                    item["model_response"] = ""  # 设置为空字符串，避免后续KeyError

def iferror(item):
    """检查是否有评估错误"""
    for subq in item["sub_questions"]:
        if subq["eval_result"] == 0:
            return True
    return False

def fix_json_data(data):
    """修复JSON数据结构"""
    for item in data:
        if "json_schema" in item:
            og_subqs = [
                {
                    "point_id": 0,
                    "question": "Does it meet schema requirements",
                    "rule": "SCHEMA:json_schema",
                    "dep": [],
                    "被依赖": False,
                    "能力项": "JSON"
                }]
            for subq in item["sub_questions"]:
                if subq["point_id"] > 0:
                    og_subqs.append(subq)
            item["sub_questions"] = og_subqs

    return data

if __name__ == "__main__":
    print("🚀 OG_meeseeks 快速启动")
    print("=" * 50)

    # 设置API URLs
    set_qwen_url(QWEN_URL)
    set_qwen_coder_url(QWEN_CODER_URL)
    set_tested_model_url(TESTED_MODEL_URL)

    print(f"🔧 配置信息:")
    print(f"   - Qwen URL: {QWEN_URL}")
    print(f"   - Qwen Coder URL: {QWEN_CODER_URL}")
    print(f"   - Tested Model URL: {TESTED_MODEL_URL}")
    print(f"   - Collecting Batch Size: {COLLECTING_BATCH_SIZE}")
    print(f"   - Processing Batch Size: {PROCESSING_BATCH_SIZE}")
    print(f"   - Rounds: {ROUNDS}")
    print(f"   - Data Path: {FILE_PATH}")
    print()

    # 测试API连接
    if not test_all_apis(QWEN_URL, QWEN_CODER_URL, TESTED_MODEL_URL):
        print("🛑 API测试失败，程序退出")
        exit(1)

    print()  # 添加空行分隔

    # 检查数据文件是否存在
    if not os.path.exists(FILE_PATH):
        print(f"❌ 数据文件不存在: {FILE_PATH}")
        print("💡 请检查文件路径或修改 FILE_PATH 变量")
        print("💡 或者使用 run_with_defaults.py 脚本指定自定义路径")
        exit(1)

    # 加载数据
    print(f"📂 Loading data from: {FILE_PATH}")
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        current_data = json.load(f)

    # 保存原始问题
    for item in current_data:
        item["og_question"] = item["question"]

    print(f"📊 Loaded {len(current_data)} items")
    print("=" * 80)

    # 创建输出目录
    os.makedirs("evaluation_results", exist_ok=True)

    # 多轮评估
    for round_num in range(ROUNDS):
        print(f"🚀 Starting Round {round_num + 1} Evaluation")
        print("=" * 60)

        # 第一轮之后，只处理有错误的项目
        if round_num != 0:
            current_data = [item for item in current_data if iferror(item)]
            current_data = multi_round_template_added(current_data)
            current_data = fix_json_data(current_data)
            print(f"📊 Processing {len(current_data)} items with errors from previous round")

        if not current_data:
            print("✅ No items to process in this round. All evaluations passed!")
            break

        print("📝 Getting model responses for evaluation...")
        process_in_batches(current_data)

        # 开始评估
        og_start_time = time.time()
        print(f"🔄 Round {round_num + 1} Processing Started")

        # 步骤1：提取对应部分
        start_time = time.time()
        print("🔍 Step 1: Extracting corresponding parts from all responses...")
        current_data = extract_content(current_data)
        print("✅ Corresponding parts extraction completed successfully")
        end_time = time.time()
        print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
        print()

        # 步骤2：处理和评估
        start_time = time.time()
        print("🔍 Step 2: Processing and evaluating all items...")
        current_data = process_all_items(current_data)
        print("✅ Item processing and evaluation completed successfully")
        end_time = time.time()
        print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
        print()

        total_time = end_time - og_start_time
        print("=" * 60)
        print(f"🎉 Round {round_num + 1} Completed Successfully!")
        print(f"⏱️  Total round time: {total_time:.2f} seconds")
        print("=" * 60)

        # 保存结果
        output_file = f"evaluation_results/round_{round_num + 1}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)
        print(f"💾 Results saved to: {output_file}")
        print()

        # 统计本轮结果
        total_items = len(current_data)
        error_items = len([item for item in current_data if iferror(item)])
        success_items = total_items - error_items
        print(f"📈 Round {round_num + 1} Statistics:")
        print(f"   - Total items: {total_items}")
        print(f"   - Successful items: {success_items}")
        print(f"   - Items with errors: {error_items}")
        print(f"   - Success rate: {success_items/total_items*100:.2f}%")
        print()

    print("🎊 All rounds completed successfully!")
