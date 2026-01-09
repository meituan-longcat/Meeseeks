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


# 检查段落中的情态动词数量是否符合要求
def check_modal_verbs_count(expected_count, model_response):
    """
    检查输入中是否包含符合期望个数的德语情态动词。

    参数：
        expected_count: 期望个数（int 或 [min_count, max_count] 列表）
        model_response: 输入数据，可以是：
                       - 字符串：整段文本
                       - 句子列表：多个句子，合并后处理
                       - 单词列表：直接处理

    返回：
        (True, message) 如果找到的情态动词数 >= 期望个数
        (False, message) 否则
    
    德语情态动词及其变位：
    - können: kann, kannst, können, könnt
    - müssen: muss, musst, müssen, müsst
    - wollen: will, willst, wollen, wollt
    - sollen: soll, sollst, sollen, sollt
    - dürfen: darf, darfst, dürfen, dürft
    - mögen: mag, magst, mögen, mögt (mag, mochte, gemocht)
    - möchten: möchte, möchtest, möchten, möchtet (polite form)
    """
    
    modal_verbs_set = {
        # 现在时直陈式
        "kann", "kannst", "können", "könnt",
        "muss", "musst", "müssen", "müsst",
        "darf", "darfst", "dürfen", "dürft",
        "soll", "sollst", "sollen", "sollt",
        "will", "willst", "wollen", "wollt",
        # 过去时直陈式
        "konnte", "konntest", "konnten", "konntet",
        "musste", "musstest", "mussten", "musstet",
        "durfte", "durftest", "durften", "durftet",
        "sollte", "solltest", "sollten", "solltet",
        "wollte", "wolltest", "wollten", "wolltet",
        # 虚拟式 II
        "könnte", "könntest", "könnten", "könntet",
        "müsste", "müsstest", "müssten", "müsstet",
        "dürfte", "dürftest", "dürften", "dürftet",
    }
 

    # 处理 expected_count 参数
    if isinstance(expected_count, (list, tuple)):
        min_count = expected_count[0]
    else:
        min_count = expected_count

    # 将输入转换为单词列表
    if isinstance(model_response, str):
        # 字符串输入：按单词边界分割
        words = re.findall(r'\b\w+\b', model_response)
    elif isinstance(model_response, list):
        # 列表输入：合并后按单词边界分割
        if all(isinstance(item, str) for item in model_response):
            combined = " ".join(model_response)
            words = re.findall(r'\b\w+\b', combined)
        else:
            return False, "❌ 输入格式错误：列表中包含非字符串元素"
    else:
        return False, "❌ 输入格式错误：应为字符串、句子列表或单词列表"

    if not words:
        return False, "❌ 没有从输入中提取到任何单词"

    # 找出所有情态动词（不区分大小写）
    found_modal_verbs = [word for word in words if word.lower() in modal_verbs_set]
    
    # 构建情态动词列表字符串
    verbs_str = ", ".join(found_modal_verbs) if found_modal_verbs else "无"
    
    # 检查符合条件的情态动词数量是否达到期望
    if len(found_modal_verbs) >= min_count:
        return True, f"✅ 找到 {len(found_modal_verbs)} 个情态动词，符合要求的至少 {min_count} 个。找到的情态动词是：{verbs_str}。"
    else:
        return False, f"❌ 仅找到 {len(found_modal_verbs)} 个情态动词，应至少为 {min_count} 个。找到的情态动词是：{verbs_str}。"


# ===== 测试代码 =====
if __name__ == "__main__":
    print("=" * 70)
    print("测试 check_modal_verbs_count 函数")
    print("=" * 70)

    # 测试用例 1: 单词列表输入，符合条件
    test1_words = ["kann", "muss", "will"]
    result, msg = check_modal_verbs_count(2, test1_words)
    print(f"\n测试1 (单词列表，符合条件)：")
    print(f"输入: {test1_words}")
    print(f"期望: >= 2 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试1失败"

    # 测试用例 2: 单词列表输入，不符合条件（个数不足）
    test2_words = ["haben", "sein", "gehen"]
    result, msg = check_modal_verbs_count(2, test2_words)
    print(f"\n测试2 (单词列表，个数不足)：")
    print(f"输入: {test2_words}")
    print(f"期望: >= 2 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is False, "测试2失败"

    # 测试用例 3: 字符串输入，符合条件
    test3_str = "Ich kann nicht gehen, weil ich muss arbeiten und will studieren."
    result, msg = check_modal_verbs_count(2, test3_str)
    print(f"\n测试3 (字符串输入，符合条件)：")
    print(f"输入: '{test3_str}'")
    print(f"期望: >= 2 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试3失败"

    # 测试用例 4: 句子列表输入，符合条件
    test4_sentences = [
        "Du kannst das machen.",
        "Wir müssen arbeiten.",
        "Sie wollen spielen."
    ]
    result, msg = check_modal_verbs_count(3, test4_sentences)
    print(f"\n测试4 (句子列表，符合条件)：")
    print(f"输入: {len(test4_sentences)} 个句子")
    print(f"期望: >= 3 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试4失败"

    # 测试用例 5: 混合大小写
    test5_words = ["KANN", "Muss", "WiLl", "soll", "DARF"]
    result, msg = check_modal_verbs_count(5, test5_words)
    print(f"\n测试5 (混合大小写)：")
    print(f"输入: {test5_words}")
    print(f"期望: >= 5 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试5失败"

    # 测试用例 6: 期望个数为列表格式 [min, max]
    test6_words = ["kann", "muss", "darf"]
    result, msg = check_modal_verbs_count([2, 5], test6_words)
    print(f"\n测试6 (期望个数为列表格式)：")
    print(f"输入: {test6_words}")
    print(f"期望: >= 2 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试6失败"

    # 测试用例 7: 字符串，恰好达到期望个数
    test7_str = "Du kannst, du musst und du darfst gehen."
    result, msg = check_modal_verbs_count(3, test7_str)
    print(f"\n测试7 (字符串，恰好达到期望个数)：")
    print(f"输入: '{test7_str}'")
    print(f"期望: >= 3 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试7失败"

    # 测试用例 8: 空输入
    test8_words = []
    result, msg = check_modal_verbs_count(1, test8_words)
    print(f"\n测试8 (空输入)：")
    print(f"输入: {test8_words}")
    print(f"期望: >= 1 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is False, "测试8失败"

    # 测试用例 9: 空字符串
    test9_str = ""
    result, msg = check_modal_verbs_count(1, test9_str)
    print(f"\n测试9 (空字符串)：")
    print(f"输入: '{test9_str}'")
    print(f"期望: >= 1 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is False, "测试9失败"

    # 测试用例 10: 期望个数为 0（应该总是通过）
    test10_words = ["gehen", "haben"]
    result, msg = check_modal_verbs_count(0, test10_words)
    print(f"\n测试10 (期望个数为0)：")
    print(f"输入: {test10_words}")
    print(f"期望: >= 0 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试10失败"

    # 测试用例 11: 包含复杂情态动词变位和混合其他动词
    test11_str = "Ich kann nicht sagen, aber du musst verstehen, dass wir sollen arbeiten, obwohl wir dürfen auch spielen und vielleicht möchten wir tanzen."
    result, msg = check_modal_verbs_count(5, test11_str)
    print(f"\n测试11 (复杂情态动词变位混合)：")
    print(f"输入: '{test11_str}'")
    print(f"期望: >= 5 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试11失败"

    # 测试用例 12: 包含möchte和mögen变位
    test12_words = ["mag", "mögen", "möchte", "möchten"]
    result, msg = check_modal_verbs_count(4, test12_words)
    print(f"\n测试12 (mögen和möchte变位)：")
    print(f"输入: {test12_words}")
    print(f"期望: >= 4 个情态动词")
    print(f"结果: {result}, 信息: {msg}")
    assert result is True, "测试12失败"

    print("\n" + "=" * 70)
    print("✅ 所有测试通过！")
    print("=" * 70)
    