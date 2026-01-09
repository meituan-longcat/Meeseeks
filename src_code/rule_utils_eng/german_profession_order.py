import re


def order_profession1_check(model_response):
    """
    检查职位名称是否按照指定顺序且连续出现
    """

    # 定义原始职位名称的顺序
    original_positions = [
        "Lehrer", "Arzt", "Ingenieur", "Professor", "Anwalt", "Musiker", "Journalist", "Politiker",  # 男性职位
        "Köchin", "Bäuerin", "Architektin", "Friseurin", "Künstlerin", "Schneiderin", "Polizistin", "Wissenschaftlerin"  # 女性职位
    ]

    # 在原始顺序的职位名称中检查它们是否按顺序出现在 model_response 中
    positions = []
    for position in model_response:
        try:
            index = original_positions.index(position)  # 查找每个职位在 original_positions 中的索引位置
            positions.append(index)
        except ValueError:
            return False, f"❌ 找的原职位不正确，具体原因：职位 '{position}' 未在文中的原职位列表出现"  # 如果某个职位没有找到，返回错误信息

    # 检查 positions 中的索引是否从0或从第8个开始，分别对应男性和女性职位
    if positions == list(range(0, len(positions))) or positions == list(range(8, 8 + len(positions))):
        return True, "✅ 找的原职位正确"
    else:
        return False, "❌ 找的原职位不正确，具体原因：找的数量不正确或顺序不对"
    

def order_profession2_check(model_response):
    """
    检查职位名称是否按照指定顺序且连续出现
    """

    # 定义被替换后职位名称的顺序
    original_positions = [
        "Lehrerin", "Ärztin", "Ingenieurin", "Professorin", "Anwältin", "Musikerin", "Journalistin", "Politikerin",  # 对应的女性职位
        "Koch", "Bauer", "Architekt", "Friseur", "Künstler", "Schneider", "Polizist", "Wissenschaftler"  # 对应的男性职位
    ]

    # 在原始顺序的职位名称中检查它们是否按顺序出现在 model_response 中
    positions = []
    for position in model_response:
        try:
            index = original_positions.index(position)  # 查找每个职位在 original_positions 中的索引位置
            positions.append(index)
        except ValueError:
            return False, f"❌ 替换后的职位不正确，具体原因：职位 '{position}' 对应的职位名称未在文中的原职位列表出现"  # 如果某个职位没有找到，返回错误信息

    # 检查 positions 中的索引是否从0或从第8个开始，分别对应女性和男性职位
    if positions == list(range(0, len(positions))) or positions == list(range(8, 8 + len(positions))):
        return True, "✅ 替换后的职位正确"
    else:
        return False, "❌ 替换后的职位不正确，具体原因：数量不正确或顺序不对"
    

# 示例：职位名称的列表（只包含部分职位）
# model_response1 = [
#     "Lehrer", "Arzt"
# ]
# model_response2 = [
#     "Arzt", "Lehrer"
# ]
# model_response3 = [
#     "Arzt", "Ingenieur"
# ]

# # 调用函数进行顺序检查
# is_correct_order1 = order_profession1_check(model_response1)
# is_correct_order2 = order_profession1_check(model_response2)
# is_correct_order3 = order_profession1_check(model_response3)

# print("顺序是否正确:", is_correct_order1)
# print("顺序是否正确:", is_correct_order2)
# print("顺序是否正确:", is_correct_order3)


# 示例：被替换后职位名称的列表（只包含部分职位）
# model_response4 = [
#     "Koch", "Bauer"
# ]
# model_response5 = [
#     "Bauer", "Koch"
# ]
# model_response6 = [
#     "Bauer", "Architekt"
# ]

# # 调用函数进行顺序检查
# is_correct_order4 = order_profession2_check(model_response4)
# is_correct_order5 = order_profession2_check(model_response5)
# is_correct_order6 = order_profession2_check(model_response6)

# print("顺序是否正确:", is_correct_order4)
# print("顺序是否正确:", is_correct_order5)
# print("顺序是否正确:", is_correct_order6)