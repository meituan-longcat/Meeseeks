import os
import sys
import re
from typing import Dict, List, Tuple

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from rule_utils.mixed_zh_eng_word_count import count_ENG_words, calculate_chinese_english_word_ratio

def count_chinese_words(text):
    # 统计中文字数（包括中文标点符号）
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    return chinese_count

# def model_each_length(range, model_response):
#     return count_ENG_words(range, model_response)

# def model_total_length(word_range, model_response):
#     total_len = 0
#     for item in model_response:
#         _, english_word_count = model_each_length(word_range, item)
#         total_len += english_word_count
#     if not word_range[0] <= total_len <= word_range[1]:
#         return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
#     return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"


def model_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        # words = model_response.split(" ")
        words = re.split(r'[ \n]+', model_response)
        # 英文字符模式
        english_pattern = r'[a-zA-Z]'
        
        # 统计包含英文字符的单词数量
        english_words = [word for word in words if word and re.search(english_pattern, word)]
        total_len = len(english_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 英文单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：英文单词数是：{str(total_len)}", total_len

def model_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = model_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"


# 检测葡萄牙语单词数(带连字符的葡语复合词应视为一个单词)
def portuguese_each_length(range, corresponding_parts):
    """
    检测葡萄牙语单词数是否在指定范围内
    """
    all_word_counts = []
    all_issues = []
    all_parts_valid = True
    cleaned_items = []  # 保存所有清理后的文本
    
    for i, item in enumerate(corresponding_parts):
        if not isinstance(item, str):
            continue
            
        # 先去除换行符和多余的空白字符
        cleaned_item = re.sub(r'\n+', ' ', item).strip()
        cleaned_items.append(cleaned_item)
        
        # 葡萄牙语单词正则表达式（包含葡语特殊字符和连字符）
        portuguese_word_pattern = r'\b[a-zA-ZáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ-]+\b'
        words = re.findall(portuguese_word_pattern, cleaned_item)
        res_len = len(words)
        all_word_counts.append(res_len)
        
        # 判断当前项是否符合范围
        is_valid = range[0] <= res_len <= range[1]
        if not is_valid:
            all_parts_valid = False
        
        all_issues.append(f"第{i+1}部分: {res_len}个葡萄牙语单词")
    
    # 根据项目数量调整表达
    total_parts = len(all_issues)
    if total_parts == 1:
        # 只有一项
        res_len = all_word_counts[0]
        cleaned_text = cleaned_items[0]
        if all_parts_valid:
            return 1, f"✅ 内容符合范围{range}: {res_len}个葡萄牙语单词", res_len
        else:
            return 0, f"❌ 内容不符合范围{range}: {res_len}个葡萄牙语单词", res_len
    else:
        # 多项
        if all_parts_valid:
            return 1, f"✅ 所有内容都符合范围{range}: {'; '.join(all_issues)}", all_word_counts
        else:
            return 0, f"❌ 存在内容不符合范围{range}: {'; '.join(all_issues)}", all_word_counts


def portuguese_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = portuguese_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"


def arabic_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用非单词字符分割文本（包括空格、标点、数字等）
        words = re.split(r'[ \n]+', model_response)
        
        # 阿拉伯语Unicode范围
        arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
        
        # 统计包含阿拉伯语字符的单词数量
        arabic_words = [word for word in words if word and re.search(arabic_pattern, word)]
        total_len = len(arabic_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 阿拉伯语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：阿拉伯语单词数是：{str(total_len)}", total_len
   
def arabic_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = arabic_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"


# 俄文版
def russian_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = russian_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"

def russian_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        words = re.split(r'[ \n]+', model_response)
        
        # 俄语Unicode范围
        russian_pattern = r'[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]'
        
        # 统计包含俄语字符的单词数量
        russian_words = [word for word in words if word and re.search(russian_pattern, word)]
        total_len = len(russian_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 俄语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：俄语单词数是：{str(total_len)}", total_len

# 法语版
def french_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = french_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"

def french_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        words = re.split(r'[ \n]+', model_response)
        
        # 法语字符模式
        french_pattern = r'[a-zA-ZàâäæçèéêëîïôœùûüÿÀÂÄÆÇÈÉÊËÎÏÔŒÙÛÜŸ]'
        
        # 统计包含法语字符的单词数量
        french_words = [word for word in words if word and re.search(french_pattern, word)]
        total_len = len(french_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 法语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：法语单词数是：{str(total_len)}", total_len

# 西班牙语版
def spanish_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = spanish_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"

def spanish_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        words = re.split(r'[ \n]+', model_response)
        
        # 西班牙语字符模式
        spanish_pattern = r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]'
        
        # 统计包含西班牙语字符的单词数量
        spanish_words = [word for word in words if word and re.search(spanish_pattern, word)]
        total_len = len(spanish_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 西班牙语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：西班牙语单词数是：{str(total_len)}", total_len
 
# 印尼语版 
def indonesian_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = indonesian_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"

def indonesian_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        words = re.split(r'[ \n]+', model_response)
        
        # 印尼语只使用基本拉丁字母
        indonesian_pattern = r'[a-zA-Z]'
        
        # 统计包含拉丁字母的单词数量
        indonesian_words = [word for word in words if word and re.search(indonesian_pattern, word)]
        total_len = len(indonesian_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 印尼语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：印尼语单词数是：{str(total_len)}", total_len

# 德语版
def german_total_length(word_range, model_response):
    total_len = 0
    for item in model_response:
        # 传入一个临时范围，因为我们只需要获取单词数
        _, _, word_count = german_each_length([0, float('inf')], [item])
        total_len += word_count
    if not word_range[0] <= total_len <= word_range[1]:
        return 0, f"❌ 字符数量不匹配此range{word_range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 字符数量匹配，model_response总数量为 {str(total_len)}"

def german_each_length(word_range, model_responses):
    for model_response in model_responses:
        # 使用空格分割文本
        words = re.split(r'[ \n]+', model_response)
        
        # 德语字符模式
        german_pattern = r'[a-zA-ZäöüßÄÖÜẞ]'
        
        # 统计包含德语字符的单词数量
        german_words = [word for word in words if word and re.search(german_pattern, word)]
        total_len = len(german_words)
        
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {model_response} 数量不匹配此范围{word_range}: 德语单词数是：{str(total_len)}", total_len
    
    return 1, f"✅ 数量匹配：德语单词数是：{str(total_len)}", total_len

# 中文+其他语言混合计数
def mixed_chinese_word_count(text: str, target_language: str = "english") -> Dict[str, int]:
    """
    统计混合中文和其他语言的文本中的词汇数量
    
    Args:
        text: 输入文本
        target_language: 目标语言 ("portuguese", "english", "spanish", "french", "german", "russian", "arabic", "indonesian")
    
    Returns:
        Dict: {"chinese_chars": 中文字符数, "target_words": 目标语言单词数, "total_units": 总单位数}
    """
    
    # 语言字符模式定义
    language_patterns = {
        "portuguese": r'[a-zA-ZáàâãçéêíóôõúüÁÀÂÃÇÉÊÍÓÔÕÚÜ]',
        "english": r'[a-zA-Z]',
        "spanish": r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]',
        "french": r'[a-zA-ZàâäæçèéêëîïôœùûüÿÀÂÄÆÇÈÉÊËÎÏÔŒÙÛÜŸ]',
        "german": r'[a-zA-ZäöüßÄÖÜẞ]',
        "russian": r'[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]',
        "arabic": r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
        "indonesian": r'[a-zA-Z]'  # 印尼语使用基本拉丁字母
    }
    
    if target_language not in language_patterns:
        raise ValueError(f"不支持的语言: {target_language}")
    
    # 1. 统计中文字符数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # 2. 提取目标语言单词
    target_pattern = language_patterns[target_language]
    
    # 将文本按非字母字符分割，然后筛选包含目标语言字符的部分
    # 使用更精确的分割模式，保留连续的字母序列
    word_segments = re.findall(r'[^\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', text)
    
    target_words = []
    for segment in word_segments:
        # 进一步按标点符号分割
        words_in_segment = re.findall(r'[a-zA-ZáàâãçéêíóôõúüÁÀÂÃÇÉÊÍÓÔÕÚÜñÑäöüßÄÖÜẞàâäæçèéêëîïôœùûüÿÀÂÄÆÇÈÉÊËÎÏÔŒÙÛÜŸ\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+', segment)
        
        for word in words_in_segment:
            if word and re.search(target_pattern, word):
                target_words.append(word)
    
    target_word_count = len(target_words)
    total_units = chinese_chars + target_word_count
    
    return {
        "chinese_chars": chinese_chars,
        "target_words": target_word_count,
        "target_word_list": target_words,  # 调试用
        "total_units": total_units
    }

def mixed_language_each_length(word_range: List[float], model_responses: List[str], language: str = "english") -> Tuple[int, str, int]:
    """
    检查每个response的混合语言词汇数量是否在范围内
    
    Args:
        word_range: [min, max] 范围
        model_responses: 模型响应列表
        language: 目标语言
    
    Returns:
        Tuple: (是否通过, 消息, 词汇数量)
    """
    for model_response in model_responses:
        chinese_words_count = count_chinese_words(model_response)
        og_model_response = model_response
        model_response = re.sub(r'[\u4e00-\u9fff]+', ' ', model_response)
        model_response = re.sub(r'\s+', ' ', model_response).strip()  # 将多个空格合并为一个

        if language == "english":
            _, _, target_word_count = model_each_length([1,1], [model_response])
        elif language == "portuguese":
            # print(model_response)
            _, _, target_word_count = portuguese_each_length([1,1], [model_response])
        elif language == "arabic":
            _, _, target_word_count = arabic_each_length([1,1], [model_response])
        elif language == "russian":
            _, _, target_word_count = russian_each_length([1,1], [model_response])
        elif language == "french":
            _, _, target_word_count = french_each_length([1,1], [model_response])
        elif language == "spanish":
            _, _, target_word_count = spanish_each_length([1,1], [model_response])
        elif language == "indonesian":
            _, _, target_word_count = indonesian_each_length([1,1], [model_response])
        elif language == "german":
            _, _, target_word_count = german_each_length([1,1], [model_response])

        total_len = target_word_count + chinese_words_count
        if not word_range[0] <= total_len <= word_range[1]:
            return 0, f"❌ {og_model_response} 数量不匹配此范围{word_range}: {language}混合中文总单位数是：{total_len} (中文字符:{chinese_words_count}, {language}单词:{target_word_count})", chinese_words_count, target_word_count
    
    return 1, f"✅ 数量匹配：{language}混合中文总单位数是：{total_len} (中文字符:{chinese_words_count}, {language}单词:{target_word_count})", chinese_words_count, target_word_count


if __name__ == "__main__":
    text = [
"Akhir kata, saya ucapkan terima kasih atas kehadiran dan doa restu dari Bapak, Ibu, keluarga, serta teman-teman semua.   " ] 
    # print(mixed_language_each_length([55.2, 88.1], x, "english"))
    # print("按照split来算：", len(x[0].split(" ")))
    print(indonesian_each_length([1,1], text))