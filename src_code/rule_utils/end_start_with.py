import re
from ..utils import clean_up_text

def model_no_end_with_punctuation(model_responses):
    def check_punctuation(s):
        if re.match(r'.*[.,!?:;]$', s):
            return 0
        else:
            return 1
    for item in model_responses:
        if check_punctuation(item) == 0:
            return 0, f"❌ 发现以标点结尾的句子： {str(item)}"
    return 1, f"✅ 未发现以标点结尾的句子"


def model_endswith_each(rule, model_response):
    rule = rule[0]
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.endswith(temp_rule):
            return 0, f"❌ 不匹配，句子：{str(item)} 不以 {str(rule)} 结尾"
    return 1, f"✅ 匹配，句子：{str(model_response)} 都以 {str(rule)} 结尾"

def endswithany_each(rule, model_response):
    failed_items = []
    
    for item in model_response:
        temp_item = clean_up_text(item)
        
        # 检查当前item是否以rule中任意元素结尾
        matches_any_rule = any(
            temp_item.endswith(clean_up_text(rule_element)) 
            for rule_element in rule
        )
        
        if not matches_any_rule:
            failed_items.append(item)
    
    if failed_items:
        return 0, f"❌ 不匹配，以下句子不以规则中任何元素结尾：{failed_items}，规则：{rule}"
    
    return 1, f"✅ 匹配，所有句子都以规则中至少一个元素结尾，规则：{rule}"


def model_startswith_each(rule, model_response):
    rule = rule[0]
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.startswith(temp_rule):
            return 0, f"❌ 不匹配，句子：{str(item)} 不以 {str(rule)} 开头"
    return 1, f"✅ 匹配，句子：{str(model_response)} 都以 {str(rule)} 开头"

