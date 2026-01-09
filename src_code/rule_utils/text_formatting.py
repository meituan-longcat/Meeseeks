import re
from ..utils import clean_up_text

def model_no_end_with_punctuation(model_responses):
    """Check if there are sentences ending with punctuation"""
    def check_punctuation(s):
        if re.match(r'.*[.,!?:;]$', s):
            return 0
        else:
            return 1
    for item in model_responses:
        if check_punctuation(item) == 0:
            return 0, f"❌ Found sentence ending with punctuation: {str(item)}"
    return 1, f"✅ No sentences ending with punctuation found"


def model_endswith_each(rule, model_response):
    """Check if each response item ends with specified content"""
    rule = rule[0]
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.endswith(temp_rule):
            return 0, f"❌ Mismatch, sentence: {str(item)} does not end with {str(rule)}"
    return 1, f"✅ Match, sentences: {str(model_response)} all end with {str(rule)}"

def endswithany_each(rule, model_response):
    """Check if each response item contains any element from the rule"""
    for item in model_response:
        temp_item = clean_up_text(item)

        # Check if current item contains any element from rule
        contains_any = False
        for rule_element in rule:
            temp_rule = clean_up_text(rule_element)
            if temp_rule in temp_item:
                contains_any = True
                break

        # If current item doesn't contain any rule element, return failure
        if not contains_any:
            return 0, f"❌ Mismatch, sentence: {str(item)} does not contain any element from rule {str(rule)}"

    return 1, f"✅ Match, sentences: {str(model_response)} all contain at least one element from rule {str(rule)}"

def model_startswith_each(rule, model_response):
    """Check if each response item starts with specified content"""
    rule = rule[0]
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.startswith(temp_rule):
            return 0, f"❌ Mismatch, sentence: {str(item)} does not start with {str(rule)}"
    return 1, f"✅ Match, sentences: {str(model_response)} all start with {str(rule)}"


def model_non_regex(rule, model_response):
    """Check if does not match specified regular expression"""
    pattern = r"\|(.*?)\|"
    regex = re.search(pattern, rule).group(1)
    for item in model_response:
        if re.match(regex, item):
            return 0, f"✅ This item satisfies: {str(item)}, regex: {str(regex)}"
    return 1, "❌ No regex match"

def model_regex(rule, model_response):
    """Check if matches specified regular expression"""
    pattern = r"\|(.*?)\|"
    regex = re.search(pattern, rule).group(1)
    for item in model_response:
        if re.fullmatch(regex, item):  # Use re.fullmatch to ensure entire string matches
            return 1, f"✅ This item satisfies: {str(item)}, regex: {str(regex)}"
    return 0, "❌ No regex match"
