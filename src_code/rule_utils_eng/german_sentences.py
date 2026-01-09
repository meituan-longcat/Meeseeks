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


# # 检查回答的句数是否是奇数
# def check_sentences_count(model_response):



# 检查理由的单词数量是否递增
def german_clause_monotonicity(model_response):
    word_counts = []  # 用于存储每个理由的单词数量

    # 为了避免分句或分词差异导致的计数偏差，直接基于原始句子文本计算词数（去除标点）
    for sentence in model_response:
        cleaned = re.sub(r'[^\w\s]', '', sentence)  # 删除标点
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        count = len(cleaned.split()) if cleaned else 0
        word_counts.append(count)

    # 检查单词数量是否递增
    for i in range(1, len(word_counts)):
        if word_counts[i] <= word_counts[i - 1]:
            return False, f"❌ 理由的单词数量未递增，第 {i+1} 条理由的单词数为 {word_counts[i]}，不大于前一条理由的单词数 {word_counts[i - 1]}。"

    return True, "✅ 理由的单词数量均递增。"


# 检查首尾两条理由的单词数是否都为奇数
def german_clause_odd_even(model_response):
    if not model_response:
        return False, "❌ 理由列表为空，无法检查首尾两条理由的单词数。"

    # 使用 Stanza 处理首条理由
    # 为避免分句/分词差异，直接基于原始句子文本计算词数（去除标点）
    def count_words_from_text(s):
        cleaned = re.sub(r'[^\w\s]', '', s)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return len(cleaned.split()) if cleaned else 0

    first_sentence = model_response[0]
    first_word_count = count_words_from_text(first_sentence)

    # 使用 Stanza 处理尾条理由
    last_sentence = model_response[-1]
    last_word_count = count_words_from_text(last_sentence)

    if first_word_count % 2 == 0:
        return False, f"❌ 首条理由的单词数为 {first_word_count}，不是奇数。"
    if last_word_count % 2 == 0:
        return False, f"❌ 尾条理由的单词数为 {last_word_count}，不是奇数。"

    return True, "✅ 首尾两条理由的单词数均为奇数。"


# 检查回答中奇数句的单词数是否是奇数
def check_word_counts_odd(model_response):
    word_counts = []
    # 遍历文中的每句话
    for sentence in model_response:
        # 使用正则表达式计算单词数，排除标点符号
        words = split_words(sentence)
        word_count = len(words)
        word_counts.append(word_count)
    
    # 检查奇数句（1、3、5...）的单词数是否为奇数
    for i, count in enumerate(word_counts):
        # 只检查奇数位置的句子，注意i从0开始，所以奇数位置是 i % 2 == 0
        if i % 2 == 0:  # 奇数句位置的索引是偶数（0, 2, 4, ...）
            if count % 2 == 0:
                return False, f"❌ 第{i + 1}句是奇数句，但是它的单词数是偶数{count}，终止检查。"
    
    # 如果所有奇数句的单词数都为奇数
    return True, "✅ 所有奇数句的单词数都是奇数。"


# 检查回答中偶数句的单词数是否是偶数
def check_word_counts_even(model_response):
    word_counts = []
    # 遍历文中的每句话
    for sentence in model_response:
        # 使用正则表达式计算单词数，排除标点符号
        words = split_words(sentence)
        word_count = len(words)
        word_counts.append(word_count)
    
    # 检查偶数句（2、4、6...）的单词数是否为偶数
    for i, count in enumerate(word_counts):
        # 只检查偶数位置的句子，注意 i 从 0 开始，所以偶数位置是 i % 2 == 1
        if i % 2 == 1:  # 偶数句位置的索引是奇数（1, 3, 5, ...）
            if count % 2 != 0:
                return False, f"❌ 第{i + 1}句是偶数句，但是它的单词数是奇数{count}，终止检查。"
    
    # 如果所有偶数句的单词数都为偶数
    return True, "✅ 所有偶数句的单词数都是偶数。"


# 检查奇数句的单词数是否单调递增
def check_odd_increase(model_response):
    word_counts = []
    # 遍历文中的每句话
    for sentence in model_response:
        # 使用正则表达式计算单词数，排除标点符号
        words = split_words(sentence)
        word_count = len(words)
        word_counts.append(word_count)
    
    # 存储奇数句的单词数
    odd_sentence_word_counts = []
    for i, count in enumerate(word_counts):
        if i % 2 == 0:  # 奇数句的位置
            odd_sentence_word_counts.append(count)
    
    # 检查奇数句的单词数是否单调递增
    for i in range(1, len(odd_sentence_word_counts)):
        if odd_sentence_word_counts[i] <= odd_sentence_word_counts[i - 1]:
            return False, f"❌ 第{i * 2 + 1}句的单词数不是递增的，{odd_sentence_word_counts[i - 1]} -> {odd_sentence_word_counts[i]}，终止检查。"
    
    # 如果所有奇数句的单词数都单调递增
    return True, "✅ 所有奇数句的单词数是单调递增的。"


# 检查偶数句的单词数是否单调递减
def check_even_decrease(model_response):
    word_counts = []
    # 遍历文中的每句话
    for sentence in model_response:
        # 使用正则表达式计算单词数，排除标点符号
        words = split_words(sentence)
        word_count = len(words)
        word_counts.append(word_count)
    
    # 存储偶数句的单词数
    even_sentence_word_counts = []
    for i, count in enumerate(word_counts):
        if i % 2 == 1:  # 偶数句的位置
            even_sentence_word_counts.append(count)
    
    # 检查偶数句的单词数是否单调递减
    for i in range(1, len(even_sentence_word_counts)):
        if even_sentence_word_counts[i] >= even_sentence_word_counts[i - 1]:
            return False, f"❌ 第{i * 2 + 2}句的单词数不是递减的，{even_sentence_word_counts[i - 1]} -> {even_sentence_word_counts[i]}，终止检查。"
    
    # 如果所有偶数句的单词数都单调递减
    return True, "✅ 所有偶数句的单词数是单调递减的。"




# 测试用例
if __name__ == "__main__":
    model_response_1 = [
                "Studien zeigen, dass Menschen, die früh schlafen und früh aufstehen, eine höhere Produktivität bei der Arbeit erreichen, weil dass diese Gewohnheit den natürlichen Schlaf-Wach-Rhythmus unterstützt und somit die Konzentration und Effizienz steigert. (29 Wörter)",
                "Es wurde beobachtet, dass Studenten, die sich an einen frühen Schlafrhythmus halten, bessere akademische Leistungen erzielen, da dass ein geregelter Schlafplan die kognitive Funktion und das Gedächtnis verbessert. (31 Wörter)",
                "Untersuchungen im Bereich der körperlichen Gesundheit haben ergeben, dass Personen, die früh schlafen und aufstehen, ein geringeres Risiko für Herz-Kreislauf-Erkrankungen haben, weil dass ein stabiler Schlaf-Wach-Zyklus den Blutdruck reguliert und Stress reduziert. (35 Wörter)",
                "Psychologische Studien zeigen, dass Menschen, die früh schlafen und aufstehen, eine bessere emotionale Stabilität aufweisen, da dass ein regelmäßiger Schlafrhythmus die Produktion von Hormonen wie Serotonin und Melatonin fördert, die für das Wohlbefinden wichtig sind. (38 Wörter)",
                "Soziologische Beobachtungen haben ergeben, dass Personen, die früh schlafen und aufstehen, eine stärkere soziale Bindung entwickeln, weil dass diese Gewohnheit mehr Zeit für soziale Interaktionen und gemeinschaftliche Aktivitäten bietet, was das Gefühl der Zugehörigkeit stärkt. (41 Wörter)",
                "Forschungsergebnisse im Bereich der Ernährung zeigen, dass Menschen, die früh schlafen und aufstehen, eine gesündere Ernährungsweise pflegen, da dass ein geregelter Tagesablauf die Planung und Zubereitung von ausgewogenen Mahlzeiten erleichtert und ungesunde Essgewohnheiten reduziert. (44 Wörter)",
                "Eine umfassende Studie zur Lebenszufriedenheit hat gezeigt, dass Menschen, die früh schlafen und aufstehen, insgesamt zufriedener mit ihrem Leben sind, weil dass diese Gewohnheit nicht nur die körperliche und geistige Gesundheit verbessert, sondern auch die Zeit für persönliche Entwicklung und Freizeitaktivitäten maximiert. (49 Wörter)"
    ]

    result3, message3 = german_clause_monotonicity(model_response_1)
    print(message3)  

    result4, message4 = german_clause_odd_even(model_response_1)
    print(message4)  


# response = [
#                 "Teamwork ist im Basketball entscheidend.",
#                 "Kommunikation ist das erste Kernelement.",
#                 "Spieler müssen effektiv miteinander sprechen.",
#                 "Ein Beispiel ist das Rufen von Spielzügen.",
#                 "Vertrauen ist das zweite wichtige Element.",
#                 "Vertraue deinen Mitspielern auf dem Feld.",
#                 "Spieler müssen sich gegenseitig unterstützen.",
#                 "Ein Beispiel ist das Abgeben des Balls.",
#                 "Das dritte Element ist die gemeinsame Strategie.",
#                 "Entwickle eine klare Spielstrategie.",
#                 "Spieler müssen die Strategie verstehen und umsetzen.",
#                 "Ein Beispiel ist das koordinierte Verteidigen.",
#                 "Ein gesunder Lebensstil verbessert die Leistung.",
#                 "Achte auf eine ausgewogene Ernährung.",
#                 "Ernährung beeinflusst die Energie und Ausdauer.",
#                 "Iss ausreichend Proteine und Kohlenhydrate.",
#                 "Erholung ist ebenfalls entscheidend für die Leistung.",
#                 "Schlaf fördert die Regeneration des Körpers.",
#                 "Spieler sollten mindestens acht Stunden schlafen.",
#                 "Vermeide Schlafmangel vor wichtigen Spielen.",
#                 "Mentale Gesundheit ist ebenso wichtig.",
#                 "Halte Stress und Druck unter Kontrolle.",
#                 "Spieler müssen mental stark und fokussiert sein.",
#                 "Nutze Entspannungstechniken zur Stressbewältigung.",
#                 "Zusammenfassend ist Teamwork im Basketball essenziell.",
#                 "Spieler müssen effektiv kommunizieren und vertrauen.",
#                 "Eine gesunde Lebensweise fördert die sportliche Leistung.",
#                 "Achte auf Ernährung, Erholung und mentale Stärke.",
#                 "Diese Faktoren sind entscheidend für den Erfolg.",
#                 "Entwickle gesunde Gewohnheiten für optimale Leistung.",
#                 "Dieser Bericht zeigt, wie Teamwork und ein gesunder Lebensstil die Leistung im Basketball beeinflussen.",
#                 "Spieler, die effektiv kommunizieren, einander vertrauen und eine gemeinsame Strategie verfolgen, sind erfolgreicher.",
#                 "Gleichzeitig ist eine gesunde Lebensweise, einschließlich ausgewogener Ernährung, ausreichender Erholung und guter mentaler Gesundheit, entscheidend für die sportliche Leistung.",
#                 "Indem Spieler diese Aspekte beachten, können sie ihre individuelle und kollektive Leistung maximieren."
#             ]
# result1 = check_word_counts_odd(response)
# result2 = check_word_counts_even(response)
# result3 = check_odd_increase(response)
# result4 = check_even_decrease(response)

# print(result1)
# print(result2)
# print(result3)
# print(result4)