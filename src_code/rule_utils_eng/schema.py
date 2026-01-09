import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jsonschema
from src_code.utils_eng import str_to_lists, json_from_string
try:
    import jsonschema
    jsonschema_AVAILABLE = True
except ImportError:
    jsonschema_AVAILABLE = False
    print("jsonschema库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("jsonschema库安装成功，正在导入...")
        import jsonschema
        jsonschema_AVAILABLE = True
        print("✅ jsonschema库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install jsonschema")
        jsonschema_AVAILABLE = False

def model_schema(item, key, model_response):
    if key == "json_schema":
        return json_schema(item, model_response)
    elif key == "list":
        return list_schema(model_response)


def json_schema(item, model_response):
    schema = item["json_schema"]
    try:
        data = json_from_string(model_response)
        print("data: ", data)
        # 根据顶层schema决定如何处理数据
        if schema.get("type") == "array":
            # 如果schema顶层是数组，data应该直接是数组
            if isinstance(data, list):
                # 数据本身就是数组，直接使用
                pass
            else:
                # 数据不是数组，包装成数组
                data = [data]
        else:
            # 如果schema顶层是对象，检测响应是否为对象而非数组
            if not isinstance(data, list) and isinstance(data, dict):
                data = [data]


        results = []
        point_id = -1
        
        def extract_validation_points(schema, path="", parent_data=None):
            """递归提取所有需要验证的点"""
            points = []
            
            if schema.get("type") == "object":
                # 处理对象类型
                properties = schema.get("properties", {})
                required_fields = schema.get("required", [])
                
                for field_name in required_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    field_schema = properties.get(field_name, {})
                    ability = field_schema.get("能力项", "JSON")
                    
                    # 添加当前字段的验证点
                    # 在能力项中添加JSON标签
                    final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                    points.append({
                        "path": field_path,
                        "field_name": field_name,
                        "schema": field_schema,
                        "ability": final_ability,
                        "is_required": True
                    })
                    
                    # 递归处理嵌套结构
                    if field_schema.get("type") == "object":
                        nested_points = extract_validation_points(field_schema, field_path)
                        points.extend(nested_points)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        # 处理数组中的嵌套对象
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_points = extract_validation_points(items_schema, f"{field_path}[*]")
                            points.extend(nested_points)
                
                # 处理非必需字段，但在数组items中的所有字段都需要验证
                if path.endswith("[*]"):  # 这是数组项的schema
                    for field_name, field_schema in properties.items():
                        if field_name not in required_fields:
                            field_path = f"{path}.{field_name}" if path else field_name
                            ability = field_schema.get("能力项", "JSON")
                            final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                            
                            points.append({
                                "path": field_path,
                                "field_name": field_name,
                                "schema": field_schema,
                                "ability": final_ability,
                                "is_required": False  # 标记为非必需
                            })
            
            elif schema.get("type") == "array" and "items" in schema:
                # 处理数组类型
                items_schema = schema["items"]
                if items_schema.get("type") == "object":
                    nested_points = extract_validation_points(items_schema, f"{path}[*]" if path else "[*]")
                    points.extend(nested_points)
            
            return points


        def get_nested_value(data, path):
            """根据路径获取嵌套数据的值，区分None和不存在"""
            if not path:
                return data, True  # 返回值和是否存在的标志
            
            parts = path.split('.')
            current = data
            
            try:
                for part in parts:
                    if '[*]' in part:
                        # 处理数组情况
                        field_name = part.replace('[*]', '')
                        if field_name:
                            current = current[field_name]
                        # 返回数组，让调用者处理每个元素
                        return current, True
                    else:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return None, False  # 字段不存在
                return current, True  # 字段存在，即使值为None
            except (KeyError, TypeError, IndexError):
                return None, False


        def validate_field(data_item, validation_point):
            """验证单个字段"""
            path = validation_point["path"]
            field_name = validation_point["field_name"]
            field_schema = validation_point["schema"]
            ability = validation_point["ability"]
            is_required = validation_point["is_required"]
            
            # 处理路径中包含数组索引的情况
            if '[*]' in path:
                # 获取数组路径和字段路径
                path_parts = path.split('[*]')
                array_path = path_parts[0]
                field_path = path_parts[1].lstrip('.')
                
                # 获取数组数据
                if array_path:
                    array_data, array_exists = get_nested_value(data_item, array_path)
                    if not array_exists:
                        return {
                            "question": f"{path}是否符合要求",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - 数组路径不存在",
                            "能力项": ability
                        }
                else:
                    array_data = data_item
                    array_exists = True
                
                if not isinstance(array_data, list):
                    return {
                        "question": f"{path}是否符合要求",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - 期望数组类型，实际为{type(array_data).__name__}",
                        "能力项": ability
                    }
                
                # 统计字段在数组中的出现情况
                found_count = 0
                valid_count = 0
                error_messages = []
                
                for i, item in enumerate(array_data):
                    if field_path:
                        # 检查嵌套字段
                        nested_value, field_exists = get_nested_value(item, field_path)
                        if field_exists:  # 字段存在（即使值为None）
                            found_count += 1
                            # 验证字段值
                            try:
                                temp_schema = {
                                    "type": "object",
                                    "properties": {field_name: field_schema},
                                    "required": [field_name] if is_required else []
                                }
                                jsonschema.validate({field_name: nested_value}, temp_schema)
                                valid_count += 1
                            except jsonschema.exceptions.ValidationError as e:
                                error_messages.append(f"项{i+1}的{field_path}不符合规则: {e.message}")
                    else:
                        # 验证数组项本身
                        try:
                            jsonschema.validate(item, field_schema)
                            found_count += 1
                            valid_count += 1
                        except jsonschema.exceptions.ValidationError as e:
                            found_count += 1
                            error_messages.append(f"项{i+1}不符合规则: {e.message}")
                
                # 判断验证结果
                if is_required and found_count == 0:
                    return {
                        "question": f"{path}是否符合要求",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - 必需字段在数组中未找到",
                        "能力项": ability
                    }
                elif found_count > 0:
                    if valid_count == found_count:
                        return {
                            "question": f"{path}是否符合要求",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - 在{len(array_data)}个数组项中找到{found_count}个有效值",
                            "能力项": ability
                        }
                    else:
                        return {
                            "question": f"{path}是否符合要求",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - 在{found_count}个值中有{len(error_messages)}个无效: " + "; ".join(error_messages),
                            "能力项": ability
                        }
                else:
                    # 非必需字段且未找到
                    return {
                        "question": f"{path}是否符合要求",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - 可选字段未使用",
                        "能力项": ability
                    }
            else:
                # 处理普通字段路径
                field_value, field_exists = get_nested_value(data_item, path)
                
                if not field_exists and is_required:
                    return {
                        "question": f"{path}是否符合要求",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - 必需字段缺失",
                        "能力项": ability
                    }
                elif field_exists:
                    # 验证字段值（即使是None也要验证）
                    try:
                        temp_schema = {
                            "type": "object",
                            "properties": {field_name: field_schema},
                            "required": [field_name] if is_required else []
                        }
                        jsonschema.validate({field_name: field_value}, temp_schema)
                        return {
                            "question": f"{path}是否符合要求",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - 符合规则",
                            "能力项": ability
                        }
                    except jsonschema.exceptions.ValidationError as e:
                        return {
                            "question": f"{path}是否符合要求",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - 不符合规则: {e.message}",
                            "能力项": ability
                        }
                else:
                    # 字段不存在
                    return {
                        "question": f"{path}是否符合要求",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - 可选字段",
                        "能力项": ability
                    }


        # 提取所有验证点
        validation_points = extract_validation_points(schema)
        
        # 对每个数据项进行验证
        if schema.get("type") == "array":
            # 顶层是数组，验证整个数组
            for validation_point in validation_points:
                result = validate_field(data, validation_point)
                result["point_id"] = point_id
                result["dep"] = []
                results.append(result)
                point_id -= 1
        else:
            # 顶层是对象，逐个验证数组中的每个对象
            for index, item_data in enumerate(data):
                for validation_point in validation_points:
                    result = validate_field(item_data, validation_point)
                    result["point_id"] = point_id
                    result["dep"] = []
                    results.append(result)
                    point_id -= 1


        return results
    
    except Exception as e:
        # 异常处理：创建所有验证点的失败结果
        results = []
        point_id = 0
        
        def extract_all_fields(schema, path=""):
            """提取所有字段用于异常情况"""
            fields = []
            if schema.get("type") == "object":
                properties = schema.get("properties", {})
                required_fields = schema.get("required", [])
                
                for field_name in required_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    field_schema = properties.get(field_name, {})
                    ability = field_schema.get("能力项", "JSON")
                    final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                    fields.append((field_path, final_ability))
                    
                    # 递归处理嵌套
                    if field_schema.get("type") == "object":
                        nested_fields = extract_all_fields(field_schema, field_path)
                        fields.extend(nested_fields)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_fields = extract_all_fields(items_schema, f"{field_path}[*]")
                            fields.extend(nested_fields)
                
                # 添加数组项中的非必需字段
                if path.endswith("[*]"):
                    for field_name, field_schema in properties.items():
                        if field_name not in required_fields:
                            field_path = f"{path}.{field_name}" if path else field_name
                            ability = field_schema.get("能力项", "JSON")
                            final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                            fields.append((field_path, final_ability))
            
            return fields
        
        all_fields = extract_all_fields(schema)
        
        for field_path, ability in all_fields:
            results.append({
                "point_id": point_id,
                "question": f"{field_path}是否符合要求",
                "dep": [],
                "eval_result": 0,
                "eval_explanation": f"❌ {field_path} - JSON解析失败: {str(e)}",
                "能力项": ability
            })
            point_id += 1 
        
        return results
    
     
def list_schema(model_response):
    try:
        model_response = str_to_lists(model_response)
    except Exception as e:
        return 0, f"INVALID LIST: ERROR DETAILS: {str(e)}"
    return 1, "VALID LIST"



if __name__ == '__main__':
    item =   {
        "category": "SCHEMA",
        "question": "You are a senior travel expert and professional article analyst. I will provide you with an article that recommends suitable travel destinations. Your task is to analyze this article and extract information from it by attraction name dimension.\n\n1. poiName: Extract the names of attractions mentioned in the article. Attractions must be location-level geographical positions, absolutely not cities or provinces. For example: botanical gardens, parks, ancient towns, scenic areas, museums, temples and other specific attractions (such as Taiyuan Botanical Garden, Jingshan Park, Gubei Water Town).\n\nOutput requirements:\n1. Return extracted information in JSON format\n2. Each attraction as a separate object, containing poiName field\n3. All attraction objects form an array\n4. Do not return any characters other than JSON format\nYou need to identify the type of each attraction (such as park, ancient town, museum, temple, theme park, scenic area, etc.), and return the poiType field in json.\nYou need to identify whether each attraction is suitable for parent-child play (return \"Yes\" if suitable, otherwise return \"No\"), and return the isParentChildFriendly field in json.\nYou need to identify whether each attraction has night view (return \"Yes\" if it has night view, otherwise return \"No\"), and return the hasNightView field in json.\nOutput format example:\n[\n  {\"poiName\": \"example value\", \"poiType\": \"example type\", \"isParentChildFriendly\": \"Yes/No\", \"hasNightView\": \"Yes/No\"}\n]\n\nArticle content:Beijing surrounding tour recommendations:\n1. Taiyuan Botanical Garden is the largest botanical garden in North China, suitable for parent-child tours\n2. Jingshan Park overlooks the panoramic view of the Forbidden City\n3. The night view of Gubei Water Town is stunning, recommend staying in the scenic area",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "poiName",
                    "poiType",
                    "isParentChildFriendly",
                    "hasNightView"
                ],
                "properties": {
                    "poiName": {
                        "type": "string",
                        "description": "Attraction name, must be a specific location-level geographical position",
                        "能力项": "JSON"
                    },
                    "poiType": {
                        "type": "string",
                        "description": "Attraction type, such as park, ancient town, museum, temple, theme park, scenic area, etc.",
                        "能力项": "JSON"
                    },
                    "isParentChildFriendly": {
                        "type": "string",
                        "enum": [
                            "Yes",
                            "No"
                        ],
                        "description": "Whether it is suitable for parent-child",
                        "能力项": "特定格式"
                    },
                    "hasNightView": {
                        "type": "string",
                        "enum": [
                            "Yes",
                            "No"
                        ],
                        "description": "Whether it has night view",
                        "能力项": "特定格式"
                    }
                },
                "additionalProperties": False
            }
        },
        "sub_questions": [
            {
                "question": "[*].poiName是否符合要求",
                "eval_result": 1,
                "eval_explanation": "✅ [*].poiName - 在6个数组项中找到6个有效值",
                "能力项": "JSON",
                "point_id": -1,
                "dep": []
            },
            {
                "question": "[*].poiType是否符合要求",
                "eval_result": 1,
                "eval_explanation": "✅ [*].poiType - 在6个数组项中找到6个有效值",
                "能力项": "JSON",
                "point_id": -2,
                "dep": []
            },
            {
                "question": "[*].isParentChildFriendly是否符合要求",
                "eval_result": 1,
                "eval_explanation": "✅ [*].isParentChildFriendly - 在6个数组项中找到6个有效值",
                "能力项": "特定格式、JSON",
                "point_id": -3,
                "dep": []
            },
            {
                "question": "[*].hasNightView是否符合要求",
                "eval_result": 1,
                "eval_explanation": "✅ [*].hasNightView - 在6个数组项中找到6个有效值",
                "能力项": "特定格式、JSON",
                "point_id": -4,
                "dep": []
            }
        ],
        "model_response": "```json\n[\n  {\"poiName\": \"Taiyuan Botanical Garden\", \"poiType\": \"botanical garden\", \"isParentChildFriendly\": \"Yes\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Jingshan Park\", \"poiType\": \"park\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Gubei Water Town\", \"poiType\": \"ancient town\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"Yes\"}\n]\n```"
    }

    model_response = "```json\n[\n  {\"poiName\": \"Taiyuan Botanical Garden\", \"poiType\": \"botanical garden\", \"isParentChildFriendly\": \"Yes\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Jingshan Park\", \"poiType\": \"park\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Gubei Water Town\", \"poiType\": \"ancient town\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"Yes\"}\n]\n```"

    print(json_schema(item, model_response))