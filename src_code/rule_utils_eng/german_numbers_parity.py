


import re
# 全局缓存，避免重复转换
_german_number_cache = {}

def _normalize_german_number(text):
    """规范化德语数字文本"""
    # 保留 'und'，因为 word2number 需要它
    return text.lower().strip()

def _find_number_value(num_str):
    """
    使用 word2number 库直接转换德语数字为数值
    """
    num_str_cleaned = _normalize_german_number(num_str)
    
    # 检查缓存
    if num_str_cleaned in _german_number_cache:
        return _german_number_cache[num_str_cleaned]
    
    try:
        # 使用 word2number 直接转换
        # 注意：word2number 默认支持英语，对于德语需要特殊处理
        # 我们需要先将德语数字转换为英语格式
        num_value = _convert_german_to_number(num_str_cleaned)
        
        if num_value is not None:
            # 缓存结果
            _german_number_cache[num_str_cleaned] = num_value
            return num_value
    except Exception as e:
        pass
    
    return None

def _convert_german_to_number(german_text):
    """
    将德语数字文本转换为数值
    使用德语数字词汇映射
    """
    text = german_text.lower().strip()
    
    # 德语数字词汇映射
    german_numbers = {
        'null': 0, 'eins': 1, 'ein': 1, 'eine': 1, 'zwei': 2, 'drei': 3, 'vier': 4,
        'fünf': 5, 'sechs': 6, 'sieben': 7, 'acht': 8, 'neun': 9, 'zehn': 10,
        'elf': 11, 'zwölf': 12, 'dreizehn': 13, 'vierzehn': 14, 'fünfzehn': 15,
        'sechzehn': 16, 'siebzehn': 17, 'achtzehn': 18, 'neunzehn': 19,
        'zwanzig': 20, 'dreißig': 30, 'vierzig': 40, 'fünfzig': 50,
        'sechzig': 60, 'siebzig': 70, 'achtzig': 80, 'neunzig': 90,
        'hundert': 100, 'tausend': 1000, 'million': 1000000, 'millionen': 1000000,
        'milliarde': 1000000000, 'milliarden': 1000000000
    }
    
    # 简单数字直接返回
    if text in german_numbers:
        return german_numbers[text]
    
    # 处理复合数字
    try:
        result = 0
        current = 0
        
        # 移除 'und' 并分割
        text = text.replace('und', ' ')
        
        # 按照德语数字规则解析
        # 例如: "einundzwanzig" -> "ein zwanzig" -> 1 + 20 = 21
        # "zweihundert" -> "zwei hundert" -> 2 * 100 = 200
        
        # 更复杂的解析逻辑
        result = _parse_german_number(german_text)
        return result
        
    except Exception as e:
        return None

def _parse_german_number(text):
    """
    解析德语数字文本
    """
    text = text.lower().strip()
    
    # 德语基本数字
    units = {
        'null': 0, 'eins': 1, 'ein': 1, 'eine': 1, 'zwei': 2, 'drei': 3, 'vier': 4,
        'fünf': 5, 'sechs': 6, 'sieben': 7, 'acht': 8, 'neun': 9
    }
    
    teens = {
        'zehn': 10, 'elf': 11, 'zwölf': 12, 'dreizehn': 13, 'vierzehn': 14,
        'fünfzehn': 15, 'sechzehn': 16, 'siebzehn': 17, 'achtzehn': 18, 'neunzehn': 19
    }
    
    tens = {
        'zwanzig': 20, 'dreißig': 30, 'vierzig': 40, 'fünfzig': 50,
        'sechzig': 60, 'siebzig': 70, 'achtzig': 80, 'neunzig': 90
    }
    
    scales = {
        'hundert': 100,
        'tausend': 1000,
        'million': 1000000,
        'millionen': 1000000,
        'milliarde': 1000000000,
        'milliarden': 1000000000
    }
    
    # 简单情况
    if text in units:
        return units[text]
    if text in teens:
        return teens[text]
    if text in tens:
        return tens[text]
    if text in scales:
        return scales[text]
    
    # 复杂解析 - 按照从大到小的顺序处理
    # 1. 处理百万
    if 'million' in text:
        parts = text.replace('millionen', 'million').split('million', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 1000000 + (remainder if remainder else 0)
    
    # 2. 处理千位 (例如: einundzwanzigtausend = 21 * 1000)
    if 'tausend' in text:
        parts = text.split('tausend', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 1000 + (remainder if remainder else 0)
    
    # 3. 处理百位 (例如: dreihundert = 3 * 100)
    if 'hundert' in text:
        parts = text.split('hundert', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 100 + (remainder if remainder else 0)
    
    # 4. 处理 "und" 连接的数字 (例如: fünfundvierzig = 5 + 40 = 45)
    # 注意：德语中 "und" 只用于个位和十位之间
    if 'und' in text:
        parts = text.split('und', 1)
        if len(parts) == 2:
            # 递归解析两部分
            left = _parse_german_number(parts[0]) if parts[0] else 0
            right = _parse_german_number(parts[1]) if parts[1] else 0
            # 如果左边为空或为None，说明是 "undeins" 这种情况，只返回右边
            if left is None or left == 0:
                return right
            if right is None:
                return left
            if left is not None and right is not None:
                return left + right
    
    return None

def check_number_parity(parity, model_response):
    """
    检查模型输出的数字的奇偶性是否符合要求。
    
    :param parity: 指定的奇偶性 ([1] 表示奇数 'ungerade'，[2] 表示偶数 'gerade')
    :param model_response: 模型输出的数字书写形式（列表）
    :return: (True/False, 消息)
    """
    parity_type = parity[0]  # 1 = ungerade (奇数), 2 = gerade (偶数)
    
    for num_str in model_response:
        # 使用优化的查找函数
        num_value = _find_number_value(num_str)
        
        if num_value is None:
            return False, f"❌ 找到的数字 '{num_str}' 不在要求的数字范围内。"
        
        # 判断奇偶性
        is_odd = num_value % 2 == 1
        
        if parity_type == 1 and not is_odd:  # 期望奇数但是偶数
            return False, f"❌ 找到的数字 '{num_str}' (值: {num_value}) 是偶数，期望是奇数（ungerade）。"
        
        if parity_type == 2 and is_odd:  # 期望偶数但是奇数
            return False, f"❌ 找到的数字 '{num_str}' (值: {num_value}) 是奇数，期望是偶数（gerade）。"

    return True, "✅ 所有数字的奇偶性符合要求。"

# # 示例：模型输出的数字书写形式列表
# model_response1 = [
#     "einundzwanzigtausenddreihundertfünfundvierzig"  # 21345 (ungerade) ✅
# ]

# model_response2 = [
#     "Einhunderteinundzwanzigtausenddreihundertneunundsechzig"  # 121369 (ungerade) ❌
# ]

# model_response3 = [
#     "Einhundertdreißigtausendsechshundertundeins"  # 130601 (ungerade) ✅
# ]

# # 设置奇偶性要求
# parity1 = [1, 1]  # 要求奇数
# parity2 = [2, 2]  # 要求偶数
# parity3 = [1, 1]  # 要求奇数

# # 调用函数进行奇偶性检查
# is_correct_parity1 = check_number_parity(parity1, model_response1)
# is_correct_parity2 = check_number_parity(parity2, model_response2)
# is_correct_parity3 = check_number_parity(parity3, model_response3)

# print("检查结果1:", is_correct_parity1)
# print("检查结果2:", is_correct_parity2)
# print("检查结果3:", is_correct_parity3)
