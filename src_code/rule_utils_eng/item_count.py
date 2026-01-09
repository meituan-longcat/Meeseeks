def model_item_count(range, model_response):
    res_len = len(model_response)
    if not range[0] <= res_len <= range[1]:
        return 0, f"❌ 数量不匹配，产生的item数量为：{str(res_len)}"
    return 1, f"✅ 数量匹配，产生的item数量为 {str(res_len)}"