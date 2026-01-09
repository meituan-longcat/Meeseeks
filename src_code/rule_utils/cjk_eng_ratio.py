import re

def calculate_chinese_english_word_ratio(text):
    # 统计中文字数
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    
    # 统计英文单词数
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)
    
    return chinese_count, english_word_count

def chinese_english_ratio(ratio, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else chinese_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ 不匹配: 中文字符数：{str(chinese_count)}，英文单词数：{str(english_word_count)}，比例：{real_ratio}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ 匹配"

def count_mixed_chinese_english_words(range, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        if not range[0] <= chinese_count + english_word_count <= range[1]:
            return 0, f"❌ 数量不匹配此范围{range}: 模型回答中的中文字符数是：{str(chinese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(chinese_count + english_word_count)}"
    return 1, f"✅ 数量匹配：模型回答中的中文字符数是：{str(chinese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(chinese_count + english_word_count)}"


def calculate_korean_english_word_ratio(text):
    # 统计韩文字数
    korean_count = sum(1 for char in text if '\uac00' <= char <= '\ud7af')
    
    # 统计英文单词数
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)
    
    return korean_count, english_word_count

def korean_english_ratio(ratio, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        korean_count, english_word_count = calculate_korean_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else korean_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ 不匹配: 韩文字符数：{str(korean_count)}，英文单词数：{str(english_word_count)}，比例：{real_ratio}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ 匹配"

def count_mixed_korean_english_words(range, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        korean_count, english_word_count = calculate_korean_english_word_ratio(model_response)
        if not range[0] <= korean_count + english_word_count <= range[1]:
            return 0, f"❌ 数量不匹配此范围{range}: 模型回答中的韩文字符数是：{str(korean_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(korean_count + english_word_count)}"
    return 1, f"✅ 数量匹配：模型回答中的韩文字符数是：{str(korean_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(korean_count + english_word_count)}"

def calculate_japanese_english_word_ratio(text):
    # 统计日文字数（包括平假名、片假名和汉字）
    japanese_count = sum(1 for char in text if 
                        ('\u3040' <= char <= '\u309f') or  # 平假名
                        ('\u30a0' <= char <= '\u30ff') or  # 片假名
                        ('\u4e00' <= char <= '\u9fff'))    # 汉字（CJK统一汉字）
    
    # 统计英文单词数
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)
    
    return japanese_count, english_word_count

def japanese_english_ratio(ratio, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        japanese_count, english_word_count = calculate_japanese_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else japanese_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ 不匹配: 日文字符数：{str(japanese_count)}，英文单词数：{str(english_word_count)}，比例：{real_ratio}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ 匹配"

def count_mixed_japanese_english_words(range, model_responses):
    # 如果model_responses是字符串，转换为列表
    if isinstance(model_responses, str):
        model_responses = [model_responses]
    
    for model_response in model_responses:
        japanese_count, english_word_count = calculate_japanese_english_word_ratio(model_response)
        if not range[0] <= japanese_count + english_word_count <= range[1]:
            return 0, f"❌ 数量不匹配此范围{range}: 模型回答中的日文字符数是：{str(japanese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(japanese_count + english_word_count)}"
    return 1, f"✅ 数量匹配：模型回答中的日文字符数是：{str(japanese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(japanese_count + english_word_count)}"




if __name__ == "__main__":
    # # ==================== 测试用例 ====================

    # # 测试 count_mixed_chinese_english_words 函数
    # print("=" * 80)
    # print("测试 count_mixed_chinese_english_words 函数")
    # print("=" * 80)

    # # 测试用例1：中文字符数 + 英文单词数 = 15，范围 [10, 20]，应该通过
    # print("\n【测试用例1】中文字符数 + 英文单词数在范围内")
    # text1 = "这是一个测试文本，包含了中文和English单词。"
    # # 中文字符：这是一个测试文本包含了中文和 = 15个
    # # 英文单词：English = 1个
    # # 总数：15 + 1 = 16
    # result1 = count_mixed_chinese_english_words([10, 20], [text1])
    # print(f"输入文本：{text1}")
    # print(f"范围：[10, 20]")
    # print(f"结果：{result1}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例2：中文字符数 + 英文单词数 = 5，范围 [10, 20]，应该失败
    # print("\n【测试用例2】中文字符数 + 英文单词数超出范围（太少）")
    # text2 = "中文test"
    # # 中文字符：中文 = 2个
    # # 英文单词：test = 1个
    # # 总数：2 + 1 = 3
    # result2 = count_mixed_chinese_english_words([10, 20], [text2])
    # print(f"输入文本：{text2}")
    # print(f"范围：[10, 20]")
    # print(f"结果：{result2}")
    # print(f"预期：(0, '❌ 数量不匹配此范围...')")

    # # 测试用例3：中文字符数 + 英文单词数 = 25，范围 [10, 20]，应该失败
    # print("\n【测试用例3】中文字符数 + 英文单词数超出范围（太多）")
    # text3 = "这是一个很长的中文测试文本，包含了很多中文字符和多个English单词以及another单词。"
    # # 中文字符：这是一个很长的中文测试文本包含了很多中文字符和多个以及 = 30个
    # # 英文单词：English, another = 2个
    # # 总数：30 + 2 = 32
    # result3 = count_mixed_chinese_english_words([10, 20], [text3])
    # print(f"输入文本：{text3}")
    # print(f"范围：[10, 20]")
    # print(f"结果：{result3}")
    # print(f"预期：(0, '❌ 数量不匹配此范围...')")

    # # 测试用例4：多个文本，都在范围内
    # print("\n【测试用例4】多个文本都在范围内")
    # texts4 = ["中文test", "测试English", "文本words"]
    # # 文本1：中文 + test = 2 + 1 = 3
    # # 文本2：测试 + English = 2 + 1 = 3
    # # 文本3：文本 + words = 2 + 1 = 3
    # result4 = count_mixed_chinese_english_words([1, 10], texts4)
    # print(f"输入文本：{texts4}")
    # print(f"范围：[1, 10]")
    # print(f"结果：{result4}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例5：多个文本，其中一个超出范围
    # print("\n【测试用例5】多个文本中有一个超出范围")
    # texts5 = ["中文test", "这是一个很长的中文测试文本，包含了很多中文字符和多个English单词以及another单词。"]
    # # 文本1：中文 + test = 2 + 1 = 3（在范围内）
    # # 文本2：30 + 2 = 32（超出范围）
    # result5 = count_mixed_chinese_english_words([1, 10], texts5)
    # print(f"输入文本：{texts5}")
    # print(f"范围：[1, 10]")
    # print(f"结果：{result5}")
    # print(f"预期：(0, '❌ 数量不匹配此范围...')")

    # # 测试用例6：只有中文，没有英文
    # print("\n【测试用例6】只有中文，没有英文单词")
    # text6 = "这是一个纯中文的测试文本"
    # # 中文字符：这是一个纯中文的测试文本 = 13个
    # # 英文单词：0个
    # # 总数：13 + 0 = 13
    # result6 = count_mixed_chinese_english_words([10, 20], [text6])
    # print(f"输入文本：{text6}")
    # print(f"范围：[10, 20]")
    # print(f"结果：{result6}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例7：只有英文，没有中文
    # print("\n【测试用例7】只有英文，没有中文字符")
    # text7 = "This is a pure English text"
    # # 中文字符：0个
    # # 英文单词：This, is, a, pure, English, text = 6个
    # # 总数：0 + 6 = 6
    # result7 = count_mixed_chinese_english_words([1, 10], [text7])
    # print(f"输入文本：{text7}")
    # print(f"范围：[1, 10]")
    # print(f"结果：{result7}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例8：边界值测试 - 恰好等于范围最小值
    # print("\n【测试用例8】边界值测试 - 恰好等于范围最小值")
    # text8 = "中test"
    # # 中文字符：中 = 1个
    # # 英文单词：test = 1个
    # # 总数：1 + 1 = 2
    # result8 = count_mixed_chinese_english_words([2, 10], [text8])
    # print(f"输入文本：{text8}")
    # print(f"范围：[2, 10]")
    # print(f"结果：{result8}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例9：边界值测试 - 恰好等于范围最大值
    # print("\n【测试用例9】边界值测试 - 恰好等于范围最大值")
    # text9 = "中文测试test"
    # # 中文字符：中文测试 = 4个
    # # 英文单词：test = 1个
    # # 总数：4 + 1 = 5
    # result9 = count_mixed_chinese_english_words([1, 5], [text9])
    # print(f"输入文本：{text9}")
    # print(f"范围：[1, 5]")
    # print(f"结果：{result9}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # # 测试用例10：包含特殊字符和数字
    # print("\n【测试用例10】包含特殊字符和数字")
    # text10 = "中文123test!@#"
    # # 中文字符：中文 = 2个
    # # 英文单词：test = 1个
    # # 总数：2 + 1 = 3（特殊字符和数字不计入）
    # result10 = count_mixed_chinese_english_words([1, 10], [text10])
    # print(f"输入文本：{text10}")
    # print(f"范围：[1, 10]")
    # print(f"结果：{result10}")
    # print(f"预期：(1, '✅ 数量匹配...')")

    # print("\n" + "=" * 80)
    # print("测试完成")
    # print("=" * 80)

    text11 = "Hi大家好！我是一个大学生，major in Computer Science，现在已经大三了。平时最大的hobby就是熬夜写代码，debug到凌晨三点已经是我的daily routine。有时候我debug到天昏地暗，饭都忘了吃，感觉自己快要变成“代码左拥右抱”的人了。我的生活除了代码，还有一只超级可爱的柯基，名字叫“小笼包”，它的腿虽然短，但跑起来左冲右突，简直萌翻了！\n\n性格方面，我是个社恐，offline见人就“左顾右盼”，但在网上却是话痨，能和大家聊到天南地北，左一句右一句停不下来。Sometimes我觉得自己是“左手社恐，右手社牛”，人格分裂现场。希望在这个小组里，能遇到更多和我一样喜欢中英文夹杂的朋友，一起左聊右聊，快乐无边！\n\n最后，I really love this group，感觉这里就是我的comfort zone，大家都so cool！期待和大家一起make some fun memories！"

    result11 = count_mixed_chinese_english_words([1,320],[text11])