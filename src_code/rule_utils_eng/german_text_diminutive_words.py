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


def check_text_diminutive_words(expected_count, model_response):
    """
    检查德语指小词（Diminutive）数量
    指小词特征：
    1. 必须是名词（NOUN）或专有名词（PROPN）
    2. 以 "chen" 或 "lein" 结尾
    3. 排除复数形式
    """
    # 所有提取的指小词
    all_diminutive_words = []
    
    if HANTA_AVAILABLE and tagger is not None:
        # 使用 HanTa 库进行词性标注
        for story in model_response:
            try:
                # 对句子进行分词和标注
                words = story.split()
                tags = tagger.tag_sent(words)
                
                # 筛选符合条件的指小词
                for tag_result in tags:
                    if isinstance(tag_result, tuple) and len(tag_result) >= 3:
                        word, lemma, pos_tag = tag_result[0], tag_result[1], tag_result[2]
                    else:
                        continue
                    
                    # 去除标点符号
                    clean_word = re.sub(r'^[^\w]+|[^\w]+$', '', word, flags=re.UNICODE)
                    if not clean_word:
                        continue
                    
                    # 检查是否以 "chen" 或 "lein" 结尾
                    ends_with_chen = clean_word.endswith("chen")
                    ends_with_lein = clean_word.endswith("lein")
                    
                    # 排除常见的非指小词
                    # - 以 ichen/lichen/ischen 结尾的是形容词变形，不是指小词
                    # - 以 chen 结尾但很长的动词（如 verdeutlichen）
                    is_adjective_ending = (
                        clean_word.endswith("ischen") or 
                        clean_word.endswith("lichen") or
                        clean_word.endswith("ichen")
                    )
                    
                    # 检查是否是指小词后缀
                    ends_with_diminutive = (ends_with_chen or ends_with_lein) and not is_adjective_ending
                    
                    if not ends_with_diminutive:
                        continue
                    
                    # 检查词性：HanTa 使用 STTS 标注集
                    # NN = 普通名词, NE = 专有名词, FM = 外来词
                    # 注意：HanTa 对于新造的指小词（特别是带引号的）可能标注为 FM 或 ADJ(A)
                    # 因此我们主要依赖后缀特征，但排除明显的动词
                    is_verb = pos_tag.startswith('V')
                    
                    if not is_verb:
                        # 排除复数形式（STTS 标注中复数通常标记为 NNS 或包含 Pl）
                        # HanTa 的复数标签通常是 NNS (Plural Noun)
                        if 'Pl' in pos_tag or pos_tag == 'NNS':
                            continue
                        
                        # 添加符合条件的指小词
                        all_diminutive_words.append(clean_word)
                        
            except Exception as e:
                # 如果 HanTa 处理失败，使用备用方法
                print(f"警告：HanTa 处理失败: {e}，使用备用方法")
                words = split_words(story)
                for word in words:
                    clean_word = re.sub(r'^[^\w]+|[^\w]+$', '', word, flags=re.UNICODE)
                    # 简单的后缀检查（备用方法，无法判断词性和单复数）
                    if clean_word and (clean_word.endswith("chen") or clean_word.endswith("lein")):
                        all_diminutive_words.append(clean_word)
    else:
        # 备用方法：仅基于后缀判断（不推荐，但在 HanTa 不可用时使用）
        print("警告：HanTa 不可用，使用简化的指小词检测（可能不够准确）")
        for story in model_response:
            words = split_words(story)
            for word in words:
                clean_word = re.sub(r'^[^\w]+|[^\w]+$', '', word, flags=re.UNICODE)
                if clean_word and (clean_word.endswith("chen") or clean_word.endswith("lein")):
                    all_diminutive_words.append(clean_word)

    # 去重
    all_diminutive_words = list(set(all_diminutive_words))
    valid_word_str = ", ".join(all_diminutive_words)

    # 特殊情况，指小词个数为0
    if len(all_diminutive_words) == 0:
        return False, f"❌ 没有提取到任何德语指小词"

    # 检查提取的指小词数量是否符合预期
    if len(all_diminutive_words) < expected_count[0]:
        return False, f"❌ 提取到的指小词数量不够，应该是不少于 {expected_count[0]} 个，但找到了 {len(all_diminutive_words)} 个，它们是：{valid_word_str}"

    # 个数符合预期
    return True, f"✅ 提取到的指小词数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {len(all_diminutive_words)} 个，数量满足要求，它们是：{valid_word_str}"

# # 测试数据
# model_response = ["Große vortrainierte Modelle wie GPT-4 oder BERT haben die natürliche Sprachverarbeitung revolutioniert, denn sie können in Anwendungsgebieten wie Textgenerierung, Sentiment-Analyse, maschineller Übersetzung oder Fragebeantwortung eingesetzt werden. Ein solches Modell kann eine hohe Präzision und starke Generalisierungsfähigkeit bieten, aber es muss auch mit Herausforderungen wie hohem Rechenaufwand, Datenschutzproblemen und mangelnder Interpretierbarkeit umgehen. Ein Diminutiv wie „Modellchen“ kann verdeutlichen, dass kleinere Varianten durch Modellpruning oder Quantisierung entstehen können, sodass die Rechenkosten reduziert werden. Ein „Datensätzchen“ kann helfen, die Trainingsdaten besser zu kontrollieren, um Vorurteile zu minimieren. Man sollte Wissensdistillation nutzen, damit ein „Netzwerkchen“ von einem großen Modell lernen kann, ohne dessen Komplexität zu übernehmen. Die ethischen und rechtlichen Auswirkungen dürfen nicht unterschätzt werden, denn ein „Algorithmchen“ kann Vorurteile verstärken oder missbraucht werden. Entwickler müssen Mechanismen wie Fairness-Checks und Transparenzrichtlinien implementieren, damit ein „Promptchen“ nicht zu diskriminierenden Ergebnissen führt. Man kann auch „Tokenchen“ und „Parameterchen“ optimieren, sodass die Nachhaltigkeit und Zuverlässigkeit verbessert werden. Letztlich sollte ein „Systemchen“ so gestaltet sein, dass es Missbrauch verhindert, sondern auch die Privatsphäre schützt. Nur durch technische Innovationen und verantwortungsvolle Nutzung kann das volle Potenzial großer Modelle ausgeschöpft werden."]

# expected_count = [8,8]  # 期望的最少数量

# # 检查段落中的所有单词是否都是德语指小词，且数量正确
# result = check_text_diminutive_words(expected_count, model_response)
# print(result)