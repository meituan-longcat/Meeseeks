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

def check_imperative_sentence(expected_count, model_response):
    imperative_count = 0  # 用于统计祈使句的数量
    valid_imperative_sentences = set()  # 用于存储符合祈使句的句子，使用set避免重复
    
    # 使用正则表达式处理每个句子
    for sentence in model_response:
        words = split_words(sentence)
        
        # 1 特别处理带有"Bitte"的句子
        if "Bitte" in sentence:
            valid_imperative_sentences.add(f"\"{sentence}\"")
            continue  # 如果有"Bitte"则当作祈使句处理
        
        # 2 检查句子是否以常见的祈使句动词开头
        if len(words) > 0:
            first_word = words[0].lower()
            
            # 常见的德语祈使句动词（以e结尾的动词）
            imperative_verbs = {
                'gehe', 'komme', 'mache', 'nimm', 'gib', 'sieh', 'höre', 'spiele', 'lese', 'schreibe',
                'denke', 'frage', 'antworte', 'arbeite', 'laufe', 'sitze', 'stehe', 'bleibe', 'fahre',
                'fliege', 'schwimme', 'tanze', 'singe', 'male', 'zeichne', 'baue', 'kaufe', 'verkaufe',
                'öffne', 'schließe', 'zeige', 'erkläre', 'erzähle', 'vergesse', 'erinnere', 'hilf',
                'versuche', 'beginne', 'ende', 'warte', 'höre', 'schaue', 'beobachte', 'vergleiche'
            }
            
            # 检查第一个单词是否是祈使句动词
            if first_word in imperative_verbs or first_word.endswith('e'):
                valid_imperative_sentences.add(f"\"{sentence}\"")
            # 检查是否包含"Sie"（尊称祈使句）
            elif "Sie" in sentence:
                valid_imperative_sentences.add(f"\"{sentence}\"")

    
    # 检查祈使句数量是否符合预期
    valid_imperative_sentences = list(valid_imperative_sentences)  # 转换为列表以便排序和编号
    imperative_count = len(valid_imperative_sentences)

    if imperative_count == 0:
        return False, "❌ 没有提取到任何祈使句"

    if imperative_count < expected_count[0]:
        # 使用 "\n" 将每个句子单独一行输出，并确保每个句子前都有编号
        valid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_imperative_sentences)])
        return False, f"❌ 提取到的祈使句数量不够，应该是不少于 {expected_count[0]} 个，但找到了 {imperative_count} 个，它们是：{valid_sentence_str}"

    # 个数符合预期
    # 使用列表确保输出顺序一致
    valid_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_imperative_sentences)])
    return True, f"✅ 提取到的祈使句数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {imperative_count} 个，数量满足要求，它们是：{valid_sentence_str}"


def check_formal_imperative_sentence(expected_count, model_response):
    """
    检查德语尊称祈使句（Formelle Imperativsätze）
    尊称祈使句特征：
    1. 包含 "Bitte" 和 "Sie" 的句子
    2. 以动词开头（原形或限定形式）且句中有 "Sie"
    3. 动词处于祈使语气且有 "Sie"
    4. 特殊情况：第一个词以 e 结尾且有 "Sie"（应对词性标注错误）
    """
    valid_formal_imperative_sentences = set()  # 用于存储符合尊称祈使句的句子
    
    if HANTA_AVAILABLE and tagger is not None:
        # 使用 HanTa 库进行词性标注
        for sentence in model_response:
            try:
                # 1. 特别处理带有"Bitte"和"Sie"的句子
                if "Bitte" in sentence and "Sie" in sentence:
                    valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                    continue
                
                # 对句子进行分词和标注
                words = sentence.split()
                tags = tagger.tag_sent(words)
                
                # 过滤掉标点符号
                non_punct_tags = []
                for tag_result in tags:
                    if isinstance(tag_result, tuple) and len(tag_result) >= 3:
                        word, lemma, pos_tag = tag_result[0], tag_result[1], tag_result[2]
                        # 去除标点符号
                        clean_word = re.sub(r'^[^\w]+|[^\w]+$', '', word, flags=re.UNICODE)
                        if clean_word and pos_tag != '$.' and pos_tag != '$,':  # 排除标点符号
                            non_punct_tags.append((clean_word, lemma, pos_tag))
                
                if not non_punct_tags:
                    continue
                
                # 检查句子中是否有 "Sie"
                has_sie = "Sie" in sentence
                
                if not has_sie:
                    continue
                
                # 2. 检查句子是否以动词开头（或 Bitte + 动词）且句中有"Sie"
                # HanTa STTS 标注集：
                # VVFIN = 限定动词, VVINF = 不定式动词, VVIMP = 祈使动词
                # VAFIN = 助动词限定形式, VAINF = 助动词不定式, VAIMP = 助动词祈使式
                
                # 找到第一个动词（可能不是第一个词，比如 "Bitte achten Sie..."）
                found_verb_with_sie = False
                for idx, (word, lemma, pos_tag) in enumerate(non_punct_tags):
                    is_verb = (
                        pos_tag.startswith('VV') or  # 实义动词
                        pos_tag.startswith('VA') or  # 助动词
                        pos_tag.startswith('VM')     # 情态动词
                    )
                    
                    # 如果是动词
                    if is_verb:
                        # 检查是否是限定形式或不定式
                        is_fin_or_inf = (
                            'FIN' in pos_tag or   # 限定形式
                            'INF' in pos_tag or   # 不定式
                            'IMP' in pos_tag      # 祈使式
                        )
                        
                        # 如果动词在前两个位置（直接开头或 Bitte + 动词）
                        if idx <= 1 and is_fin_or_inf:
                            found_verb_with_sie = True
                            valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                            break
                        
                        # 如果动词有祈使式标记
                        if 'IMP' in pos_tag:
                            found_verb_with_sie = True
                            valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                            break
                
                if found_verb_with_sie:
                    continue
                
                # 3. 特殊情况：第一个单词以 e 结尾（应对词性判断错误）
                # 大部分德语祈使句动词以 e 结尾
                first_word = non_punct_tags[0][0]
                if first_word.endswith('e') or (len(non_punct_tags) > 1 and non_punct_tags[1][0].endswith('e')):
                    valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                    
            except Exception as e:
                # 如果 HanTa 处理失败，使用备用方法
                print(f"警告：HanTa 处理失败: {e}，使用备用方法")
                # 备用方法：简单规则
                if "Bitte" in sentence and "Sie" in sentence:
                    valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                elif "Sie" in sentence:
                    words = split_words(sentence)
                    if len(words) > 0:
                        first_word = words[0]
                        clean_first = re.sub(r'^[^\w]+|[^\w]+$', '', first_word, flags=re.UNICODE)
                        if clean_first.endswith('e') or clean_first.lower() in ['seien', 'nehmen', 'folgen']:
                            valid_formal_imperative_sentences.add(f"\"{sentence}\"")
    else:
        # 备用方法：不使用 HanTa
        print("警告：HanTa 不可用，使用简化的尊称祈使句检测")
        for sentence in model_response:
            # 1. 特别处理带有"Bitte"和"Sie"的句子
            if "Bitte" in sentence and "Sie" in sentence:
                valid_formal_imperative_sentences.add(f"\"{sentence}\"")
                continue
            
            # 2. 检查是否包含"Sie"（尊称祈使句的标志）
            if "Sie" in sentence:
                words = split_words(sentence)
                if len(words) > 0:
                    first_word = words[0]
                    clean_first = re.sub(r'^[^\w]+|[^\w]+$', '', first_word, flags=re.UNICODE).lower()
                    
                    # 常见的德语祈使句动词
                    imperative_verbs = {
                        'gehe', 'komme', 'mache', 'nimm', 'gib', 'sieh', 'höre', 'spiele', 'lese', 'schreibe',
                        'denke', 'frage', 'antworte', 'arbeite', 'laufe', 'sitze', 'stehe', 'bleibe', 'fahre',
                        'öffne', 'schließe', 'zeige', 'erkläre', 'erzähle', 'vergesse', 'erinnere', 'hilf',
                        'versuche', 'beginne', 'ende', 'warte', 'schaue', 'beobachte', 'vergleiche',
                        'seien', 'nehmen', 'folgen', 'respektieren', 'halten', 'achten', 'melden'
                    }
                    
                    # 检查第一个单词是否是祈使句动词或以e结尾
                    if clean_first in imperative_verbs or clean_first.endswith('e'):
                        valid_formal_imperative_sentences.add(f"\"{sentence}\"")
    
    # 检查尊称祈使句数量是否符合预期
    valid_formal_imperative_sentences = list(valid_formal_imperative_sentences)
    formal_imperative_count = len(valid_formal_imperative_sentences)

    if formal_imperative_count == 0:
        return False, "❌ 没有提取到任何尊称祈使句"

    if formal_imperative_count < expected_count[0]:
        valid_formal_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_formal_imperative_sentences)])
        return False, f"❌ 提取到的尊称祈使句数量不够，应该是不少于 {expected_count[0]} 个，但找到了 {formal_imperative_count} 个，它们是：{valid_formal_sentence_str}"

    # 个数符合预期
    valid_formal_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_formal_imperative_sentences)])
    return True, f"✅ 提取到的尊称祈使句数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {formal_imperative_count} 个，数量满足要求，它们是：{valid_formal_sentence_str}"


def check_informal_imperative_sentence(expected_count, model_response):
    valid_informal_imperative_sentences = set()  # 用于存储符合平称祈使句的句子，使用set避免重复
    
    # 使用正则表达式处理每个句子
    for sentence in model_response:
        words = split_words(sentence)
        
        # 1 特别处理带有"Bitte"但不包含"Sie"的句子
        if "Bitte" in sentence and "Sie" not in sentence:
            valid_informal_imperative_sentences.add(f"\"{sentence}\"")
            continue
        
        # 2 检查是否不包含"Sie"（平称祈使句的标志）
        if "Sie" not in sentence and len(words) > 0:
            first_word = words[0].lower()
            
            # 常见的德语祈使句动词
            imperative_verbs = {
                'gehe', 'komme', 'mache', 'nimm', 'gib', 'sieh', 'höre', 'spiele', 'lese', 'schreibe',
                'denke', 'frage', 'antworte', 'arbeite', 'laufe', 'sitze', 'stehe', 'bleibe', 'fahre',
                'fliege', 'schwimme', 'tanze', 'singe', 'male', 'zeichne', 'baue', 'kaufe', 'verkaufe',
                'öffne', 'schließe', 'zeige', 'erkläre', 'erzähle', 'vergesse', 'erinnere', 'hilf',
                'versuche', 'beginne', 'ende', 'warte', 'höre', 'schaue', 'beobachte', 'vergleiche',
                'trainiere', 'folge', 'respektiere', 'halte', 'achte', 'melde'
            }
            
            # 检查第一个单词是否是祈使句动词或以e结尾
            if first_word in imperative_verbs or first_word.endswith('e'):
                valid_informal_imperative_sentences.add(f"\"{sentence}\"")
            
    
    # 检查平称祈使句数量是否符合预期
    valid_informal_imperative_sentences = list(valid_informal_imperative_sentences)  # 转换为列表以便排序和编号
    informal_imperative_count = len(valid_informal_imperative_sentences)

    if informal_imperative_count == 0:
        return False, "❌ 没有提取到任何平称祈使句"

    if informal_imperative_count < expected_count[0]:
        valid_informal_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_informal_imperative_sentences)])
        return False, f"❌ 提取到的平称祈使句数量不够，应该是不少于 {expected_count[0]} 个，但找到了 {informal_imperative_count} 个，它们是：{valid_informal_sentence_str}"

    # 个数符合预期
    valid_informal_sentence_str = "\n".join([f"{idx + 1}. {sentence}" for idx, sentence in enumerate(valid_informal_imperative_sentences)])
    return True, f"✅ 提取到的平称祈使句数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {informal_imperative_count} 个，数量满足要求，它们是：{valid_informal_sentence_str}"


def check_sentence_length_monotonicity(model_response):
    # 正则表达式去除标点符号
    def remove_punctuation(sentence):
        return re.sub(r'[^\w\s]', '', sentence)
    
    # 计算去除标点符号后的句子长度
    sentence_lengths = [len(remove_punctuation(sentence).split()) for sentence in model_response]

    # 检查是否单调递增
    is_monotonic = all(earlier <= later for earlier, later in zip(sentence_lengths, sentence_lengths[1:]))
    
    if is_monotonic:
        return True, "✅ 句子长度是单调递增的。"
    else:
        return False, "❌ 句子长度不是单调递增的。"


# # 测试数据
# model_response = [
# "Stehen Sie jeden Morgen pünktlich um 6 Uhr auf.",
#  "Tragen Sie Ihre Uniform stets ordentlich und vollständig.",
# "Melden Sie sich bei jedem Vorgesetzten korrekt an.",
#  "Seien Sie während des Unterrichts aufmerksam und respektvoll.",
#  "Halten Sie Ihre Unterkunft sauber und ordentlich.",
#  "Folgen Sie den Trainingsanweisungen ohne Verzögerung.",
#  "Befolgen Sie die Sicherheitsvorschriften in allen Bereichen.",
#  "Bitte achten Sie darauf, Ihre Kameraden jederzeit zu unterstützen und zu respektieren.",
# "Bitte erscheinen Sie zu allen Veranstaltungen und Übungen rechtzeitig und vorbereitet.",
#  "Bitte melden Sie jegliche Regelverstöße oder Vorfälle unverzüglich und ehrlich an die zuständigen Stellen, damit wir gemeinsam für ein sicheres und diszipliniertes Umfeld sorgen können."
# ]

# expected_count = [10, 1000]  # 期望的最少数量

# # 调用函数进行检查
# result1 = check_imperative_sentence(expected_count, model_response)
# print(result1)  

# result2 = check_formal_imperative_sentence(expected_count, model_response)
# print(result2)  

# result3 = check_informal_imperative_sentence(expected_count, model_response)
# print(result3) 


# model_response_new = [
#                 "Mach dein Bett ordentlich!",
#                 "Zieh deine Uniform korrekt an!",
#                 "Halte deine Ausrüstung sauber und einsatzbereit!",
#                 "Bitte achten Sie darauf, dass Ihr Spind immer ordentlich ist."
#             ]

# result4 = check_sentence_length_monotonicity(model_response_new)
# print(result4)