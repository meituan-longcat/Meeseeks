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


# 检查内容中是否同时出现由'Weil', 'Dass' 和 'Obwohl'引导的从句
def check_three_conjunctions(model_response):
    # 定义正则表达式，用于查找"weil"、"dass"和"obwohl"引导的从句
    weil_pattern = r"\bweil\b"
    dass_pattern = r"\bdass\b"
    obwohl_pattern = r"\bobwohl\b"

   # 提取信件
    text = model_response[0]  # 假设 model_response 是一个包含一个字符串的列表

    # 检查是否存在这些从句
    has_weil = bool(re.search(weil_pattern, text, re.IGNORECASE))
    has_dass = bool(re.search(dass_pattern, text, re.IGNORECASE))
    has_obwohl = bool(re.search(obwohl_pattern, text, re.IGNORECASE))

    # 如果不同时包含所有三个从句，找出缺失的部分
    missing_conjunctions = []
    if not has_weil:
        missing_conjunctions.append("Weil")
    if not has_dass:
        missing_conjunctions.append("Dass")
    if not has_obwohl:
        missing_conjunctions.append("Obwohl")

    if missing_conjunctions:
        return False, f"❌ 缺少从句引导词：{', '.join(missing_conjunctions)}"
    else:
        return True, "✅ 包含了所有三个从句引导词：Weil, Dass 和 Obwohl"


# 每个理由的从句是否以###从句连词###引导
def german_clause_conjunction(conjunction, model_response):
    invalid_sentences = []  # 用于存储不符合条件的从句

    # 使用正则表达式处理每个从句
    for sentence in model_response:
        words = split_words(sentence)
        
        # 查找从句开头是否是指定的从句连词
        if len(words) > 0 and words[0].lower() != conjunction.lower():
            invalid_sentences.append(f"\"{sentence}\"")

    if not invalid_sentences:
        return True, "✅ 所有从句均以指定连词引导。"
    else:
        invalid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(invalid_sentences)])
        return False, f"❌ 以下从句未以指定连词{conjunction}引导：\n{invalid_sentence_str}"
    

# 检查德语从句的动词是否位于从句句尾
def german_clause_verb(model_response):
    """
    使用 HanTa 库检查德语从句的动词是否位于句尾
    如果 HanTa 不可用，则使用备用的动词列表
    """
    invalid_sentences = []  # 用于存储不符合条件的从句

    if HANTA_AVAILABLE and tagger is not None:
        # 使用 HanTa 库进行词性标注
        for sentence in model_response:
            words = split_words(sentence)
            
            # 去除标点符号(包括单词末尾的标点)
            non_punct_words = []
            for w in words:
                # 去除单词两端的标点符号
                cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', w, flags=re.UNICODE)
                if cleaned:  # 如果去除标点后还有内容
                    non_punct_words.append(cleaned)
            
            if not non_punct_words:
                invalid_sentences.append(f"\"{sentence}\"")
                continue
            
            # 使用 HanTa 标注最后一个单词
            last_word = non_punct_words[-1]
            try:
                # HanTa 返回 (word, lemma, pos_tag) 三元组
                tags = tagger.tag_sent([last_word])
                if tags:
                    tag_result = tags[0]
                    # 处理不同的返回格式
                    if isinstance(tag_result, tuple):
                        if len(tag_result) == 3:
                            # (word, lemma, pos_tag)
                            word, lemma, pos_tag = tag_result
                        elif len(tag_result) == 2:
                            # (lemma, pos_tag)
                            lemma, pos_tag = tag_result
                        else:
                            # 未知格式，使用备用方法
                            raise ValueError(f"未知的标注格式: {tag_result}")
                    else:
                        # 单个值，可能是字符串
                        raise ValueError(f"未知的标注格式: {tag_result}")
                    
                    # 检查词性标签是否为动词 (V 开头表示动词)
                    # VVFIN, VVINF, VVPP, VAFIN, VAINF, VAPP, VMFIN, VMINF, VMPP
                    if not pos_tag.startswith('V'):
                        invalid_sentences.append(f"\"{sentence}\"")
            except Exception as e:
                # 如果标注失败，使用备用方法（动词列表）
                # print(f"警告：HanTa 标注失败 '{last_word}': {e}")
                # 使用备用动词列表判断
                german_verbs_backup = {
                    'sein', 'haben', 'werden', 'können', 'müssen', 'sollen', 'wollen', 'dürfen', 'mögen',
                    'gehen', 'kommen', 'machen', 'geben', 'nehmen', 'sehen', 'hören', 'sprechen', 'schreiben',
                    'lesen', 'denken', 'wissen', 'glauben', 'fühlen', 'lieben', 'hassen', 'finden', 'suchen',
                    'zeigen', 'erklären', 'verstehen', 'lernen', 'lehren', 'arbeiten', 'spielen', 'laufen',
                    'fahren', 'fliegen', 'schwimmen', 'tanzen', 'singen', 'essen', 'trinken', 'schlafen',
                    'wachen', 'stehen', 'sitzen', 'liegen', 'fallen', 'steigen', 'öffnen', 'schließen',
                    'beginnen', 'enden', 'anfangen', 'aufhören', 'vergessen', 'erinnern', 'helfen', 'folgen',
                    'führen', 'tragen', 'bringen', 'legen', 'stellen', 'setzen', 'hängen', 'heben', 'senken',
                    'werfen', 'fangen', 'halten', 'greifen', 'fassen', 'packen', 'lösen', 'binden', 'knüpfen',
                    'nähen', 'schneiden', 'brechen', 'reißen', 'zerreißen', 'zerbrechen', 'zerstören', 'bauen',
                    'zerstört', 'reparieren', 'verbessern', 'verschlechtern', 'ändern', 'verändern', 'umändern',
                    'unterstützt', 'steigert', 'verbessert', 'reduziert', 'fördert', 'maximiert', 'bietet',
                    'erleichtert', 'stärkt', 'reguliert', 'produziert', 'schafft', 'verbringt', 'schaffen'
                }
                if last_word.lower() not in german_verbs_backup:
                    invalid_sentences.append(f"\"{sentence}\"")
    else:
        # 备用方法：使用动词列表
        print("警告：HanTa 不可用，使用备用动词列表")
        german_verbs = {
            'sein', 'haben', 'werden', 'können', 'müssen', 'sollen', 'wollen', 'dürfen', 'mögen',
            'gehen', 'kommen', 'machen', 'geben', 'nehmen', 'sehen', 'hören', 'sprechen', 'schreiben',
            'lesen', 'denken', 'wissen', 'glauben', 'fühlen', 'lieben', 'hassen', 'finden', 'suchen',
            'zeigen', 'erklären', 'verstehen', 'lernen', 'lehren', 'arbeiten', 'spielen', 'laufen',
            'fahren', 'fliegen', 'schwimmen', 'tanzen', 'singen', 'essen', 'trinken', 'schlafen',
            'wachen', 'stehen', 'sitzen', 'liegen', 'fallen', 'steigen', 'öffnen', 'schließen',
            'beginnen', 'enden', 'anfangen', 'aufhören', 'vergessen', 'erinnern', 'helfen', 'folgen',
            'führen', 'tragen', 'bringen', 'legen', 'stellen', 'setzen', 'hängen', 'heben', 'senken',
            'werfen', 'fangen', 'halten', 'greifen', 'fassen', 'packen', 'lösen', 'binden', 'knüpfen',
            'nähen', 'schneiden', 'brechen', 'reißen', 'zerreißen', 'zerbrechen', 'zerstören', 'bauen',
            'zerstört', 'reparieren', 'verbessern', 'verschlechtern', 'ändern', 'verändern', 'umändern',
            'unterstützt', 'steigert', 'verbessert', 'reduziert', 'fördert', 'maximiert', 'bietet',
            'erleichtert', 'stärkt', 'reguliert', 'produziert', 'schafft', 'verbringt', 'schaffen'
        }
        
        for sentence in model_response:
            words = split_words(sentence)
            
            # 去除标点符号(包括单词末尾的标点)
            non_punct_words = []
            for w in words:
                # 去除单词两端的标点符号
                cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', w, flags=re.UNICODE)
                if cleaned:  # 如果去除标点后还有内容
                    non_punct_words.append(cleaned)
            
            # 判断最后一个非标点符号单词是否是动词
            if not non_punct_words or non_punct_words[-1].lower() not in german_verbs:
                invalid_sentences.append(f"\"{sentence}\"")

    if not invalid_sentences:
        return True, "✅ 所有从句中的动词均位于句尾。"
    else:
        invalid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(invalid_sentences)])
        return False, f"❌ 以下从句中的动词未位于句尾：\n{invalid_sentence_str}"


# # 示例
# model_response = [
#                 "Liebe Alina,\n\nich hoffe, es geht dir gut! Ich freue mich riesig, dir mitteilen zu können, dass ich bald meinen Geburtstag feiern werde und du unbedingt dabei sein musst. Es wäre einfach nicht dasselbe ohne dich!\n\nDie Party steigt am Samstag, den 18. November, ab 18 Uhr bei mir zu Hause. Wir werden leckeres Essen, tolle Musik und natürlich jede Menge Spaß haben. Ich habe ein paar Überraschungen geplant, die dir bestimmt gefallen werden. Bring gerne deine Tanzschuhe mit, denn wir werden die Nacht durchtanzen!\n\nBitte gib mir Bescheid, ob du kommen kannst, damit ich alles gut vorbereiten kann. Falls du jemanden mitbringen möchtest, sag einfach Bescheid. Je mehr, desto besser!\n\nIch freue mich schon sehr darauf, mit dir zu feiern und einen unvergesslichen Abend zu verbringen. Lass uns zusammen lachen, tanzen und die besten Erinnerungen schaffen.\n\nLiebe Grüße und bis bald,\n[Dein Name]"
#             ]
# print(check_three_conjunctions(model_response))


# # 测试用例

# model_response_2 = [
#     "dass diese Gewohnheit den natürlichen Schlaf-Wach-Rhythmus unterstützt und somit die Konzentration und Effizienz steigert.",
#     "dass ein geregelter Schlafplan die kognitive Funktion und das Gedächtnis verbessert.",
#     "dass ein stabiler Schlaf-Wach-Zyklus den Blutdruck reguliert und Stress reduziert.",
#     "dass ein regelmäßiger Schlafrhythmus die Produktion von Hormonen wie Serotonin und Melatonin fördert, die für das Wohlbefinden wichtig sind.",
#     "dass diese Gewohnheit mehr Zeit für soziale Interaktionen und gemeinschaftliche Aktivitäten bietet, was das Gefühl der Zugehörigkeit stärkt.",
#     "dass ein geregelter Tagesablauf die Planung und Zubereitung von ausgewogenen Mahlzeiten erleichtert und ungesunde Essgewohnheiten reduziert.",
#     "dass diese Gewohnheit nicht nur die körperliche und geistige Gesundheit verbessert, sondern auch die Zeit für persönliche Entwicklung und Freizeitaktivitäten maximiert."
# ]

# result1, message1 = german_clause_conjunction("dass", model_response_2)
# print(message1)  

# result2, message2 = german_clause_verb(model_response_2)
# print(message2) 

if __name__ == "__main__":
    german_clause_verb(["weil laut einer Studie der Universität Oxford die Produktivität am Morgen deutlich höher ist."])