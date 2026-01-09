import json
import re
import ast
from math import inf
from typing import Any, List

try:
    import json_repair
    from json_repair import repair_json
    json_repair_AVAILABLE = True
except ImportError:
    json_repair_AVAILABLE = False
    print("json_repair库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "json-repair"])
        print("json_repair库安装成功，正在导入...")
        import json_repair
        from json_repair import repair_json
        json_repair_AVAILABLE = True
        print("✅ json_repair库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install json-repair")
        json_repair_AVAILABLE = False


BATCH_SIZE = 1

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8')  as file:
        data = json.load(file)
    return data

def txt_to_json_og(text):
    json_content = re.search(r'\[.*\]', text, re.DOTALL).group()
    return ast.literal_eval(json_content)

def txt_to_json(text):
    good_json_string = repair_json(text, ensure_ascii=False)
    decoded_object = json_repair.loads(good_json_string)
    return decoded_object

def str_to_lists(text):
    pattern = r'\["(.*?)"\]'
    # 使用正则表达式查找所有匹配内容
    result_list = re.findall(pattern, text, re.DOTALL)
    return result_list

def extract_and_load_json(text):
    # 使用正则表达式提取```json到```之间的内容
    pattern = r'```json(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    
    if not match:
        pattern = r'```(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_content = match.group(1).strip()
    else:
        json_content = text
    # 使用json.loads解析提取的内容
    json_data = json.loads(json_content)
    return json_data


def txt_to_json_braces(text):
    # json_str = extract_json(text)
    # return ast.literal_eval(json_str)
    return extract_and_load_json(text)

def get_json_info_by_key(model_response, prompt):
    key = prompt.split(":")[1]
    processed_model_response = txt_to_json_braces(model_response)
    if isinstance(processed_model_response, list):
        return txt_to_json_braces(model_response)[0][key]
    return txt_to_json_braces(model_response)[key]

def remove_invalid_characters(data):
    if isinstance(data, dict):
        return {key: remove_invalid_characters(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_invalid_characters(element) for element in data]
    elif isinstance(data, str):
        return data.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    else:
        return data

def clean_up_text(text):
    # 先删除所有空格
    text = text.replace(" ", "")
    
    text_after_index = remove_index(text)
    
    # 清理文本，只保留中文、日语、韩语字符
    # \u4e00-\u9fff: 中文汉字
    # \u3040-\u309f: 日语平假名
    # \u30a0-\u30ff: 日语片假名
    # \uac00-\ud7af: 韩语
    cleaned_text = re.sub(r'[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', '', text_after_index)
    
    return cleaned_text

def remove_index(text):
    # 定义各种索引模式
    patterns = [
        r'^\d+\.',          # 12.
        r'^\d+\s*',          # 12 
        r'^\d+\)',          # 12)
        r'^\d+\]',          # 12]
        r'^\d+\}',          # 12}
        r'^\d+、',          # 12、
        r'^\d+\s',          # 12 
        r'^[a-zA-Z]\.',     # a.
        r'^[a-zA-Z]\)',     # a)
        r'^[a-zA-Z]\]',     # a]
        r'^[a-zA-Z]\}',     # a}
        r'^[a-zA-Z]、',     # a、
        r'^[a-zA-Z]\s',     # a 
        r'^[ivxIVX]+\.',    # iv.
        r'^[ivxIVX]+\)',    # iv)
        r'^[ivxIVX]+\]',    # iv]
        r'^[ivxIVX]+\}',    # iv}
        r'^[ivxIVX]+、',    # iv、
        r'^[ivxIVX]+\s',    # iv 
        r'^\(\d+\)',        # (12)
        r'^\([a-zA-Z]\)',   # (a)
        r'^\[[a-zA-Z]\]',   # [a]
        r'^\[\d+\]',        # [12]
        r'^\{[a-zA-Z]\}',   # {a}
        r'^\{\d+\}',        # {12}
    ]
    
    # 合并所有模式
    combined_pattern = '|'.join(patterns)
    
    # 删除匹配到的索引
    result = re.sub(combined_pattern, '', text)
    
    # 删除开头的空白字符
    result = result.lstrip()
    
    return result

def json_parse(json_string: str, keep_undefined: bool = True) -> Any:
    """
    解析JSON字符串，处理特殊值如Infinity、NaN和undefined
    
    Args:
        json_string: 要解析的JSON字符串
        keep_undefined: 是否保留undefined值作为字符串，否则转为None
        
    Returns:
        解析后的Python对象
    """
    def parse_handler(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):  # 使用list()创建副本以便在迭代中修改字典
                if isinstance(v, str):
                    if v == '{{Infinity}}':
                        obj[k] = float('inf')
                    elif v == '{{-Infinity}}':
                        obj[k] = float('-inf')
                    elif v == '{{NaN}}':
                        obj[k] = float('nan')
                    elif v == '{{undefined}}':
                        obj[k] = None if not keep_undefined else v
                    elif re.match(r'^{{"{{(Infinity|NaN|-Infinity|undefined)}}"}}$', v):
                        obj[k] = re.sub(r'^{{"{{(Infinity|NaN|-Infinity|undefined)}}"}}$', r'{{\1}}', v)
        return obj

    # 预处理JSON字符串，处理特殊值
    processed = json_string
    
    # 处理带引号的特殊值
    processed = re.sub(
        r'":\s*"{{(Infinity|NaN|-Infinity|undefined)}}"([,}\n])',
        r':"{{\"{{\\1}}\"}}"\\2',
        processed
    )
    
    # 处理不带引号的特殊值
    processed = re.sub(
        r'":\s*(Infinity|NaN|-Infinity|undefined)([,}\n])',
        r':"{{\\1}}"\\2',
        processed
    )

    try:
        # 尝试解析JSON
        result = json.loads(processed, object_hook=parse_handler)
        return result
    except json.JSONDecodeError:
        # 如果解析失败，尝试清理JSON字符串后再解析
        # 移除可能导致解析错误的控制字符
        cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', processed)
        return json.loads(cleaned, object_hook=parse_handler)


def json_from_string(text: str) -> List[Any]:
    """
    从字符串中提取和解析JSON数据。
    如果顶层是数组，就直接返回那个数组；
    否则把单个对象包装成长度为1的列表返回。
    """
    # 方法1: ast.literal_eval
    try:
        python_obj = ast.literal_eval(text)
        if python_obj is not None:
            if isinstance(python_obj, list):
                return python_obj
            return [python_obj]
    except (SyntaxError, ValueError):
        pass

    # 方法2: json_parse
    try:
        parsed = json_parse(text, True)
        if parsed is not None:
            if isinstance(parsed, list):
                return parsed
            return [parsed]
    except Exception:
        pass

    # 方法3: regex 提取 - 修复重复问题
    # 首先尝试匹配完整的数组
    array_pattern = r'($(?:[^$$]|(?:$[^$$]*$))*$)'
    for match in re.finditer(array_pattern, text, re.DOTALL):
        json_str = match.group(0)
        try:
            parsed_obj = json_parse(json_str, True)
            if parsed_obj is not None and isinstance(parsed_obj, list):
                return parsed_obj  # 直接返回数组，不继续匹配
        except Exception:
            continue
    
    # 如果没有找到数组，再匹配单个对象
    matches = []
    object_pattern = r'(\{(?:[^{}]|(?:\{[^{}]*\}))*\})'
    for match in re.finditer(object_pattern, text, re.DOTALL):
        json_str = match.group(0)
        try:
            parsed_obj = json_parse(json_str, True)
            if parsed_obj is not None:
                matches.append(parsed_obj)
        except Exception:
            continue

    if matches:
        return matches

    raise Exception("Failed to parse JSON from string")


if __name__ == "__main__":
    # rule = "stroke_count_total:24"
    # match = re.search(r'stroke_count_total:(.+)', rule)
    # if match:
    #     structure = match.group(1).strip()
    #     print(structure)
    # else:
    #     print(0, "❌ 规则格式错误，应为 'word_structure:ABAC'") 
    # return word_structure(model_response, structure)
    rule = "count_mixed_chinese_english_words:[1,280]"
    print(txt_to_json_og(rule))