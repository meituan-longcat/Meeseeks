#!/usr/bin/env python3
"""
OG_meeseeks项目的主运行文件 - 带默认配置版本
基于原始evaluate.py的默认配置，可以直接运行
"""

import sys
import subprocess
import os

# 强制关闭输出缓冲，确保 print 立即显示
import builtins
_original_print = builtins.print
def debug_print(*args, **kwargs):
    """增强的 print 函数，强制刷新输出"""
    kwargs.setdefault('flush', True)
    _original_print(*args, **kwargs)

# 可选：替换全局 print（调试模式下）
# builtins.print = debug_print

import json
import time
import argparse
from process_corresponding_parts import extract_content
from process_evaluation import process_all_items
from multi_round_template_added import multi_round_template_added
from LLM_APIs.qwen_api import set_qwen_config
from LLM_APIs.qwen_coder_api import set_qwen_coder_config
from LLM_APIs.tested_model_api import set_tested_model_config, call_tested_model


def test_single_api(client, model_name, api_name):
    """测试单个API是否可用"""
    print(f"🔗 Testing {api_name} with model: {model_name}")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": "Hello"},
            ],
            max_tokens=50,
            temperature=0.00,
            timeout=30
        )
        
        if response.choices and len(response.choices) > 0:
            print(f"✅ {api_name} is working")
            return True
        else:
            print(f"❌ {api_name} returned invalid format")
            return False

    except Exception as e:
        print(f"❌ {api_name} error: {e}")
        return False


def test_all_apis():
    """测试所有三个API是否可用"""
    from LLM_APIs.qwen_api import _qwen_client, _qwen_model_name
    from LLM_APIs.qwen_coder_api import _qwen_coder_client, _qwen_coder_model_name
    from LLM_APIs.tested_model_api import _tested_model_client, _tested_model_name
    
    print("🧪 Testing API connections...")
    print("=" * 50)

    results = {}
    
    if _qwen_client:
        results['qwen'] = test_single_api(_qwen_client, _qwen_model_name, "Qwen API")
    else:
        print("⚠️  Qwen API not configured")
        results['qwen'] = False
        
    if _qwen_coder_client:
        results['qwen_coder'] = test_single_api(_qwen_coder_client, _qwen_coder_model_name, "Qwen Coder API")
    else:
        print("⚠️  Qwen Coder API not configured")
        results['qwen_coder'] = False
        
    if _tested_model_client:
        results['tested_model'] = test_single_api(_tested_model_client, _tested_model_name, "Tested Model API")
    else:
        print("⚠️  Tested Model API not configured")
        results['tested_model'] = False

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
        print("   - API keys are correct")
        print("   - Base URLs are correct")
        print("   - Model names are correct")
        print("   - Network connectivity")

        user_input = input("\n❓ Continue anyway? (y/N): ").strip().lower()
        return user_input in ['y', 'yes']

# 导入配置
from config import (
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    QWEN_CODER_API_KEY, QWEN_CODER_BASE_URL, QWEN_CODER_MODEL,
    TESTED_MODEL_API_KEY, TESTED_MODEL_BASE_URL, TESTED_MODEL_NAME
)

# 默认配置 - 基于原始evaluate.py
# 默认使用文件夹路径，会自动加载该文件夹下的所有JSON文件
DEFAULT_CONFIG = {
    'qwen_api_key': QWEN_API_KEY,
    'qwen_base_url': QWEN_BASE_URL,
    'qwen_model': QWEN_MODEL,
    'qwen_coder_api_key': QWEN_CODER_API_KEY,
    'qwen_coder_base_url': QWEN_CODER_BASE_URL,
    'qwen_coder_model': QWEN_CODER_MODEL,
    'tested_model_api_key': TESTED_MODEL_API_KEY,
    'tested_model_base_url': TESTED_MODEL_BASE_URL,
    'tested_model_name': TESTED_MODEL_NAME,
    'batch_size': 5,
    'rounds': 2,
    'data_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'input_data/asia_data/raw_input'),
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
    
    # Qwen API配置
    parser.add_argument('--qwen_api_key', default=DEFAULT_CONFIG['qwen_api_key'], help='Qwen API密钥')
    parser.add_argument('--qwen_base_url', default=DEFAULT_CONFIG['qwen_base_url'], help='Qwen API基础URL')
    parser.add_argument('--qwen_model', default=DEFAULT_CONFIG['qwen_model'], help='Qwen模型名称')
    
    # Qwen Coder API配置
    parser.add_argument('--qwen_coder_api_key', default=DEFAULT_CONFIG['qwen_coder_api_key'], help='Qwen Coder API密钥')
    parser.add_argument('--qwen_coder_base_url', default=DEFAULT_CONFIG['qwen_coder_base_url'], help='Qwen Coder API基础URL')
    parser.add_argument('--qwen_coder_model', default=DEFAULT_CONFIG['qwen_coder_model'], help='Qwen Coder模型名称')
    
    # Tested Model API配置
    parser.add_argument('--tested_model_api_key', default=DEFAULT_CONFIG['tested_model_api_key'], help='被测模型API密钥')
    parser.add_argument('--tested_model_base_url', default=DEFAULT_CONFIG['tested_model_base_url'], help='被测模型API基础URL')
    parser.add_argument('--tested_model_name', default=DEFAULT_CONFIG['tested_model_name'], help='被测模型名称')
    
    # 其他配置
    parser.add_argument('--batch_size', type=int, default=DEFAULT_CONFIG['batch_size'], help=f'批处理大小 (默认: {DEFAULT_CONFIG["batch_size"]})')
    parser.add_argument('--rounds', type=int, default=DEFAULT_CONFIG['rounds'], help=f'评估轮数 (默认: {DEFAULT_CONFIG["rounds"]})')
    parser.add_argument('--data_path', default=DEFAULT_CONFIG['data_path'], help=f'数据文件路径 (默认: {DEFAULT_CONFIG["data_path"]})')
    parser.add_argument('--output_dir', default=DEFAULT_CONFIG['output_dir'], help=f'输出目录 (默认: {DEFAULT_CONFIG["output_dir"]})')
    parser.add_argument('--language_filter', default='', help='语言过滤器，多个语言用逗号分隔 (例如: 中文,日语 或 英语,德语)')
    parser.add_argument('--use_defaults', action='store_true', help='使用所有默认配置，无需指定参数')
    parser.add_argument('--debug', action='store_true', help='启用调试模式，显示所有子模块的输出')
    parser.add_argument('--verbose', action='store_true', help='显示详细输出信息')

    args = parser.parse_args()
    
    # 如果启用调试模式，替换全局 print 并设置环境变量
    if args.debug or args.verbose:
        print("🐛 调试模式已启用 - 将显示所有子模块的输出")
        builtins.print = debug_print
        os.environ['PYTHONUNBUFFERED'] = '1'  # 关闭 Python 输出缓冲
        sys.stdout.reconfigure(line_buffering=True)  # 启用行缓冲
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(line_buffering=True)

    # 如果使用默认配置模式，直接使用所有默认值
    if args.use_defaults:
        print("🎯 使用默认配置模式")
        for key, value in DEFAULT_CONFIG.items():
            setattr(args, key, value)

    # 设置API配置
    set_qwen_config(
        api_key=args.qwen_api_key,
        base_url=args.qwen_base_url,
        model_name=args.qwen_model
    )
    set_qwen_coder_config(
        api_key=args.qwen_coder_api_key,
        base_url=args.qwen_coder_base_url,
        model_name=args.qwen_coder_model
    )
    set_tested_model_config(
        api_key=args.tested_model_api_key,
        base_url=args.tested_model_base_url,
        model_name=args.tested_model_name
    )

    # 测试API连接
    if not test_all_apis():
        print("🛑 API测试失败，程序退出")
        return

    print()  # 添加空行分隔

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 检查数据路径是否存在
    if not os.path.exists(args.data_path):
        print(f"❌ 数据路径不存在: {args.data_path}")
        print("💡 请检查路径或使用 --data_path 参数指定正确的路径")
        return

    # 加载数据 - 支持文件或文件夹
    current_data = []
    if os.path.isdir(args.data_path):
        # 如果是文件夹，加载所有JSON文件
        print(f"📂 Loading data from directory: {args.data_path}")
        json_files = sorted([f for f in os.listdir(args.data_path) if f.endswith('.json')])
        
        # 应用语言过滤器
        if args.language_filter:
            filter_langs = [lang.strip() for lang in args.language_filter.split(',')]
            print(f"🔍 Applying language filter: {', '.join(filter_langs)}")
            
            # 过滤文件：只保留包含指定语言的文件
            filtered_files = []
            for json_file in json_files:
                if any(lang in json_file for lang in filter_langs):
                    filtered_files.append(json_file)
            
            json_files = filtered_files
            
            if not json_files:
                print(f"❌ 使用语言过滤器后没有找到匹配的文件")
                print(f"   过滤条件: {', '.join(filter_langs)}")
                return
        
        if not json_files:
            print(f"❌ 目录中没有找到JSON文件: {args.data_path}")
            return
        
        print(f"📄 Found {len(json_files)} JSON files:")
        for json_file in json_files[:5]:  # 只显示前5个
            print(f"   - {json_file}")
        if len(json_files) > 5:
            print(f"   ... and {len(json_files) - 5} more files")
        
        # 加载所有JSON文件
        for json_file in json_files:
            file_path = os.path.join(args.data_path, json_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        current_data.extend(file_data)
                    else:
                        current_data.append(file_data)
            except Exception as e:
                print(f"⚠️  Failed to load {json_file}: {e}")
    else:
        # 如果是单个文件
        print(f"📂 Loading data from file: {args.data_path}")
        try:
            with open(args.data_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    current_data = file_data
                else:
                    current_data = [file_data]
        except Exception as e:
            print(f"❌ 加载数据文件失败: {e}")
            return

    if not current_data:
        print("❌ 没有加载到任何数据")
        return

    # 保存原始问题
    for item in current_data:
        item["og_question"] = item["question"]

    print(f"📊 Loaded {len(current_data)} items")
    print(f"🔧 Configuration:")
    print(f"   - Qwen Model: {args.qwen_model}")
    print(f"   - Qwen Base URL: {args.qwen_base_url}")
    print(f"   - Qwen Coder Model: {args.qwen_coder_model}")
    print(f"   - Qwen Coder Base URL: {args.qwen_coder_base_url}")
    print(f"   - Tested Model: {args.tested_model_name}")
    print(f"   - Tested Model Base URL: {args.tested_model_base_url}")
    print(f"   - Batch Size: {args.batch_size}")
    print(f"   - Rounds: {args.rounds}")
    print(f"   - Output Directory: {args.output_dir}")
    print("=" * 80)

    # 根据数据路径判断使用哪个语言的评估模块
    # 需要将 src_code 添加为包，并正确导入
    project_root = os.path.dirname(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 智能判断语言：支持路径中包含 english/eng 或 asia/中文/日语/韩语
    data_path_lower = args.data_path.lower()
    is_english = ('english' in data_path_lower or 'eng' in data_path_lower or 
                  '/english_data/' in data_path_lower)
    is_asia = ('asia' in data_path_lower or '中文' in data_path_lower or 
               '/asia_data/' in data_path_lower or 'chinese' in data_path_lower)
    
    # 如果路径中没有明确的语言标识，尝试从文件名判断
    if not is_english and not is_asia and os.path.isdir(args.data_path):
        sample_files = [f for f in os.listdir(args.data_path) if f.endswith('.json')][:5]
        asia_lang_count = sum(1 for f in sample_files if any(lang in f for lang in ['中文', '日语', '韩语']))
        eng_lang_count = sum(1 for f in sample_files if any(lang in f for lang in ['英语', '德语', '法语', '西语', '葡语', '俄语', '阿语', '印尼']))
        is_english = eng_lang_count > asia_lang_count
        is_asia = asia_lang_count >= eng_lang_count
    
    if is_english and not is_asia:
        from src_code import process_rule_based_evaluate_eng
        rule_based_evaluate_func = process_rule_based_evaluate_eng.rule_based_evaluate
        print("🔧 Using English/Multi-language evaluation modules")
    else:
        from src_code import process_rule_based_evaluate
        rule_based_evaluate_func = process_rule_based_evaluate.rule_based_evaluate
        print("🔧 Using Asia languages evaluation modules")

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
        current_data = process_all_items(current_data, batch_size=5, rule_based_evaluate_func=rule_based_evaluate_func)
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
    # 如果从命令行直接运行，也可以通过环境变量启用调试
    if os.environ.get('DEBUG') == '1' or os.environ.get('VERBOSE') == '1':
        print("🐛 检测到环境变量 DEBUG/VERBOSE，启用调试模式")
        builtins.print = debug_print
        os.environ['PYTHONUNBUFFERED'] = '1'
    
    main()