def check_words_case(expected_count, model_response):
    if not model_response:
        return False, "❌ 没有提取到期望的阳性弱变化名词列表"
    
    # 检查单词数量是否正确
    if len(model_response) != expected_count[0]:
        return False, f"❌ 提取的阳性弱变化名词数量不正确，应该是 {expected_count[0]} 个，但找到了 {len(model_response)} 个"
    
    # 检查每个单词是否以"n"结尾
    valid_words = [word for word in model_response if word.endswith("n")]
    invalid_words = [word for word in model_response if not word.endswith("n")]
    
    if invalid_words:
        invalid_word_str = ", ".join(invalid_words)
        return False, f"❌ 以下单词未符合阳性弱变化名词的第二、三、四格形态：{invalid_word_str}"

    # 返回符合条件的单词
    valid_word_str = ", ".join(valid_words)
    return True, f"✅ 全部单词符合阳性弱变化名词的第二、三、四格形态：{valid_word_str}"

# 测试数据
word_list = ["Arzten", "Krankenpflegern", "Apotheker"]  # 示例单词，注意 Apothekern 不符合
expected_count = [3,3]  # 期望的数量

# 检查列表中的所有单词是否都以"n"结尾，且数量正确
result = check_words_case(expected_count, word_list)
print(result)


