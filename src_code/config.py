#!/usr/bin/env python3
"""
配置管理模块 - 统一管理API配置
从.env文件或环境变量中读取配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件（如果存在）
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # 尝试从当前工作目录加载
    load_dotenv()

# Qwen API配置
QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'your-qwen-api-key')
QWEN_BASE_URL = os.getenv('QWEN_BASE_URL', 'http://10.164.51.197:8080')
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-model')

# Qwen Coder API配置
QWEN_CODER_API_KEY = os.getenv('QWEN_CODER_API_KEY', 'your-qwen-coder-api-key')
QWEN_CODER_BASE_URL = os.getenv('QWEN_CODER_BASE_URL', 'http://10.166.176.56:8080')
QWEN_CODER_MODEL = os.getenv('QWEN_CODER_MODEL', 'qwen-coder-model')

# Tested Model API配置
TESTED_MODEL_API_KEY = os.getenv('TESTED_MODEL_API_KEY', 'your-tested-model-api-key')
TESTED_MODEL_BASE_URL = os.getenv('TESTED_MODEL_BASE_URL', 'http://10.164.51.197:8080')
TESTED_MODEL_NAME = os.getenv('TESTED_MODEL_NAME', 'default-model')

def print_config():
    """打印当前配置（隐藏敏感信息）"""
    print("📋 Current Configuration:")
    print(f"   - Qwen API Key: {'*' * 10}{QWEN_API_KEY[-4:] if len(QWEN_API_KEY) > 4 else '****'}")
    print(f"   - Qwen Base URL: {QWEN_BASE_URL}")
    print(f"   - Qwen Model: {QWEN_MODEL}")
    print()
    print(f"   - Qwen Coder API Key: {'*' * 10}{QWEN_CODER_API_KEY[-4:] if len(QWEN_CODER_API_KEY) > 4 else '****'}")
    print(f"   - Qwen Coder Base URL: {QWEN_CODER_BASE_URL}")
    print(f"   - Qwen Coder Model: {QWEN_CODER_MODEL}")
    print()
    print(f"   - Tested Model API Key: {'*' * 10}{TESTED_MODEL_API_KEY[-4:] if len(TESTED_MODEL_API_KEY) > 4 else '****'}")
    print(f"   - Tested Model Base URL: {TESTED_MODEL_BASE_URL}")
    print(f"   - Tested Model Name: {TESTED_MODEL_NAME}")