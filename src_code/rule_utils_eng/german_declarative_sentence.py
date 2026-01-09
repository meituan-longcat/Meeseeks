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

# 检查文案总句数是否符合预期
def german_total_sentences(expected_count, model_response):
    actual_count = len(model_response)
    if actual_count == expected_count[0]:
        return True, f"✅ 文案总句数符合要求。我们在题目中要求 {expected_count[0]} 句，实际找到了 {actual_count} 句，数量满足要求。"
    else:
        return False, f"❌ 文案总句数不符合要求。我们在题目中要求 {expected_count[0]} 句，实际找到了 {actual_count} 句，数量不符合要求。"


# 检查文案是否至少有###句数###句正确使用情态动词的一般陈述句
# 情态动词在一般陈述句中的用法:情态动词变位放第二位，搭配的实义动词原形放句尾。  以müssen(必须）和können（可以，能够）为例:  Ich muss(情态动词变位，第二位) heute meine Arbeit erledigen（动词原形，句尾）. 我今天必须完成我的工作。  Thomas kann(情态动词变位，第二位) viele verschiedene Sprachen sprechen（动词原形，句尾）. Thomas能够说许多不同的语言。
def check_declarative_sentence_modal_verbs(expected_count, model_response):

    # 定义情态动词变位列表
    modal_verbs = {
        # 现在时直陈式
        "kann", "kannst", "könnt",
        "muss", "musst", "müsst",
        "darf", "darfst", "dürft",
        "soll", "sollst", "sollt",
        "will", "willst", "wollt",
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

    valid_declarative_sentences = set()  # 用于存储符合条件的句子

    # 使用正则表达式处理每个句子
    for sentence in model_response:
        # 使用 split_words 分割单词
        words = split_words(sentence)
        
        # 检查是否包含情态动词
        has_modal_verb = False
        for word in words:
            if word.lower() in modal_verbs:
                has_modal_verb = True
                break
        
        # 如果包含情态动词，则认为是符合条件的陈述句
        if has_modal_verb:
            valid_declarative_sentences.add(f"\"{sentence}\"")

    # 检查符合条件的句子数量是否符合预期
    valid_declarative_sentences = list(valid_declarative_sentences)  # 转换为列表以便排序和编号
    declarative_count = len(valid_declarative_sentences)

    if declarative_count == 0:
        return False, "❌ 没有提取到任何使用情态动词的一般陈述句"

    if declarative_count < expected_count[0]:
        valid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_declarative_sentences)])
        return False, f"❌ 提取到的使用情态动词的一般陈述句数量不够，应该是不少于 {expected_count[0]} 个，但找到了 {declarative_count} 个，它们分别是：{valid_sentence_str}"

    # 个数符合预期
    valid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_declarative_sentences)])
    return True, f"✅ 提取到的使用情态动词的一般陈述句数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {declarative_count} 个，数量满足要求，它们分别是：{valid_sentence_str}"


# 检查每句正确使用情态动词的一般陈述句的长度是否递增，这里就不能再使用集合了，集合无序
def check_declarative_sentence_length_monotonicity(model_response):

    # 使用check_declarative_sentence_modal_verbs函数找到所有正确使用情态动词的一般陈述句
        # 定义情态动词变位列表
    modal_verbs = {
        # 现在时直陈式
        "kann", "kannst", "könnt",
        "muss", "musst", "müsst",
        "darf", "darfst", "dürft",
        "soll", "sollst", "sollt",
        "will", "willst", "wollt",
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

    valid_declarative_sentences = []  # 用于存储符合条件的句子，保持原始顺序

    # 使用正则表达式处理每个句子
    for sentence in model_response:
        # 使用 split_words 分割单词
        words = split_words(sentence)
        
        # 检查是否包含情态动词
        has_modal_verb = False
        for word in words:
            if word.lower() in modal_verbs:
                has_modal_verb = True
                break
        
        # 如果包含情态动词，则认为是符合条件的陈述句
        if has_modal_verb:
            valid_declarative_sentences.append(sentence)

    declarative_count = len(valid_declarative_sentences)

    if declarative_count == 0:
        return False, "❌ 没有提取到任何使用情态动词的一般陈述句"
    
    # 正则表达式去除标点符号
    cleaned_sentences = [re.sub(r'[^\w\s]', '', sentence) for sentence in valid_declarative_sentences]
    
    # 计算去除标点符号后的句子长度
    sentence_lengths = [len(sentence.split()) for sentence in cleaned_sentences]

    # 检查是否单调递增
    is_monotonic = all(earlier <= later for earlier, later in zip(sentence_lengths, sentence_lengths[1:]))
    
    if is_monotonic:
        return True, "✅ 使用情态动词的一般陈述句长度是单调递增的。"
    else:
        return False, "❌ 使用情态动词的一般陈述句长度不是单调递增的。"




# 测试用例
if __name__ == "__main__":
    # 测试 german_total_sentences
    model_response_1 = [
        "Ich muss heute meine Arbeit erledigen.",
        "Thomas kann viele verschiedene Sprachen sprechen.",
        "Wir dürfen hier nicht parken."
    ]
    result, message = german_total_sentences([3], model_response_1)
    print(message)  # 预期: ✅ 文案总句数符合要求。

    model_response_2 = [
        "Ich muss heute meine Arbeit erledigen.",
        "Thomas kann viele verschiedene Sprachen sprechen."
    ]
    result, message = german_total_sentences([3], model_response_2)
    print(message)  # 预期: ❌ 文案总句数不符合要求。

    # 测试 check_declarative_sentence_modal_verbs
    model_response_3 = [
                "Lebenslauf",
                "Name: Max Mustermann",
                "Kontakt: max.mustermann@email.com",
                "Standort: Shanghai/Peking/Shenzhen",
                "Berufserfahrung:",
                "Ich habe über drei Jahre Erfahrung im Bereich Data Engineering und bin spezialisiert auf die Verarbeitung und Analyse großer Datenmengen.",
                "In meiner letzten Position konnte ich die Datenplattform eines führenden Technologieunternehmens erfolgreich optimieren.",
                "Dabei habe ich eng mit dem F&E-Team zusammengearbeitet, um die Geschäftsanforderungen zu verstehen und effiziente Datenbankabfragen zu entwickeln.",
                "Ich sollte die abteilungsübergreifende Zusammenarbeit koordinieren, um einen reibungslosen Datenfluss zu gewährleisten.",
                "Die Datenqualität und -sicherheit müssen stets sichergestellt werden.",
                "Ich habe kontinuierlich die Datenverarbeitungsprozesse optimiert, um die Systemstabilität und -effizienz zu verbessern.",
                "Die Erstellung professioneller Analyseberichte und die Bereitstellung von Erkenntnissen sind für die datengestützte strategische Entscheidungsfindung des Unternehmens entscheidend.",
                "Bildung:",
                "Bachelor-Abschluss in Informatik von der Universität XYZ.",
                "Fähigkeiten:",
                "Fundierte Kenntnisse in SQL und Erfahrung mit NoSQL-Datenbanken wie MongoDB und Cassandra.",
                "Ich habe Erfahrung mit Cloud-Computing-Plattformen wie AWS und Azure.",
                "Das Design von ETL-Prozessen und die Arbeit mit Big-Data-Plattformen wie Hadoop und Spark sind von Vorteil.",
                "Ich verfüge über ausgezeichnete Kommunikationsfähigkeiten und Teamfähigkeit.",
                "Probleme müssen selbstständig in einem dynamischen Umfeld gelöst werden.",
                "Ich freue mich darauf, Teil Ihres Teams zu werden und die Zukunft der Technologie mitzugestalten."
            ]
    result, message = check_declarative_sentence_modal_verbs([2], model_response_3)
    print(message)  # 预期: ✅ 提取到的使用情态动词的一般陈述句数量符合要求。

    model_response_4 = [
        "Ich gehe heute ins Kino.",
        "Thomas spricht viele verschiedene Sprachen."
    ]
    result, message = check_declarative_sentence_modal_verbs([1], model_response_4)
    print(message) 

    # 测试 check_declarative_sentence_length_monotonicity
    model_response_5 = [
        "Wir dürfen hier nicht parken.",
        "Thomas kann viele verschiedene Sprachen sprechen."
    ]
    result, message = check_declarative_sentence_length_monotonicity(model_response_3)
    print(message) 

    model_response_6 = [
        "Thomas kann viele verschiedene Sprachen sprechen.",
        "Ich muss heute meine Arbeit erledigen.",
        "Wir dürfen hier nicht parken."
    ]
    result, message = check_declarative_sentence_length_monotonicity(model_response_6)
    print(message)  # 预期: ❌ 使用情态动词的一般陈述句长度不是单调递增的。

    model_response_7 = [
        "Ich gehe heute ins Kino.",
        "Thomas spricht viele verschiedene Sprachen."
    ]
    result, message = check_declarative_sentence_length_monotonicity(model_response_7)
    print(message)  # 预期: ❌ 没有提取到任何使用情态动词的一般陈述句
