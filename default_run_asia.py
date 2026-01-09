#!/usr/bin/env python3
"""
Meeseeks 亚洲语系数据默认运行脚本
使用预设的API地址和参数运行亚洲语系数据评估
支持语言过滤：--chinese, --japanese, --korean
"""

import subprocess
import sys
import os
import argparse
from dotenv import load_dotenv

def main():
    """运行亚洲语系数据评估"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Meeseeks Asia Languages Data Evaluation')
    parser.add_argument('--chinese', action='store_true', help='只评估中文数据')
    parser.add_argument('--japanese', action='store_true', help='只评估日语数据')
    parser.add_argument('--korean', action='store_true', help='只评估韩语数据')
    args = parser.parse_args()
    
    # 确定要评估的语言
    selected_langs = []
    if args.chinese:
        selected_langs.append('中文')
    if args.japanese:
        selected_langs.append('日语')
    if args.korean:
        selected_langs.append('韩语')
    
    # 如果没有指定任何语言，评估所有语言
    if not selected_langs:
        selected_langs = ['中文', '日语', '韩语']
    
    print("🌏 Starting Meeseeks Asia Languages Data Evaluation")
    print(f"📋 Selected languages: {', '.join(selected_langs)}")
    print("=" * 50)

    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 默认配置参数（从 .env 读取 URL）
    config = {
        "qwen_base_url": os.getenv("QWEN_BASE_URL", "http://10.164.46.86:8080"),
        "qwen_coder_base_url": os.getenv("QWEN_CODER_BASE_URL", "http://10.164.46.199:8080"),
        "tested_model_base_url": os.getenv("TESTED_MODEL_BASE_URL", "http://10.164.46.86:8080"),
        "batch_size": 5,
        "rounds": 2,
        "data_path": "input_data/asia_data/raw_input",
        "output_dir": "evaluation_results_asia",
        "language_filter": ','.join(selected_langs)
    }

    print("🔧 Configuration:")
    for key, value in config.items():
        print(f"   - {key}: {value}")
    print("=" * 50)

    # 构建命令
    cmd = [
        sys.executable, "src_code/run_with_defaults.py",
        "--qwen_base_url", config["qwen_base_url"],
        "--qwen_coder_base_url", config["qwen_coder_base_url"],
        "--tested_model_base_url", config["tested_model_base_url"],
        "--batch_size", str(config["batch_size"]),
        "--rounds", str(config["rounds"]),
        "--data_path", config["data_path"],
        "--output_dir", config["output_dir"],
        "--language_filter", config["language_filter"]
    ]

    try:
        # 运行评估
        print("🚀 Starting evaluation...")
        result = subprocess.run(cmd, check=True)
        print("✅ Asia languages data evaluation completed successfully!")
        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running evaluation: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)