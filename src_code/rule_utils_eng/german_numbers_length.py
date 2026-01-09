import re

def check_number_length(min_length, model_response):
    """
    检查模型输出的数字是否满足指定的最小长度要求。

    :param model_response: 模型输出的数字书写形式（列表）
    :param min_length: 最小字符长度
    :return: True 或 False，表示是否满足要求，以及相关的错误信息
    """

    # 定义数字书写形式的长度要求
    for num_str in model_response:
        if len(num_str) < min_length[0]:
            return False, f"❌ 找到的数字 '{num_str}' 长度为 {len(num_str)}，小于 {min_length}。"

    return True, "✅ 所有数字书写形式符合长度要求。"

# # 示例：模型输出的数字书写形式列表
# model_response1 = [
#     "dreihundertfünfundsechzigtausendvierhundertachtundzwanzig",
#     "neunhundertneunundneunzigtausendneunhundertneunundneunzig",
#     "zweimillionendreihundertvierundfünfzigtausendsechshundertneunundachtzig"
# ]

# model_response2 = [
#     "dreihundertfünfundsechzigtausendvierhundertachtundzwanzig",
#     "neunhundertneunundneunzigtausendneunhundertneunundneunzig",
#     "zweimillionendreihundertvierundfünfzigtausend"
# ]

# # 设置最小长度要求
# minimum_length1 = [15,15]  # 最小长度为 15
# minimum_length2 = [20,20]  # 最小长度为 20

# # 调用函数进行长度检查
# is_correct_length1 = check_number_length(minimum_length1, model_response1)
# is_correct_length2 = check_number_length(minimum_length2, model_response2)

# print("检查结果1:", is_correct_length1)
# print("检查结果2:", is_correct_length2)
