#!/usr/bin/env python3
"""
OG_meeseeks项目的主运行文件 - 带默认配置版本
基于原始evaluate.py的默认配置，可以直接运行
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
            # 读取requirements.txt
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()

            # 过滤掉注释和空行
            packages = []
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)

            if packages:
                print(f"📦 发现 {len(packages)} 个依赖包需要检查...")
                for package in packages:
                    print(f"   - {package}")

                # 安装依赖
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", requirements_file
                ])
                print("✅ 所有依赖包安装完成!")
            else:
                print("📦 未发现需要安装的依赖包")

        except subprocess.CalledProcessError as e:
            print(f"❌ 安装依赖包时出错: {e}")
            print("请手动运行: pip install -r requirements.txt")
        except Exception as e:
            print(f"❌ 读取requirements.txt时出错: {e}")
    else:
        print("⚠️  未找到requirements.txt文件")

# 在导入其他模块之前先安装依赖
if __name__ == "__main__":
    install_requirements()

import json
import time
import argparse
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
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        response = requests.post(url, headers=headers, json=payload, timeout=10)

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
DEFAULT_CONFIG = {
    'qwen_url': 'http://10.164.51.197:8080',
    'qwen_coder_url': 'http://10.166.176.56:8080',
    'tested_model_url': 'http://10.164.51.197:8080',  # 默认使用相同的模型
    'batch_size': 500,
    'rounds': 2,
    'data_path': '',
    'output_dir': 'evaluation_results'
}

def process_in_batches(data, batch_size=100):
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
            batch_responses = call_tested_model(batch_questions)  # 使用被测模型

            # Assign responses back to data items
            for item, response in zip(current_batch, batch_responses):
                item["model_response"] = response

        except Exception as e:
            print(f"❌ Error occurred while processing batch {batch_start}-{batch_end-1}: {str(e)}")
            # Add retry logic or error handling here


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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OG_meeseeks评估系统 - 带默认配置')
    parser.add_argument('--qwen_url', default=DEFAULT_CONFIG['qwen_url'], help=f'Qwen API的URL (默认: {DEFAULT_CONFIG["qwen_url"]})')
    parser.add_argument('--qwen_coder_url', default=DEFAULT_CONFIG['qwen_coder_url'], help=f'Qwen Coder API的URL (默认: {DEFAULT_CONFIG["qwen_coder_url"]})')
    parser.add_argument('--tested_model_url', default=DEFAULT_CONFIG['tested_model_url'], help=f'被测模型API的URL (默认: {DEFAULT_CONFIG["tested_model_url"]})')
    parser.add_argument('--batch_size', type=int, default=DEFAULT_CONFIG['batch_size'], help=f'批处理大小 (默认: {DEFAULT_CONFIG["batch_size"]})')
    parser.add_argument('--rounds', type=int, default=DEFAULT_CONFIG['rounds'], help=f'评估轮数 (默认: {DEFAULT_CONFIG["rounds"]})')
    parser.add_argument('--data_path', default=DEFAULT_CONFIG['data_path'], help=f'数据文件路径 (默认: {DEFAULT_CONFIG["data_path"]})')
    parser.add_argument('--output_dir', default=DEFAULT_CONFIG['output_dir'], help=f'输出目录 (默认: {DEFAULT_CONFIG["output_dir"]})')
    parser.add_argument('--use_defaults', action='store_true', help='使用所有默认配置，无需指定参数')

    args = parser.parse_args()

    # 如果使用默认配置模式，直接使用所有默认值
    if args.use_defaults:
        print("🎯 使用默认配置模式")
        for key, value in DEFAULT_CONFIG.items():
            setattr(args, key, value)

    # 设置API URLs
    set_qwen_url(args.qwen_url)
    set_qwen_coder_url(args.qwen_coder_url)
    set_tested_model_url(args.tested_model_url)

    # 测试API连接
    if not test_all_apis(args.qwen_url, args.qwen_coder_url, args.tested_model_url):
        print("🛑 API测试失败，程序退出")
        return

    print()  # 添加空行分隔

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 检查数据文件是否存在
    if not os.path.exists(args.data_path):
        print(f"❌ 数据文件不存在: {args.data_path}")
        print("💡 请检查文件路径或使用 --data_path 参数指定正确的路径")
        return

    # 加载数据
    print(f"📂 Loading data from: {args.data_path}")
    try:
        with open(args.data_path, "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except Exception as e:
        print(f"❌ 加载数据文件失败: {e}")
        return

    # 保存原始问题
    for item in current_data:
        item["og_question"] = item["question"]

    print(f"📊 Loaded {len(current_data)} items")
    print(f"🔧 Configuration:")
    print(f"   - Qwen URL: {args.qwen_url}")
    print(f"   - Qwen Coder URL: {args.qwen_coder_url}")
    print(f"   - Tested Model URL: {args.tested_model_url}")
    print(f"   - Batch Size: {args.batch_size}")
    print(f"   - Rounds: {args.rounds}")
    print(f"   - Output Directory: {args.output_dir}")
    print("=" * 80)

    # 多轮评估
    for round_num in range(args.rounds):
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
        process_in_batches(current_data, args.batch_size)

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
        output_file = os.path.join(args.output_dir, f"round_{round_num + 1}.json")
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


if __name__ == "__main__":
    main()
