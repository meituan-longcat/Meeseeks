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

# 统计回答中是否同时出现了['der', 'die', 'das']这三个冠词
def check_three_articles(model_response):
    # 初始化要检查的冠词集合
    articles_to_check = ['der', 'die', 'das']
    found_articles = set()  # 用于存储已经出现的冠词
    
    # 遍历文中的每个句子
    for sentence in model_response:
        # 使用正则表达式分割单词，而不是使用 stanza
        words = split_words(sentence)
        for word in words:
            # 如果词是定冠词，加入 found_articles 集合
            if word.lower() in articles_to_check:
                found_articles.add(word.lower())
    
    # 计算哪些冠词没有出现
    missing_articles = [article for article in articles_to_check if article not in found_articles]
    
    if len(found_articles) == 3:
        return True, f"✅ 三个定冠词全部出现。"
    
    # 这里如果写else,评测时会出问题，推理是范围覆盖问题。
    return False, f"❌ 有以下定冠词未出现：{missing_articles}。"


# 检查德语定冠词总数是否符合要求
def german_article_count(expected_count, model_response):
    # 统计定冠词的总数
    total_count = 0
    for sentence in model_response:
        # 使用正则表达式分割单词，而不是使用 stanza
        words = split_words(sentence)
        for word in words:
            if word.lower() in ['der', 'die', 'das']:
                total_count += 1

    if total_count >= expected_count[0]:
        return True, f"✅ 定冠词总数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {total_count} 个，数量满足要求。"
    else:
        return False, f"❌ 定冠词总数量不符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {total_count} 个，数量不符合要求。"
    

# 检查定冠词der是否数量符合要求
def german_article_der(expected_count, model_response):
    der_count = 0
    
    for sentence in model_response:
        # 使用正则表达式分割单词，而不是使用 stanza
        words = split_words(sentence)
        for word in words:
            # 统计 'der' 的出现次数
            if word.lower() == 'der':
                der_count += 1

    if der_count < expected_count[0]:
        return False, f"❌ 定冠词der的数量不符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {der_count} 个，数量不符合要求。"
    
    return True, f"✅ 定冠词der的数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {der_count} 个，数量满足要求。"


# 检查定冠词das是否数量符合要求
def german_article_das(expected_count, model_response):
    das_count = 0

    for sentence in model_response:
        # 使用正则表达式分割单词，而不是使用 stanza
        words = split_words(sentence)
        for word in words:
            # 统计 'das' 的出现次数
            if word.lower() == 'das':
                das_count += 1

    if das_count < expected_count[0]:
        return False, f"❌ 定冠词das的数量不符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {das_count} 个，数量不符合要求。"
    
    return True, f"✅ 定冠词das的数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {das_count} 个，数量满足要求。"


# 检查定冠词die是否数量符合要求
def german_article_die(expected_count, model_response):
    die_count = 0

    for sentence in model_response:
        # 使用正则表达式分割单词，而不是使用 stanza
        words = split_words(sentence)
        for word in words:
            # 统计 'die' 的出现次数
            if word.lower() == 'die':
                die_count += 1

    if die_count < expected_count[0]:
        return False, f"❌ 定冠词die的数量不符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {die_count} 个，数量不符合要求。"
    
    return True, f"✅ 定冠词die的数量符合要求。我们在题目中要求不少于 {expected_count[0]} 个，实际找到了 {die_count} 个，数量满足要求。"




# # 测试用例
# model_response_1 = [
#                 "Während meiner besonderen Zoo-Tour hatte ich die Gelegenheit, faszinierende Tiere und ihre Lebensräume kennenzulernen. Der erste Bereich, den wir besuchten, war der tropische Regenwald, wo ich die Gorillas beobachtete. Diese beeindruckenden Primaten leben in dichten Wäldern und ernähren sich hauptsächlich von Blättern, Früchten und gelegentlich Insekten. Ihre kräftigen Arme und Hände ermöglichen es ihnen, sich geschickt durch die Bäume zu bewegen und Nahrung zu sammeln. Ich bemerkte, wie die Gorillas in Gruppen interagierten und ihre sozialen Strukturen pflegten, was für ihr Überleben entscheidend ist.Im nächsten Bereich trafen wir auf die majestätischen Löwen der afrikanischen Savanne. Diese Raubtiere sind Fleischfresser und jagen in Rudeln, um ihre Beute effizient zu erlegen. Die Löwen sind perfekt an das Leben in der offenen Savanne angepasst, mit ihrer Fähigkeit, große Distanzen zu überwinden und sich in der Hitze zu tarnen. Ich beobachtete, wie sie sich im Schatten ausruhten und ihre Energie für die Jagd sparten, was ihre Überlebensstrategie in dieser Umgebung verdeutlicht.Ein weiteres Highlight war der Besuch der Polarregion, wo die Pinguine leben. Diese Vögel sind an das kalte Klima angepasst und ernähren sich hauptsächlich von Fisch. Ihre dichte Federstruktur und die Fähigkeit, lange Strecken zu schwimmen, helfen ihnen, in der eisigen Umgebung zu überleben. Ich sah, wie die Pinguine sich in Gruppen bewegten und ihre sozialen Bindungen stärkten, was ihnen Schutz und Wärme bietet.Zusätzlich zu diesen drei Arten lernte ich auch die Elefanten kennen, die in verschiedenen Lebensräumen wie Wäldern und Savannen vorkommen. Diese Pflanzenfresser sind für ihre Intelligenz und sozialen Strukturen bekannt. Ihre großen Ohren helfen ihnen, sich abzukühlen, und ihr Rüssel ist ein vielseitiges Werkzeug zum Fressen und Trinken. Ich beobachtete, wie die Elefanten miteinander kommunizierten und ihre Umgebung erkundeten, was ihre Anpassungsfähigkeit zeigt.Schließlich besuchten wir die Aquarien, wo ich die bunten Clownfische sah. Diese kleinen Fische leben in Korallenriffen und haben eine symbiotische Beziehung zu Seeanemonen. Sie ernähren sich von kleinen Wirbellosen und Algen. Ihre leuchtenden Farben und schnellen Bewegungen sind perfekt an das Leben im Wasser angepasst. Ich bemerkte, wie sie sich geschickt zwischen den Anemonen bewegten und Schutz suchten.Während der Tour stellte ich dem Zoowärter zwei Fragen: Erstens wollte ich wissen, wie der Zoo bedrohte Arten schützt. Er erklärte, dass der Zoo an Zuchtprogrammen und internationalen Schutzprojekten beteiligt ist, um die Populationen zu stabilisieren. Zweitens fragte ich nach den Verhaltensweisen der Tiere in Gefangenschaft. Der Zoowärter erläuterte, dass der Zoo versucht, die natürlichen Lebensbedingungen so gut wie möglich nachzubilden, um das Wohlbefinden der Tiere zu gewährleisten.In meiner Zusammenfassung habe ich gelernt, dass der Schutz von Tieren im Zoo eine wichtige Rolle spielt, um das Überleben bedrohter Arten zu sichern. Die Tiere sind entscheidend für das Gleichgewicht im Ökosystem, da sie zur Erhaltung der Biodiversität beitragen. Der Zoo bietet eine wertvolle Gelegenheit, mehr über die Tiere und ihre Lebensräume zu erfahren und das Bewusstsein für den Tierschutz zu erhöhen. Durch diese Tour habe ich ein tieferes Verständnis für die Bedeutung des Schutzes und der Erhaltung unserer Tierwelt entwickelt."
#             ]

# result1 = german_article_count([3], model_response_1)
# print(result1)  

# result2 = german_article_der([3], model_response_1)
# print(result2)

# result3 = german_article_das([1], model_response_1)
# print(result3)

# result4 = german_article_die([3], model_response_1)
# print(result4)

# result5 = check_three_articles(model_response_1)
# print(result5)