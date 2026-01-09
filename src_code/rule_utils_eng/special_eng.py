from src_code.utils_eng import to_lowercase_list

def count_cap_num_helper(strings):
    """统计包含全大写字母内容的字符串数量"""
    count = 0
    for s in strings:
        # 提取所有字母字符
        letters_only = ''.join(c for c in s if c.isalpha())
        # 检查是否有字母且全为大写
        if letters_only and letters_only.isupper():
            count += 1
    return count

def count_low_num_helper(strings):
    """统计包含全小写字母内容的字符串数量"""
    count = 0
    for s in strings:
        # 提取所有字母字符
        letters_only = ''.join(c for c in s if c.isalpha())
        # 检查是否有字母且全为小写
        if letters_only and letters_only.islower():
            count += 1
    return count


def count_cap_num(num, strings):
    # print("here: ", num)
    cap_num = count_cap_num_helper(strings)
    if num != cap_num:
        return 0, f"❌ 大写的数量为{cap_num}, 不符合题目要求的数量：{num}"
    else:
        return 1, "✅ 数量符合"


def count_low_num(num, strings):
    # print("here: ", num)
    cap_num = count_low_num_helper(strings)
    if num != cap_num:
        return 0, f"❌ 小写的数量为{cap_num}, 不符合题目要求的数量：{num}"
    else:
        return 1, "✅ 数量符合"
    
def compound_word_num(range, strings):
    def is_compound_word(word):
        return '-' in word or "'" in word
    for item in strings:
        cnt = 0
        compound_words = []
        words = item.split()
        for word in words:
            if is_compound_word(word): 
                cnt += 1
                compound_words.append(word)
        if not range[0] <= cnt <= range[1]:
            return 0, f"❌ 数量不匹配，产生的复合词数量为：{str(cnt)}, 检测到以下复合词{compound_words}"

    return 1, f"✅ 数量匹配，产生的复合词数量为 {str(cnt)}, 检测到以下复合词{compound_words}"

def no_character_repeat(strings):
    strings = to_lowercase_list(strings)
    for string in strings:
        char_count = {}
        for char in string:
            if char in char_count:
                return 0, f"❌，{string} 中字符 '{char}' 重复出现"
            char_count[char] = 1
    
    return 1, "✅，所有字符串中均无重复字符"

def character_freq(letter, range, strings):
    strings = to_lowercase_list(strings)
    cnt = 0
    for string in strings:
        for char in string:
            if char == letter:
                cnt += 1
    if range[0] <= cnt <= range[1]:
        return 1, f"✅，Letter ‘{letter}’ appears {cnt} times."
    else:
        return 0, f"❌，Letter ‘{letter}’ appears {cnt} times."