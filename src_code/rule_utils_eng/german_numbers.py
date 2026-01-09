import re

# 使用正则表达式来分割词汇
def split_words(text):
    """
    使用正则表达式分割德语文本为单词
    """
    # 使用正则表达式匹配单词（包括带连字符的复合词）
    words = re.findall(r'\b[\w\-]+\b', text, re.UNICODE)
    return words

def _is_german_number(word):
    """
    判断一个单词是否是德语数字
    使用词根匹配
    """
    word_lower = word.lower()
    
    # 德语数字的基本词根
    number_roots = [
        'null', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun',
        'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn', 
        'siebzehn', 'achtzehn', 'neunzehn', 'zwanzig', 'dreißig', 'vierzig', 
        'fünfzig', 'sechzig', 'siebzig', 'achtzig', 'neunzig',
        'hundert', 'tausend', 'million', 'milliarde', 'billion'
    ]
    
    # 检查是否包含任何数字词根
    for root in number_roots:
        if root in word_lower:
            return True
    
    return False


# 检查回答中是否出现不少于期望个数个德语数字
def check_numbers_count(expected_count, model_response):
    # 提取德语数字词汇
    numbers = set()  # 使用 set 去重

    # 使用正则表达式处理每个句子
    for sentence in model_response:
        words = split_words(sentence)
        for word in words:
            # 如果是阿拉伯数字，跳过
            if word.isdigit():
                continue
            
            # 使用自定义函数识别德语数字
            if _is_german_number(word):
                numbers.add(word)  # 将数字添加到 set 中（自动去重）
    
    # 判断数字出现的数量是否满足预期
    actual_count = len(numbers)

    # 返回是否满足预期数字数量
    if actual_count >= expected_count[0]:
        return True, f"✅ 数字数量满足要求，我们要求出现至少{expected_count[0]}个，实际出现了{actual_count}个，它们分别是{numbers}。" 
    else:
        return False, f"❌ 数字数量不满足要求，我们要求出现至少{expected_count[0]}个，实际出现了{actual_count}个，它们分别是{numbers}。" 

# # 示例输入
# model_response1 = ["Während meiner besonderen Zoo-Tour habe ich fünf faszinierende Tierarten kennengelernt. Der Gorilla lebt in den tropischen Regenwäldern und ernährt sich hauptsächlich von Blättern und Früchten. Er interagiert mit seiner Umgebung, indem er sich durch die Bäume bewegt und Nester baut. Die Anpassung an den Regenwald zeigt sich in seiner kräftigen Körperstruktur und seinem sozialen Verhalten. Der Löwe, ein Bewohner der afrikanischen Savanne, ist ein Fleischfresser und jagt in Gruppen. Seine Anpassung an die Savanne zeigt sich in seiner Fähigkeit, große Entfernungen zu überwinden und sich im hohen Gras zu verstecken. Die Pinguine aus den Polarregionen sind an das kalte Klima angepasst, mit einer dicken Fettschicht und dichtem Gefieder. Sie ernähren sich von Fischen und bewegen sich geschickt im Wasser. Der Elefant, ebenfalls aus der Savanne, nutzt seinen Rüssel zum Greifen und Trinken. Er ist ein Pflanzenfresser und spielt eine wichtige Rolle bei der Landschaftsgestaltung. Schließlich der Koala, der in den Eukalyptuswäldern Australiens lebt und sich von Eukalyptusblättern ernährt. Seine Anpassung zeigt sich in seinem langsamen Stoffwechsel und seiner Fähigkeit, lange Zeit in Bäumen zu verweilen. Ich habe den Zoowärter gefragt, wie der Zoo bedrohte Arten schützt und welche Verhaltensweisen bei Gorillas besonders beobachtet werden. Der Zoo engagiert sich in Schutzprojekten, die sich auf die Erhaltung von Lebensräumen und die Aufklärung der Öffentlichkeit konzentrieren. Diese Bemühungen sind entscheidend, um das Überleben bedrohter Arten zu sichern. Tiere spielen eine wesentliche Rolle im Ökosystem, indem sie zur Biodiversität beitragen und natürliche Prozesse unterstützen. Durch diese Tour habe ich ein tieferes Verständnis für die Bedeutung des Tierschutzes entwickelt und erkannt, wie wichtig es ist, die Vielfalt der Tierwelt zu bewahren 23 1."]
# expected_count = [2]

# result1 = check_numbers_count(expected_count, model_response1)
# print(result1)  


# 检查回答中每个德语数字的长度是否都不少于期望长度
def check_numbers_length(expected_length, model_response):
    # 提取德语数字词汇
    numbers = set()  # 使用 set 去重

    # 使用正则表达式处理每个句子
    for sentence in model_response:
        words = split_words(sentence)
        for word in words:
            # 如果是阿拉伯数字，跳过
            if word.isdigit():
                continue
            
            # 使用自定义函数识别德语数字
            if _is_german_number(word):
                numbers.add(word)  # 将数字添加到 set 中（自动去重）

    # 如果没有提取到任何数字，直接返回
    if not numbers:
        return False, "❌ 没有提取到德语数字。"
    
    # 分别给出长度符合要求和不符合要求的数字列表
    sufficient_length_numbers = [num for num in numbers if len(num) >= expected_length[0]]
    insufficient_length_numbers = [num for num in numbers if len(num) < expected_length[0]]
    
    # 返回是否满足预期数字数量
    if len(insufficient_length_numbers) == 0:
        return True, f"✅ 数字长度全部满足要求，都不少于{expected_length[0]}。" 
    else:
        return False, f"❌ 数字长度不满足要求，我们要求不少于{expected_length[0]}，有如下数字不符合要求：{insufficient_length_numbers}。" 

# # 示例输入
# model_response2 = ["Während meiner besonderen Zoo-Tour habe ich faszinierende Tierarten kennengelernt. Der Gorilla lebt in den tropischen Regenwäldern und ernährt sich hauptsächlich von Blättern und Früchten. Er interagiert mit seiner Umgebung, indem er sich durch die Bäume bewegt und Nester baut. Die Anpassung an den Regenwald zeigt sich in seiner kräftigen Körperstruktur und seinem sozialen Verhalten. Der Löwe, ein Bewohner der afrikanischen Savanne, ist ein Fleischfresser und jagt in Gruppen. Seine Anpassung an die Savanne zeigt sich in seiner Fähigkeit, große Entfernungen zu überwinden und sich im hohen Gras zu verstecken. Die Pinguine aus den Polarregionen sind an das kalte Klima angepasst, mit einer dicken Fettschicht und dichtem Gefieder. Sie ernähren sich von Fischen und bewegen sich geschickt im Wasser. Der Elefant, ebenfalls aus der Savanne, nutzt seinen Rüssel zum Greifen und Trinken. Er ist ein Pflanzenfresser und spielt eine wichtige Rolle bei der Landschaftsgestaltung. Schließlich der Koala, der in den Eukalyptuswäldern Australiens lebt und sich von Eukalyptusblättern ernährt. Seine Anpassung zeigt sich in seinem langsamen Stoffwechsel und seiner Fähigkeit, lange Zeit in Bäumen zu verweilen. Ich habe den Zoowärter gefragt, wie der Zoo bedrohte Arten schützt und welche Verhaltensweisen bei Gorillas besonders beobachtet werden. Der Zoo engagiert sich in Schutzprojekten, die sich auf die Erhaltung von Lebensräumen und die Aufklärung der Öffentlichkeit konzentrieren. Diese Bemühungen sind entscheidend, um das Überleben bedrohter Arten zu sichern. Tiere spielen eine wesentliche Rolle im Ökosystem, indem sie zur Biodiversität beitragen und natürliche Prozesse unterstützen. Durch diese Tour habe ich ein tieferes Verständnis für die Bedeutung des Tierschutzes entwickelt und erkannt, wie wichtig es ist, die Vielfalt der Tierwelt zu bewahren."]
# expected_length = [2]

# result2 = check_numbers_length(expected_length, model_response2)
# print(result2)  