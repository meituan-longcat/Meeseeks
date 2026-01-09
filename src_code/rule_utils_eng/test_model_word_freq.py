# coding = utf-8
#!/usr/bin/env python3
"""
model_word_freq 函数的测试用例
测试关键词频率检查功能
"""

import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .keywords import model_word_freq
from src_code.utils_eng import to_lowercase_list

print("=" * 80)
print("model_word_freq 函数测试用例")
print("=" * 80)

# 测试数据
model_response = """
大家好，我是一个来自遥远地方的有趣灵魂，来到上海这座充满活力的城市，感受着这里的繁华与多元。小时候我喜欢在院子里追逐蝴蝶，也爱在雨天听老奶奶讲故事。我的家乡有很多美食，但来到上海后，我发现这里的生煎和小笼包更让我流口水。我喜欢在黄浦江边散步，欣赏上海夜景，偶尔会和朋友一起去外滩拍照。我的性格开朗，喜欢结交新朋友，尤其是在上海这样的大都市，认识了很多来自世界各地的人。平时我喜欢看书，尤其是科幻小说，也爱听音乐，偶尔会弹吉他。我觉得生活就像一场冒险，每天都充满新鲜事物。来到上海后，我学会了用上海话点菜，虽然发音还不标准，但老板娘总是很热情地纠正我。我的梦想是能在上海实现自己的价值，成为一个有趣又有用的人。说到工作，我在APP开发领域有丰富经验。曾经参与过多个APP项目，从需求分析到上线运营，每个环节都亲力亲为。比如我在一个电商APP项目中，负责前端界面设计和后端数据交互，采用了最新的Flutter技术，让用户体验更加流畅。还记得有一次，客户突然要求增加一个社交功能，我和团队连夜加班，最终在上海的办公室里完成了任务，客户非常满意。在另一个健康管理APP项目中，我负责数据采集和分析模块，利用AI算法提升了用户健康建议的准确性。我的代码风格简洁，注重可维护性，团队成员都说和我合作很愉快。曾经在上海举办的APP开发大赛中获得过二等奖，那次经历让我认识到创新的重要性。除了开发，我还参与过APP的测试和优化工作，发现并修复了多个关键bug，保障了产品稳定运行。我的APP开发经验不仅限于技术层面，还包括与产品经理、设计师的沟通协作，确保每个APP都能满足用户需求。每次看到自己的APP在上海的地铁里被用户使用，我都感到非常自豪。说到数据挖掘，我在这个领域也有不少心得。曾经在上海一家互联网公司担任数据分析师，负责用户行为数据挖掘。通过构建用户画像，帮助公司精准营销，提升了APP用户活跃度。还参与过金融APP的数据风控项目，利用机器学习模型识别高风险用户，有效降低了坏账率。我的数据挖掘方法包括数据清洗、特征工程、模型训练和结果可视化，能够独立完成从数据到决策的全过程。曾经在上海的一个医疗APP项目中，分析用户健康数据，发现了影响用户睡眠质量的关键因素，为产品优化提供了科学依据。我的数据挖掘工具包括Python、R、SQL等，熟练使用pandas、scikit-learn等库。团队成员都说我思路清晰，善于发现问题并提出解决方案。还记得有一次在上海的咖啡馆里，和同事讨论APP用户增长策略，灵感迸发，最终制定了有效的数据驱动方案。我的数据挖掘经验不仅限于技术，还包括与业务部门的沟通，确保数据分析结果能够落地应用。每次看到自己的分析成果在上海的APP产品中发挥作用，我都感到非常有成就感。工作之余，我喜欢参加上海的技术沙龙，结识志同道合的朋友，一起交流APP开发和数据挖掘的最新趋势。我的工作态度积极，喜欢挑战新技术，乐于分享经验。每当遇到难题，我总是能用幽默化解压力，团队气氛也因此更加轻松。我相信，只有不断学习和创新，才能在上海这样竞争激烈的环境中脱颖而出。我的目标是成为上海最有趣、最专业的APP开发和数据挖掘专家。希望能在上海的工作中继续成长，和大家一起创造更美好的未来。工作对我来说不仅是谋生，更是实现自我价值的舞台。每次完成一个APP项目，或是挖掘出有价值的数据洞见，我都感到无比满足。上海给了我很多机会，也让我结识了很多优秀的人。未来我希望能在上海继续深耕APP开发和数据挖掘领域，用自己的专业和热情为公司创造更多价值。感谢您阅读我的简历，期待在上海与您共事，一起用APP和数据改变世界！"""


question = "请根据以下要求生成一份自我介绍：要求在自我介绍中恰好出现3次'上海'这个词汇"

# 测试用例 1: 检查"上海"出现3次（应该通过）
print("\n【测试用例 1】检查'上海'出现3次")
print("-" * 80)
print(f"问题: {question}")
print(f"关键词: ['上海']")
print(f"要求次数: 3")
print(f"文本长度: {len(model_response)} 字符")

# 先统计实际出现次数
actual_count = model_response.count("上海")
print(f"实际出现次数: {actual_count} 次")

result, message = model_word_freq(
    num_need=3,
    keywords=["上海"],
    corresponding_parts=[model_response],
    question=question
)

print(f"\n测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 测试用例 2: 检查"上海"出现5次（应该失败，因为实际出现次数不是5）
print("\n" + "=" * 80)
print("【测试用例 2】检查'上海'出现5次（应该失败）")
print("-" * 80)
print(f"问题: {question}")
print(f"关键词: ['上海']")
print(f"要求次数: 5")
print(f"实际出现次数: {actual_count} 次")

result, message = model_word_freq(
    num_need=5,
    keywords=["上海"],
    corresponding_parts=[model_response],
    question=question
)

print(f"\n测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 测试用例 3: 检查"APP"出现的次数
print("\n" + "=" * 80)
print("【测试用例 3】检查'APP'出现的次数")
print("-" * 80)

app_count = model_response.count("APP")
print(f"关键词: ['APP']")
print(f"实际出现次数: {app_count} 次")

# 测试恰好出现的次数
result, message = model_word_freq(
    num_need=app_count,
    keywords=["APP"],
    corresponding_parts=[model_response],
    question=question
)

print(f"\n要求次数: {app_count}")
print(f"测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 测试用例 4: 检查"数据"出现的次数
print("\n" + "=" * 80)
print("【测试用例 4】检查'数据'出现的次数")
print("-" * 80)

data_count = model_response.count("数据")
print(f"关键词: ['数据']")
print(f"实际出现次数: {data_count} 次")

# 测试恰好出现的次数
result, message = model_word_freq(
    num_need=data_count,
    keywords=["数据"],
    corresponding_parts=[model_response],
    question=question
)

print(f"\n要求次数: {data_count}")
print(f"测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 测试用例 5: 多个部分的文本
print("\n" + "=" * 80)
print("【测试用例 5】多个部分的文本（分割成两部分）")
print("-" * 80)

# 将文本分成两部分
mid_point = len(model_response) // 2
part1 = model_response[:mid_point]
part2 = model_response[mid_point:]

print(f"第一部分长度: {len(part1)} 字符")
print(f"第二部分长度: {len(part2)} 字符")

part1_count = part1.count("上海")
part2_count = part2.count("上海")
total_count = part1_count + part2_count

print(f"\n第一部分'上海'出现次数: {part1_count} 次")
print(f"第二部分'上海'出现次数: {part2_count} 次")
print(f"总计: {total_count} 次")

result, message = model_word_freq(
    num_need=total_count,
    keywords=["上海"],
    corresponding_parts=[part1, part2],
    question=question
)

print(f"\n要求次数: {total_count}")
print(f"测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 测试用例 6: 检查不存在的关键词
print("\n" + "=" * 80)
print("【测试用例 6】检查不存在的关键词")
print("-" * 80)

print(f"关键词: ['北京']")
beijing_count = model_response.count("北京")
print(f"实际出现次数: {beijing_count} 次")

result, message = model_word_freq(
    num_need=0,
    keywords=["北京"],
    corresponding_parts=[model_response],
    question=question
)

print(f"\n要求次数: 0")
print(f"测试结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
print(f"返回值: {result}")
print(f"消息: {message}")

# 总结
print("\n" + "=" * 80)
print("测试总结")
print("=" * 80)
print(f"文本统计信息:")
print(f"  - 总字符数: {len(model_response)}")
print(f"  - '上海'出现次数: {model_response.count('上海')}")
print(f"  - 'APP'出现次数: {model_response.count('APP')}")
print(f"  - '数据'出现次数: {model_response.count('数据')}")
print(f"  - '工作'出现次数: {model_response.count('工作')}")
print(f"  - '项目'出现次数: {model_response.count('项目')}")
print(f"\n✅ 所有测试用例已完成")