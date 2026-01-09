
import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src_code.utils_eng import to_lowercase_list
from ._clean_up_text import clean_up_text

# 根据接收的language不同，只保留对应language的内容
def model_repeat_each(model_response):
    model_response = to_lowercase_list(model_response)
    cleaned_responses = [clean_up_text(item) for item in model_response]
    
    # 创建字典记录每个元素出现的次数
    item_count = {}
    for item in cleaned_responses:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1
    
    # 找出重复项
    duplicates = [item for item, count in item_count.items() if count > 1]
    
    if duplicates:
        duplicate_info = ", ".join([f"'{item}' (出现{item_count[item]}次)" for item in duplicates])
        return 0, f"❌ 有重复：{duplicate_info}"
    
    return 1, "✅ 无重复"

def model_no_word_repeat(model_response):
    model_response = [clean_up_text(item) for item in model_response]
    # print(model_response)
    for i, item in enumerate(model_response):
        words = [word.lower() for word in item.split()]
        # print(words)
        seen_words = set()
        duplicates = []
        
        for word in words:
            if word in seen_words:
                if word not in duplicates:
                    duplicates.append(word)
            else:
                seen_words.add(word)
        
        if duplicates:
            duplicate_words = ", ".join(duplicates)
            duplicate_info = f"'{duplicate_words}'" if len(duplicate_words) <= 50 else f"'{duplicate_words[:50]}...'({len(duplicates)} words)"
            text_preview = item[:100] + "..." if len(item) > 100 else item
            return 0, f"❌ Text '{text_preview}' has repeated words: 【{duplicate_info}】"
    
    return 1, "✅ No repeated words in any text"

def model_no_char_repeat(model_response):
    model_response = [clean_up_text(item) for item in model_response]
    for i, item in enumerate(model_response):
        english_chars = [char.lower() for char in item if char]
        seen_chars = set()
        duplicates = []
        
        for character in english_chars:
            if character in seen_chars:
                if character not in duplicates:
                    duplicates.append(character)
            else:
                seen_chars.add(character)
        
        if duplicates:
            duplicate_chars = "".join(duplicates)
            duplicate_info = f"'{duplicate_chars}'" if len(duplicate_chars) <= 20 else f"'{duplicate_chars[:20]}...'({len(duplicates)} chars)"
            text_preview = item[:100] + "..." if len(item) > 100 else item
            return 0, f"❌ Text '{text_preview}' has repeated characters: {duplicate_info}"
    
    return 1, "✅ No repeated characters in any text"