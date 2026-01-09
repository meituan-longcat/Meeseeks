import re

# 尝试导入 HanTa 库
try:
    from HanTa import HanoverTagger as ht
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    HANTA_AVAILABLE = True
except ImportError:
    HANTA_AVAILABLE = False
    print("HanTa库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "HanTa", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("HanTa库安装成功，正在导入...")
        from HanTa import HanoverTagger as ht
        tagger = ht.HanoverTagger('morphmodel_ger.pgz')
        HANTA_AVAILABLE = True
        print("✅ HanTa库已成功导入")
    except Exception as e:
        print(f"❌ HanTa自动安装失败: {e}")
        print("请手动运行: pip install HanTa")
        HANTA_AVAILABLE = False
        tagger = None
except Exception as e:
    print(f"❌ HanTa初始化失败: {e}")
    HANTA_AVAILABLE = False
    tagger = None

# 使用 HanTa 或正则表达式来分割词汇

def split_words(text):
    """
    使用 HanTa 库或正则表达式分割德语文本为单词
    HanTa 可以更准确地识别德语单词边界
    """
    if HANTA_AVAILABLE and tagger is not None:
        try:
            # 使用 HanTa 进行分词
            # HanTa 返回 (word, lemma, pos_tag) 三元组列表
            tokens = tagger.tag_sent(text.split())
            # 提取单词部分
            words = []
            for token in tokens:
                if isinstance(token, tuple) and len(token) >= 1:
                    words.append(token[0])  # 第一个元素是原始单词
                else:
                    words.append(str(token))
            return words
        except Exception as e:
            # 如果 HanTa 失败，回退到正则表达式
            pass
    
    # 备用方法：使用正则表达式匹配单词（包括带连字符的复合词）
    words = re.findall(r'\b[\w\-]+\b', text, re.UNICODE)
    return words


def check_conjunctions_per_sentence(conjunction_range, model_response):
    conjunctions = ["aber", "denn", "und", "sondern", "oder"]
    
    # 遍历每个句子
    for idx, sentence in enumerate(model_response):
        # 统计该句子中的不占位连词个数
        conjunction_count = sum(conjunction in sentence for conjunction in conjunctions)

        # 如果该句子不恰好包含 count 个连词
        if conjunction_count != conjunction_range[0]:
            return 0, f"❌ 句子 {idx + 1} 的不占位连词个数为 {conjunction_count}，应恰好为 {conjunction_range[0]} 个。"

    # 如果所有句子的连词个数都符合要求
    return 1, "✅ 所有句子中的不占位连词数量都符合要求。"

# 示例规则
# conjunction_range = [2]  # 每个句子应包含 2 个连词
# model_response = [
#     "Es regnet, aber wir gehen trotzdem raus.",
#     "Wir haben keine Zeit, denn der Zug fährt bald.",
#     "Er ging nach Hause, und sie blieben im Park.",
#     "Ich möchte einen Apfel, oder eine Birne.",
#     "Sie isst Pizza, sondern mag eigentlich lieber Pasta."
# ]

# # 执行检查
# result, message = check_conjunctions_per_sentence(conjunction_range, model_response)
# print(result, message)


# 检查段落中是否依次出现aber, denn, und, sondern, oder这5个不占位连词
def check_conjunctions_order(model_response):
    """
    检查整个段落中是否按顺序依次出现不占位连词列表：
    ["aber", "denn", "und", "sondern", "oder"]。

    输入可为字符串（整段）或句子列表；匹配时忽略大小写并使用词边界。
    返回 (1, message) 表示通过；(0, message) 表示失败并给出原因。
    """
    conjunctions = ["aber", "denn", "und", "sondern", "oder"]

    # 支持字符串或句子列表输入
    if isinstance(model_response, list):
        text = " ".join(model_response)
    else:
        text = str(model_response)

    text_low = text.lower()

    positions = []
    # 从段落开头开始查找，每找到一个连词就从该位置之后继续查找下一个
    search_offset = 0
    for conj in conjunctions:
        pattern = r"\b" + re.escape(conj) + r"\b"
        m = re.search(pattern, text_low[search_offset:])
        if not m:
            # 未在剩余文本中找到该连词，尝试检查段落中是否根本不存在该连词
            if not re.search(pattern, text_low):
                return 0, f"❌ 未找到连词 '{conj}'。段落中应依次出现 {', '.join(conjunctions)}。"
            # 如果存在但不在正确顺序（出现在前面的剩余部分），说明顺序错误
            first_overall = re.search(pattern, text_low).start()
            return 0, (f"❌ 连词 '{conj}' 的出现位置违反顺序（首次出现在字符索引 {first_overall + 1}），"
                       f"应在之前连词之后出现。")

        found_index = search_offset + m.start()
        positions.append((conj, found_index))
        # 更新下次搜索的偏移（跳过当前匹配的整个单词）
        search_offset = found_index + len(m.group(0))

    # 如果所有连词都按顺序找到，返回成功并给出每个连词的字符位置（从1开始）
    pos_msg = ", ".join([f"'{c}'@{p + 1}" for c, p in positions])
    return 1, f"✅ 段落中按顺序找到所有连词：{pos_msg}。"


# ===== 测试代码 =====
if __name__ == "__main__":
    print("=" * 60)
    print("测试 check_conjunctions_order 函数")
    print("=" * 60)

    # 测试用例 1: 完整段落（按顺序包含所有5个连词）
    test1 = "Es regnet, ABER wir gehen trotzdem raus. Wir haben keine Zeit, Denn der Zug fährt bald. Er ging nach Hause, UND sie blieben im Park. Ich möchte einen Apfel, SONDERN eine Birne. Wir können hoffen ODER nicht."
    result, msg = check_conjunctions_order(test1)
    print(f"\n测试1 (完整段落)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 1, "测试1失败"

    # 测试用例 2: 句子列表输入
    test2 = [
        "Es regnet, aber wir gehen trotzdem raus.",
        "Wir haben keine Zeit, denn der Zug fährt bald.",
        "Er ging nach Hause, und sie blieben im Park.",
        "Ich möchte einen Apfel, sondern eine Birne.",
        "Wir können hoffen oder nicht."
    ]
    result, msg = check_conjunctions_order(test2)
    print(f"\n测试2 (句子列表)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 1, "测试2失败"

    # 测试用例 3: 缺少某个连词
    test3 = "Es regnet, aber wir gehen trotzdem raus. Wir haben keine Zeit, denn der Zug fährt bald. Er ging nach Hause, und sie blieben im Park. Wir können hoffen oder nicht."
    result, msg = check_conjunctions_order(test3)
    print(f"\n测试3 (缺少 'sondern')：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 0, "测试3失败"

    # 测试用例 4: 连词顺序错误（denn 在 aber 之前）
    test4 = "Wir haben keine Zeit, denn der Zug fährt bald. Es regnet, aber wir gehen trotzdem raus. Er ging nach Hause, und sie blieben im Park. Ich möchte einen Apfel, sondern eine Birne. Wir können hoffen oder nicht."
    result, msg = check_conjunctions_order(test4)
    print(f"\n测试4 (连词顺序错误)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 0, "测试4失败"

    # 测试用例 5: 只有前三个连词
    test5 = "Es regnet, aber wir gehen trotzdem raus. Wir haben keine Zeit, denn der Zug fährt bald. Er ging nach Hause, und sie blieben im Park."
    result, msg = check_conjunctions_order(test5)
    print(f"\n测试5 (只有前三个连词)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 0, "测试5失败"

    # 测试用例 6: 大小写混合
    test6 = "Es regnet, AbEr wir gehen trotzdem raus. Wir haben keine Zeit, DENN der Zug fährt bald. Er ging nach Hause, uNd sie blieben im Park. Ich möchte einen Apfel, SoNdErN eine Birne. Wir können hoffen ODER nicht."
    result, msg = check_conjunctions_order(test6)
    print(f"\n测试6 (大小写混合)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 1, "测试6失败"

    # 测试用例 7: 空字符串
    test7 = ""
    result, msg = check_conjunctions_order(test7)
    print(f"\n测试7 (空字符串)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 0, "测试7失败"

    # 测试用例 8: 包含连词的单词被正确识别（词边界测试）
    test8 = "Es ist aber nicht wunderbar. Denn die Schande ist groß. Und Menschen sagen sondern denken oder schweigen."
    result, msg = check_conjunctions_order(test8)
    print(f"\n测试8 (词边界测试)：")
    print(f"结果: {result}, 信息: {msg}")
    assert result == 1, "测试8失败"

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
