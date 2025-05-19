import json
json_indent_defult = input()
try:
    # 将输入的字符串解析为JSON对象
    json_obj = json.loads(json_indent_defult)
    # 重新格式化JSON并打印，设置缩进为4个空格
    print("\n" + json.dumps(json_obj, indent=4, ensure_ascii=False))
except json.JSONDecodeError:
    print("输入的不是有效的JSON格式")
