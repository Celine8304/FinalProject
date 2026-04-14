# import json
# import os

# def analyze_xray_result(json_file):
#     if not os.path.exists(json_file):
#         print(f"❌ 找不到文件: {json_file}")
#         return

#     with open(json_file, 'r', encoding='utf-8') as f:
#         try:
#             # Xray 的 JSON 格式是一个列表，每个元素是一个漏洞对象
#             data = json.load(f)
            
#             if not data:
#                 print("✅ 扫描完成，未发现漏洞。")
#                 return

#             print(f"⚠️ 警报！共发现 {len(data)} 个潜在安全风险：\n")
            
#             for index, item in enumerate(data, 1):
#                 # 提取核心信息
#                 plugin = item.get('plugin')      # 插件名 (如 xss)
#                 level = item.get('detail', {}).get('level', 'Unknown') # 危害等级
#                 addr = item.get('detail', {}).get('addr') # 漏洞地址

#                 print(f"[{index}] 等级: {level.upper()}")
#                 print(f"    类型: {plugin}")
#                 print(f"    地址: {addr}")
                
#                 # 如果是高危，可以在这里写发送飞书/钉钉的代码
#                 if level.lower() == 'high':
#                     print("    🔥 这是一个高危漏洞，请立即处理！")
#                 print("-" * 30)

#         except json.JSONDecodeError:
#             print("❌ JSON 文件格式错误或为空")
# # 修改最后一行，把路径填完整
# if __name__ == "__main__":
#     # 比如：analyze_xray_result("/Users/linmohan/Downloads/result.json")
#     analyze_xray_result("/Users/linmohan/Downloads/result.json")