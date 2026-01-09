import re
from ..utils import clean_up_text

def model_each_length(range, model_response):
    res_len = -1
    for item in model_response:
        cleaned_text = clean_up_text(item)
        res_len = len(cleaned_text)
        
        if not range[0] <= res_len <= range[1]:
            return 0, f"❌ 存在内容字符数量不匹配此range{range}: [{str(cleaned_text)}] 数量为：{str(res_len)}"
    return 1, f"✅ 全部内容字符数量匹配"


def model_total_length(range, model_response):
    total_len = 0
    for item in model_response:
        cleaned_text = clean_up_text(item)
        res_len = len(cleaned_text)
        total_len += res_len
    if not range[0] <= total_len <= range[1]:
        return 0, f"❌ 清理后的字符数量不匹配此range{range}: model_response总数量为：{str(total_len)}"
    return 1, f"✅ 清理后的字符数量匹配，model_response总数量为 {str(total_len)}"

def model_item_count(range, model_response):
    res_len = len(model_response)
    if not range[0] <= res_len <= range[1]:
        return 0, f"❌ 数量不匹配，产生的item数量为：{str(res_len)}"
    return 1, f"✅ 数量匹配，产生的item数量为 {str(res_len)}"

def model_repeat_each(model_response):
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
    model_response = [clean_up_text(i) for i in model_response]
    
    all_characters = []
    duplicates = []
    
    for item in model_response:
        for character in item:
            if character not in all_characters:
                all_characters.append(character)
            elif character not in duplicates:
                # 如果字符已经在all_characters中但还不在duplicates中，
                # 则将其添加到duplicates列表中
                duplicates.append(character)
    
    if duplicates:
        # 格式化重复字符的输出，明确指出哪些字符重复了
        if len(duplicates) <= 10:
            duplicate_list = "、".join([f"'{char}'" for char in duplicates])
            duplicate_info = f"字符 {duplicate_list} 出现重复"
        else:
            duplicate_list = "、".join([f"'{char}'" for char in duplicates[:10]])
            duplicate_info = f"字符 {duplicate_list} 等{len(duplicates)}个字符出现重复"
        
        return 0, f"❌ 检测到重复: {duplicate_info}"
    
    return 1, "✅ 无重复"


def model_each_no_word_repeat (model_response):
    model_response = [clean_up_text(i) for i in model_response]
    
    all_duplicates = []
    failed_parts = []
    
    # 对每个部分分别检查重复
    for idx, item in enumerate(model_response):
        characters_in_item = []
        duplicates_in_item = []
        
        for character in item:
            if character not in characters_in_item:
                characters_in_item.append(character)
            elif character not in duplicates_in_item:
                duplicates_in_item.append(character)
        
        # 如果当前部分有重复字符
        if duplicates_in_item:
            failed_parts.append(idx)
            all_duplicates.extend(duplicates_in_item)
    
    # 只有所有部分都没有重复才返回成功
    if all_duplicates:
        # 去重并格式化输出
        unique_duplicates = list(dict.fromkeys(all_duplicates))  # 保持顺序的去重
        
        if len(unique_duplicates) <= 10:
            duplicate_list = "、".join([f"'{char}'" for char in unique_duplicates])
            duplicate_info = f"字符 {duplicate_list} 出现重复"
        else:
            duplicate_list = "、".join([f"'{char}'" for char in unique_duplicates[:10]])
            duplicate_info = f"字符 {duplicate_list} 等{len(unique_duplicates)}个字符出现重复"
        
        failed_parts_info = "、".join([f"第{i+1}部分" for i in failed_parts])
        return 0, f"❌ 检测到重复: {duplicate_info} (出现在{failed_parts_info})"
    
    return 1, "✅ 所有部分均无重复"


def model_no_word_eachrepeat(model_response):
    model_response = [clean_up_text(i) for i in model_response]
    
    all_duplicates = []
    failed_parts = []
    
    # 对每个部分分别检查重复
    for idx, item in enumerate(model_response):
        characters_in_item = []
        duplicates_in_item = []
        
        for character in item:
            if character not in characters_in_item:
                characters_in_item.append(character)
            elif character not in duplicates_in_item:
                duplicates_in_item.append(character)
        
        # 如果当前部分有重复字符
        if duplicates_in_item:
            failed_parts.append(idx)
            all_duplicates.extend(duplicates_in_item)
    
    # 只有所有部分都没有重复才返回成功
    if all_duplicates:
        # 去重并格式化输出
        unique_duplicates = list(dict.fromkeys(all_duplicates))  # 保持顺序的去重
        
        if len(unique_duplicates) <= 10:
            duplicate_list = "、".join([f"'{char}'" for char in unique_duplicates])
            duplicate_info = f"字符 {duplicate_list} 出现重复"
        else:
            duplicate_list = "、".join([f"'{char}'" for char in unique_duplicates[:10]])
            duplicate_info = f"字符 {duplicate_list} 等{len(unique_duplicates)}个字符出现重复"
        
        failed_parts_info = "、".join([f"第{i+1}部分" for i in failed_parts])
        return 0, f"❌ 检测到重复: {duplicate_info} (出现在{failed_parts_info})"
    
    return 1, "✅ 所有部分均无重复"


def model_non_very_similar(sentences_list):
    # 如果有两个句子的文字使用复合率超过75%，则认为不匹配
    for i in range(len(sentences_list)):
        sentences_list[i] = clean_up_text(sentences_list[i])

    def calculate_similarity(sentence1, sentence2):
        # 将句子转换为字符集合
        chars1 = set(sentence1)
        chars2 = set(sentence2)
        
        # 计算共有字符的数量
        common_chars = chars1.intersection(chars2)
        
        # 计算复合率
        total_chars = len(chars1) + len(chars2)
        if total_chars == 0:
            return 0
        similarity_rate = (2 * len(common_chars)) / total_chars
        return similarity_rate

    # 遍历所有句子对
    for i in range(len(sentences_list)):
        for j in range(i + 1, len(sentences_list)):
            sentence1 = sentences_list[i]
            sentence2 = sentences_list[j]
            similarity_rate = calculate_similarity(sentence1, sentence2)
            
            # 判断复合率是否超过75%
            if similarity_rate > 0.75:
                return 0, f"❌ 句子对不匹配因为相似度过高: \n1: {sentence1}\n2: {sentence2}\n相似度: {similarity_rate:.2f}"
    return 1, "✅ 无特别相似"