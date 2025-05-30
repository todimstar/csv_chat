from config import ai_config

class AISuggest:
    def __init__(self):
        """
        初始化AI分析器。
        它会使用 src/config.py 中的 ai_config 实例来获取配置。
        """
        self.config = ai_config

        if not self.config.is_configured():
            print("警告: AI服务API密钥未在 config.py 中配置。AI分析功能可能无法使用。")
        # 实际应用中，这里可以初始化API客户端，例如 openai.api_key = self.config.api_key

    def aisuggest_disk_usage_summary(self, summary_data):
        """
        使用AI分析磁盘使用摘要数据。

        :param summary_data: 一个包含磁盘使用摘要信息的字符串或字典。
                             例如："总大小: 100GB, 图片: 20GB (20%), 视频: 50GB (50%), 其他: 30GB (30%)..."
        :return: AI生成的分析结果字符串，或者在出错时返回None。
        \n///<summary>\nsystem_prompt = '''你是一个专业的磁盘空间分析助手。你的任务是：
        1. 分析用户提供的磁盘使用数据
        2. 识别主要的空间占用来源
        3. 提供至少3条具体的、可操作的优化建议
        4. 建议应该考虑数据安全性，不要建议删除可能重要的系统文件
        5. 使用清晰的格式展示分析结果，让用户容易理解'''
        
        \n///<summary>\nuser_content = f"请分析以下磁盘使用情况，并给出优化建议：{summary_data}"
        """
        if not self.config.is_configured():
            return "AI服务未配置，无法进行分析。请在 src/config.py 中设置 API 密钥。"

        
        from aiapi import get_ai_analysis
        
        system_prompt = """你是一个专业的磁盘空间分析助手。你的任务是：
        1. 分析用户提供的磁盘使用数据
        2. 识别主要的空间占用来源
        3. 提供至少3条具体的、可操作的优化建议
        4. 建议应该考虑数据安全性，不要建议删除可能重要的系统文件
        5. 使用清晰的格式展示分析结果，让用户容易理解"""
        
        user_content = f"请分析以下磁盘使用情况，并给出优化建议：\n{summary_data}"
        
        try:
            ai_result = get_ai_analysis(user_content, system_prompt)
            print("AI分析完成。")
            return ai_result
        except Exception as e:
            print(f"调用AI API时发生错误: {e}")
            return f"AI分析失败: {e}"
        

    def aisuggest_files_for_cleanup(self, file_list_dic):
        """
        根据文件列表（dic/str）建议可以清理的文件。

        :param file_list_str: 包含文件列表信息的string或字典。
        :return: AI生成的清理建议字符串，或者在出错时返回None。
        """
        if not self.config.is_configured():
            return "AI服务未配置，无法提供清理建议。请在 src/config.py 中设置 API 密钥。"

        # 检查字典是否为空
        if not file_list_dic:
            return "没有文件数据可供分析以提供清理建议。"

        from aiapi import get_ai_analysis

        
        system_prompt = """你是一个专业的文件清理顾问。你的任务是：
        1. 分析用户提供的文件列表,推测文件之间可能的联系
        2. 应该尽力搜集信息推测可能可以清理的文件类型和具体文件
        3. 提供具体的清理建议，至少包括：
        - 文件列表中哪些文件可以安全删除
        - 哪些文件可以适当删除，但强调风险
        - 如何判断具体文件是否可以删除
        - 清理前应该注意的安全事项
        4. 建议应该有理有据，但不要建议删除可能影响系统正常运行的文件
        5. 使用清晰的格式展示建议，便于用户理解和操作"""
        
        user_content = f"请分析以下文件列表，并给出清理建议：\n{file_list_dic}"
        try:
            ai_result = get_ai_analysis(user_content, system_prompt)
            print("AI清理建议生成完成。")
            return ai_result
        except Exception as e:
            print(f"生成AI清理建议时发生错误: {e}")
            return f"AI清理建议生成失败: {e}"
        

    def aisuggest_folder_contents(self, folder_path, file_details_dic, user_query=None):
        """
        使用AI分析特定文件夹的内容，并可以结合用户提出的具体问题。

        :param folder_path: 用户想要分析的文件夹路径。
        :param file_details_dic: 包含该文件夹内文件信息的字典或str。
                                 传输前的字典或字符串应该由专门分析后返回本模块不负责处理数据
                                 对处理前数据可能的要求Pandas DataFrame应至少包含 'File Name', 'Size', 'Path', 'Time', 'Type' (可选) 列。
        :param user_query: 用户关于此文件夹内容的具体问题 (可选)。
        :return: AI生成的关于文件夹内容的分析和解答字符串，或出错时返回None。
        """
        if not self.config.is_configured():
            return "AI服务未配置，无法进行文件夹内容分析。请在 src/config.py 中设置 API 密钥。"

        if file_details_dic.empty:
            return f"文件夹 {folder_path} 中没有文件数据可供分析。"

        from aiapi import get_ai_analysis # 确保导入

        system_prompt = """
        你是一个智能文件夹分析助手。你的任务是：
        1. 分析用户提供的文件夹内容摘要（包括文件类型统计和大文件示例）。
        2. 如果用户提出了具体问题，请优先并详细地回答该问题。
        3. 如果用户没有提问，请对文件夹内容进行通用性分析，例如：
           - 这个文件夹可能用于什么目的？
           - 哪些文件类型占据主要空间？
           - 是否有可以安全清理或归档的文件类型建议？
        4. 给出关于文件管理、清理或优化的具体建议。
        5. 如果发现潜在的风险文件（如大量可执行文件、脚本在非预期位置），请提示用户注意安全。
        6. 分析结果应该清晰、易懂、具有可操作性。"""

        user_content = ""
        if user_query:
            user_content += f"\n用户关于此文件夹的具体问题是：'{user_query}'"
            user_content += f"\n请针对以上信息和问题进行分析并解答：{file_details_dic}"
        else:
            user_content += f"\n用户没有提出具体问题，请直接对文件夹内容进行分析：{file_details_dic}"
        
        try:
            ai_result = get_ai_analysis(user_content, system_prompt)
            print(f"AI对文件夹 '{folder_path}' 的分析完成。")
            return ai_result
        except Exception as e:
            print(f"分析文件夹 '{folder_path}' 时发生AI API调用错误: {e}")
            return f"AI分析文件夹 '{folder_path}' 失败: {e}"

    

# 示例用法 (用于测试此模块)
if __name__ == "__main__":
    # 现在配置通过 src/config.py 管理
    # 您需要编辑 src/config.py 文件并填入您的 API 密钥
    # from src.config import ai_config
    # ai_config.update_config(api_key="YOUR_API_KEY_HERE")
    analyzer = AISuggest()

    # 测试分析磁盘使用摘要
    sample_summary = "总大小: 500GB, 图片: 100GB (20%), 视频: 250GB (50%), 文档: 50GB (10%), 其他: 100GB (20%)"
    analysis_result = analyzer.aisuggest_disk_usage_summary(sample_summary)
    print("\n--- 磁盘使用摘要分析 ---")
    print(analysis_result)

    # 测试清理建议
    # 创建一个示例Data
    try:
        data = {
            'File Name': ['video1.mp4', 'photo_archive.zip', 'document.pdf', 'large_log.txt', 'system_file.dll'],
            'Size': [2000000000, 500000000, 10000000, 800000000, 50000000], # Bytes
            'Path': ['/videos/video1.mp4', '/backups/photo_archive.zip', '/docs/document.pdf', '/logs/large_log.txt', '/system/system_file.dll']
        }
        cleanup_suggestion = analyzer.aisuggest_files_for_cleanup(data)
        print("\n--- 文件清理建议 ---")
        print(cleanup_suggestion)

    except Exception as e:
        print(f"执行清理建议示例时出错: {e}")

    # 测试分析特定文件夹内容
    try:
        folder_files_data = {
            'File Name': ['project_alpha.docx', 'temp_image.jpg', 'archive_2022.zip', 'notes.txt', 'old_backup.bak', 'report_final_v2.pdf'],
            'Size': [1500000, 2500000, 150000000, 50000, 250000000, 5000000], # Bytes
            'Path': ['/documents/project_alpha.docx', '/documents/temp_image.jpg', '/documents/archive_2022.zip', '/documents/notes.txt', '/documents/old_backup.bak', '/documents/report_final_v2.pdf'],
            'Type': ['document', 'image', 'archive', 'text', 'backup', 'document']
        }
        
        # 测试1: 无特定问题
        folder_analysis_result_general = analyzer.aisuggest_folder_contents('/documents', folder_files_data)
        print("\n--- 特定文件夹内容分析 (通用) --- ")
        print(folder_analysis_result_general)

        # 测试2: 带特定问题
        user_q = "这个文件夹里的压缩包和备份文件是做什么的？可以删除吗？"
        folder_analysis_result_specific = analyzer.aisuggest_folder_contents('/documents', folder_files_data, user_query=user_q)
        print(f"\n--- 特定文件夹内容分析 (问题: {user_q}) --- ")
        print(folder_analysis_result_specific)

    except Exception as e:
        print(f"执行特定文件夹内容分析示例时出错: {e}")