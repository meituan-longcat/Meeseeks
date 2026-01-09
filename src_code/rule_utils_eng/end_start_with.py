import re
import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src_code.utils_eng import clean_up_text, to_lowercase_list

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
    rule = to_lowercase_list(rule)[0]
    model_response = to_lowercase_list(model_response)
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.endswith(temp_rule):
            return 0, f"❌ 不匹配，句子：{str(item)} 不以 {str(rule)} 结尾"
    return 1, f"✅ 匹配，句子：{str(model_response)} 都以 {str(rule)} 结尾"

def model_startswith_each(rule, model_response):
    rule = to_lowercase_list(rule)[0]
    model_response = to_lowercase_list(model_response)
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.startswith(temp_rule):
            return 0, f"❌ 不匹配，句子：{str(item)} 不以 {str(rule)} 开头"
    return 1, f"✅ 匹配，句子：{str(model_response)} 都以 {str(rule)} 开头"

if __name__ == "__main__":
    x = [
                "1. Gras Goji Essence Gras\n",
                "2. Gras Herbal Harmony Gras\n",
                "3. Gras Angelica Remedy Gras\n",
                "4. Gras Ginseng Fusion Gras\n",
                "5. Gras Autumn Harvest Gras\n",
                "6. Gras Berry Elixir Gras\n",
                "7. Gras Sumsum Vitality Gras\n",
                "8. Gras Wind-Cool Relief Gras\n",
                "9. Gras Eye Brightener Gras\n",
                "10. Gras Liver Nourish Gras\n",
                "11. Gras Essence Blend Gras\n",
                "12. Gras Sumsum Strength Gras\n",
                "13. Gras Herbal Cure Gras\n",
                "14. Gras Berry Balance Gras\n",
                "15. Gras Ginseng Harmony Gras\n",
                "16. Gras Angelica Essence Gras\n",
                "17. Gras Autumn Essence Gras\n",
                "18. Gras Berry Remedy Gras\n",
                "19. Gras Herbal Vitality Gras\n",
                "20. Gras Wind-Cool Remedy Gras\n",
                "21. Gras Eye Nourish Gras\n",
                "22. Gras Liver Vitality Gras\n",
                "23. Gras Essence Harmony Gras\n",
                "24. Gras Sumsum Remedy Gras\n",
                "25. Gras Herbal Elixir Gras\n",
                "26. Gras Berry Fusion Gras\n",
                "27. Gras Ginseng Essence Gras\n",
                "28. Gras Angelica Balance Gras\n",
                "29. Gras Autumn Remedy Gras\n",
                "30. Gras Berry Vitality Gras\n",
                "31. Gras Herbal Brightener Gras\n",
                "32. Gras Wind-Cool Essence Gras\n",
                "33. Gras Eye Remedy Gras\n",
                "34. Gras Liver Essence Gras\n",
                "35. Gras Essence Vitality Gras\n",
                "36. Gras Sumsum Elixir Gras\n",
                "37. Gras Herbal Balance Gras\n",
                "38. Gras Berry Harmony Gras\n",
                "39. Gras Ginseng Remedy Gras\n",
                "40. Gras Angelica Vitality Gras\n",
                "41. Gras Autumn Balance Gras\n",
                "42. Gras Berry Essence Gras\n",
                "43. Gras Herbal Remedy Gras\n",
                "44. Gras Wind-Cool Vitality Gras\n",
                "45. Gras Eye Essence Gras\n",
                "46. Gras Liver Remedy Gras\n",
                "47. Gras Essence Brightener Gras\n",
                "48. Gras Sumsum Harmony Gras\n",
                "49. Gras Herbal Essence Gras\n",
                "50. Gras Berry Elixir Gras"
            ]
    
    print(model_startswith_each(["gras"], x))
    # print(model_startswith_each(["Gras"], x))