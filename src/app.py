import streamlit as st
import pandas as pd
from main import analyze_data, format_size_dynamically # 假设main.py中有一个analyze_data函数
from ai_analyzer import AISuggest # 假设ai_analyzer.py可用

# 设置页面配置，例如标题和图标
st.set_page_config(page_title="AI 磁盘空间分析助手", layout="wide")

def main():
    st.title("✨ AI 磁盘空间分析助手 ✨")
    st.markdown("上传您的 WizTree CSV 文件，让我来帮您分析磁盘空间使用情况！")

    uploaded_file = st.file_uploader("选择 WizTree CSV 文件", type=["csv"])

    if uploaded_file is not None:
        st.success(f"文件 '{uploaded_file.name}' 上传成功！")
        
        # 读取CSV数据
        # 尝试多种编码读取，以提高兼容性
        encodings_to_try = ['utf-8', 'gbk', 'latin1']
        df = None
        for encoding in encodings_to_try:
            try:
                # WizTree的CSV通常从第二行开始是数据，第一行是元信息
                df = pd.read_csv(uploaded_file, skiprows=1, encoding=encoding)
                st.write(f"使用 {encoding} 编码成功读取文件。")
                break # 成功读取后跳出循环
            except Exception as e:
                st.write(f"尝试使用 {encoding} 编码读取失败: {e}")
                continue
        
        if df is None:
            st.error("无法读取CSV文件。请确保文件格式正确，或尝试其他编码。")
            return

        # 数据预处理和列名标准化 (与 main.py 中的逻辑类似)
        df.columns = [col.strip() for col in df.columns]
        rename_map = {
            '文件名称': 'File Name',
            '大小': 'Size',
            '路径': 'Path',
            # 根据实际WizTree输出的列名添加更多映射
        }
        df.rename(columns=rename_map, inplace=True)

        if 'Size' not in df.columns:
            st.error("CSV文件中未找到 'Size' 列，请检查文件格式。")
            return
        if 'File Name' not in df.columns:
            st.error("CSV文件中未找到 'File Name' 列，请检查文件格式。")
            return
        
        # 如果 'Path' 列不存在，但 'File Name' 列存在，则使用 'File Name' 作为 'Path'
        if 'Path' not in df.columns and 'File Name' in df.columns:
            st.info("CSV文件中未找到 'Path' 列，将使用 'File Name' 列作为路径。")
            df['Path'] = df['File Name']
        elif 'Path' not in df.columns:
            st.error("CSV文件中未找到 'Path' 列，并且无法从 'File Name' 创建。请检查文件格式。")
            return

        # 将 'Size' 列转换为数值类型，处理非数字和空值
        df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
        df.dropna(subset=['Size'], inplace=True)
        df['Size'] = df['Size'].astype(float) # 确保是浮点数以便后续计算

        st.markdown("---数据预览---")
        st.dataframe(df.head())

        # 调用 src.main.py 中的 analyze_data 函数进行分析
        st.markdown("--- 详细分析结果 ---")
        with st.spinner('正在分析数据，请稍候...'):
            # 注意：main.py 中的 analyze_data 内部有很多 print 语句，会输出到控制台
            # 为了在 Streamlit 中获得更纯净的体验，理想情况下 analyze_data 应避免直接 print
            # 但此处我们先直接调用
            analysis_results = analyze_data(df) # analyze_data 来自 src.main

        if analysis_results:
            if analysis_results.error_messages:
                for error_msg in analysis_results.error_messages:
                    st.error(f"分析错误: {error_msg}")
            
            st.subheader("基本统计")
            st.metric(label="扫描项目总数", value=f"{analysis_results.total_items_count:,}")
            st.metric(label="总占用空间", value=format_size_dynamically(analysis_results.total_scan_size_bytes))

            st.subheader("占用空间最大的条目")
            if analysis_results.largest_items and len(analysis_results.largest_items) > 1:
                # largest_items[0] 是标题字符串，之后是 (路径, 大小) 元组
                largest_items_df_data = []
                for item in analysis_results.largest_items[1:]:
                    if isinstance(item, tuple) and len(item) == 2:
                        largest_items_df_data.append({'Path': item[0], 'Size_bytes': item[1]})
                
                if largest_items_df_data:
                    largest_items_df = pd.DataFrame(largest_items_df_data)
                    largest_items_df['Size'] = largest_items_df['Size_bytes'].apply(format_size_dynamically)
                    st.table(largest_items_df[['Path', 'Size']])
                else:
                    st.write("未能提取最大的条目信息。")
            elif analysis_results.largest_items:
                 st.write(analysis_results.largest_items[0]) # 如果只有一个元素，可能是错误信息
            else:
                st.write("没有找到最大的文件/文件夹信息。")

            st.subheader("按文件类型分类统计")
            if analysis_results.category_stats:
                # category_stats 的结构是 { '标题': {'类别': '统计信息字符串', ...} } 或 {'错误信息key': '错误信息'}
                # 我们需要找到包含实际统计数据的那个键
                stats_data_key = next((key for key in analysis_results.category_stats if isinstance(analysis_results.category_stats[key], dict)), None)
                if stats_data_key and isinstance(analysis_results.category_stats[stats_data_key], dict):
                    st.write(f"**{stats_data_key}**")
                    category_df_data = []
                    for category, stats_str in analysis_results.category_stats[stats_data_key].items():
                        # 解析 '大小 (数量, 百分比)' 格式的字符串会比较复杂
                        # 简单起见，我们直接显示字符串，或者可以考虑修改 main.py 让其返回更结构化的数据
                        category_df_data.append({'类别': category, '统计': stats_str})
                    if category_df_data:
                        category_df = pd.DataFrame(category_df_data)
                        st.table(category_df)
                    
                    # 尝试为类别统计创建饼图 (需要从字符串中提取数值)
                    try:
                        pie_chart_data = {}
                        for category, stats_str in analysis_results.category_stats[stats_data_key].items():
                            # 尝试从 '1.23 GB (10 个条目, 12.34%)' 提取大小 (GB) 和百分比
                            # 这部分比较脆弱，依赖于 format_size_dynamically 和 print 格式
                            # 更好的做法是让 analyze_data 返回原始数值
                            size_part = stats_str.split('(')[0].strip()
                            size_value = float(size_part.split(' ')[0])
                            size_unit = size_part.split(' ')[1]
                            # 转换为 MB 以便比较
                            if size_unit == 'KB': size_value /= 1024
                            elif size_unit == 'GB': size_value *= 1024
                            elif size_unit == 'TB': size_value *= (1024*1024)
                            pie_chart_data[category] = size_value # 大小（MB）
                        
                        if pie_chart_data:
                            pie_df = pd.Series(pie_chart_data).sort_values(ascending=False)
                            st.write("文件类型空间占比 (MB):")
                            st.bar_chart(pie_df)
                    except Exception as e:
                        st.write(f"无法为文件类型生成图表: {e}")

                elif analysis_results.category_stats.get("calculate_category_stats().error"):
                     st.warning(f"文件类型统计时发生错误: {analysis_results.category_stats['calculate_category_stats().error']}")       
                else:
                    st.write("未能解析文件类型统计数据。")
            else:
                st.write("没有文件类型统计信息。")

            st.subheader("按文件扩展名统计 (Top 20)")
            if analysis_results.extension_stats:
                stats_data_key = next((key for key in analysis_results.extension_stats if isinstance(analysis_results.extension_stats[key], dict)), None)
                if stats_data_key and isinstance(analysis_results.extension_stats[stats_data_key], dict):
                    st.write(f"**{stats_data_key}**")
                    ext_df_data = []
                    raw_ext_sizes = {}
                    for ext, size_bytes in analysis_results.extension_stats[stats_data_key].items():
                        ext_df_data.append({'扩展名': f".{ext}", '大小': format_size_dynamically(size_bytes)})
                        raw_ext_sizes[f".{ext}"] = size_bytes
                    if ext_df_data:
                        ext_df = pd.DataFrame(ext_df_data)
                        st.table(ext_df)
                    
                    if raw_ext_sizes:
                        ext_pie_df = pd.Series(raw_ext_sizes).sort_values(ascending=False)
                        st.write("扩展名空间占比 (Bytes):")
                        st.bar_chart(ext_pie_df)
                elif analysis_results.extension_stats.get("calculate_category_stats().error"): # 修正可能的笔误，应该是 extension_stats 的错误key
                     st.warning(f"文件扩展名统计时发生错误: {analysis_results.extension_stats.get('calculate_category_stats().error', '未知错误')}")
                else:
                    st.write("未能解析文件扩展名统计数据。")
            else:
                st.write("没有文件扩展名统计信息。")
        else:
            st.error("数据分析未能返回结果。")

        # AI 分析集成 (占位符或调用实际AI)
        st.markdown("--- AI 分析与建议 ---")
        analyzer = AISuggest() # AIAnalyzer 会尝试从环境变量或config读取API密钥
        
        # 准备摘要给AI
        #summary_for_ai = f"总扫描项目数: {analysis_results.total_items_count}, 总占用空间: {format_size_dynamically(analysis_results.total_scan_size_bytes)}."
        summary_for_ai = analysis_results.to_summary_dict()
        # 可以在这里添加更多摘要信息，比如主要文件类型等
        
        with st.spinner('AI 正在分析磁盘使用摘要...'):
            ai_summary_analysis = analyzer.aisuggest_disk_usage_summary(summary_for_ai)
        st.subheader("AI 磁盘使用摘要分析")
        st.markdown(ai_summary_analysis)

        with st.spinner('AI 正在生成文件清理建议...'):
            # 传递整个DataFrame或其摘要给AI
            # summary_for_ai = analysis_results.to_summary_dict()
            # 
            ai_cleanup_suggestion = analyzer.aisuggest_files_for_cleanup(summary_for_ai) # 
        st.subheader("AI 文件清理建议")
        st.markdown(ai_cleanup_suggestion)

        # AI分析特定文件夹 (示例)
        st.markdown("--- AI 分析特定文件夹内容 ---")
        # 允许用户输入文件夹路径和问题
        # 注意：在Web应用中直接访问本地文件系统路径需要特别处理或让用户上传文件夹内容的CSV
        # 这里简化为让用户输入一个“虚拟”的文件夹路径（存在于CSV中）和问题
        folder_path_query = st.text_input("输入您想分析的文件夹路径 (基于CSV中的路径):", key="folder_path_q")
        user_query_folder = st.text_area("您对这个文件夹有什么具体问题吗？", key="user_query_f")

        if st.button("分析指定文件夹", key="analyze_folder_btn") and folder_path_query:
            # 从DataFrame中筛选出该文件夹下的文件
            # 注意：WizTree的路径可能是 'C:\Folder\Subfolder'，也可能是 'C:\Folder\Subfolder\file.txt'
            # 我们需要找到所有以 folder_path_query 开头的条目
            folder_files_df = df[df['Path'].str.startswith(folder_path_query, na=False) & (df['Path'] != folder_path_query)]
            
            if not folder_files_df.empty:
                with st.spinner(f"AI 正在分析文件夹 '{folder_path_query}'..."):
                    ai_folder_analysis = analyzer.aisuggest_folder_contents(
                        folder_path=folder_path_query, 
                        file_details_dic=folder_files_df, 
                        user_query=user_query_folder if user_query_folder else None
                    )
                st.subheader(f"AI 对文件夹 '{folder_path_query}' 的分析结果")
                st.markdown(ai_folder_analysis)
            else:
                st.warning(f"在上传的CSV中没有找到路径以 '{folder_path_query}' 开头的文件/子文件夹。请确保路径正确。")

    else:
        st.info("请上传一个 CSV 文件开始分析。")

    st.sidebar.header("关于")
    st.sidebar.info(
        "这是一个使用 Streamlit 构建的 AI 磁盘空间分析助手。"
        "它可以帮助您理解 WizTree 导出的 CSV 文件中的磁盘使用情况，并提供 AI 驱动的分析和建议。"
    )

if __name__ == "__main__":
    main()