#!/usr/bin/env python3
"""
Meeseeks English Data Default Run Script
Run English data evaluation with preset API addresses and parameters
Supports language filtering: --english, --german, --french, --spanish, --portuguese, --russian, --arabic, --indonesian
"""

import subprocess
import sys
import os
import argparse
from dotenv import load_dotenv

def main():
    """Run English data evaluation"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Meeseeks English/Multi-language Data Evaluation')
    parser.add_argument('--english', action='store_true', help='只评估英语数据')
    parser.add_argument('--german', action='store_true', help='只评估德语数据')
    parser.add_argument('--french', action='store_true', help='只评估法语数据')
    parser.add_argument('--spanish', action='store_true', help='只评估西语数据')
    parser.add_argument('--portuguese', action='store_true', help='只评估葡语数据')
    parser.add_argument('--russian', action='store_true', help='只评估俄语数据')
    parser.add_argument('--arabic', action='store_true', help='只评估阿语数据')
    parser.add_argument('--indonesian', action='store_true', help='只评估印尼语数据')
    args = parser.parse_args()
    
    # Determine which languages to evaluate
    selected_langs = []
    if args.english:
        selected_langs.append('英语')
    if args.german:
        selected_langs.append('德语')
    if args.french:
        selected_langs.append('法语')
    if args.spanish:
        selected_langs.append('西语')
    if args.portuguese:
        selected_langs.append('葡语')
    if args.russian:
        selected_langs.append('俄语')
    if args.arabic:
        selected_langs.append('阿语')
    if args.indonesian:
        selected_langs.append('印尼')
    
    # If no language specified, evaluate all languages
    if not selected_langs:
        selected_langs = ['英语', '德语', '法语', '西语', '葡语', '俄语', '阿语', '印尼']
    
    print("🌍 Starting Meeseeks English/Multi-language Data Evaluation")
    print(f"📋 Selected languages: {', '.join(selected_langs)}")
    print("=" * 50)

    # Load environment variables from .env file
    load_dotenv()

    # Default configuration parameters (读取 .env 中的 URL)
    config = {
        "qwen_base_url": os.getenv("QWEN_BASE_URL", "http://10.164.46.86:8080"),
        "qwen_coder_base_url": os.getenv("QWEN_CODER_BASE_URL", "http://10.164.46.199:8080"),
        "tested_model_base_url": os.getenv("TESTED_MODEL_BASE_URL", "http://10.164.46.86:8080"),
        "batch_size": 100,
        "rounds": 2,
        "data_path": "input_data/english_data/raw_input",
        "output_dir": "evaluation_results_english",
        "language_filter": ','.join(selected_langs)
    }

    print("🔧 Configuration:")
    for key, value in config.items():
        print(f"   - {key}: {value}")
    print("=" * 50)

    # Build command
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
        # Run evaluation
        print("🚀 Starting evaluation...")
        result = subprocess.run(cmd, check=True)
        print("✅ English data evaluation completed successfully!")
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