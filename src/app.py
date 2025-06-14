import streamlit as st
import pandas as pd
from deal_csv import to_read_csv,analyze_data, format_size_dynamically 
from ai_analyzer import AISuggest, FolderTooLargeError 
import time
import threading


# 设置页面配置，标题和图标
st.set_page_config(page_title="AI 磁盘空间分析助手", layout="wide")

@st.cache_data
def cache_analyze_data(df):
    return analyze_data(df)

@st.cache_data
def cached_aisuggest_disk_usage_summary(summary_input):
    analyzer = AISuggest()
    return analyzer.aisuggest_disk_usage_summary(summary_input)

@st.cache_data
def cached_aisuggest_files_for_cleanup(summary_input):
    analyzer = AISuggest()
    return analyzer.aisuggest_files_for_cleanup(summary_input)

def main():
    st.title("✨ AI 磁盘空间分析助手 ✨")
    st.markdown("上传您的 WizTree CSV 文件，让我来帮您分析磁盘空间使用情况！")

    #拿到文件路径
    uploaded_file_path = st.file_uploader("选择 WizTree CSV 文件 ", type=["csv"],key="upload_csv_file")
                            #load_csv_file()可以处理中文文件名但是没有前端显示，交互只能用一次，所以弃用了
    if uploaded_file_path:
        
        st.success(f"文件 '{uploaded_file_path.name}' 上传成功！")
        
        # 尝试多种编码读取CSV数据，以提高兼容性
        encodings_to_try = ['utf-8', 'gbk', 'latin1']
        df = None
        for encoding in encodings_to_try:
            try:
                # WizTree的CSV通常从第二行开始是数据，第一行是元信息，但to_read_csv()会自动处理无论标题行在第一还是第二行
                df = to_read_csv(uploaded_file_path,sep=',', encoding=encoding)
                st.write(f"使用 {encoding} 编码成功读取文件。")
                break 
            except Exception as e:
                st.write(f"尝试使用 {encoding} 编码读取失败: {e}")
                continue
        
        if df is None:
            st.error("无法读取CSV文件。请确保文件格式正确，或尝试其他编码。")
            return

        # 数据预处理和列名标准化，中文有读取不了的偶现情况 
        df.columns = [col.strip() for col in df.columns]
        rename_map = {
            '文件名称': 'File Name',
            '分配': 'Size', #采用'分配'列作为大小，因为磁盘里分配的大小是文件在磁盘中实际占用大小。windows可以压缩，使文件实际占用大小小于"大小"列显示的大小，所以不采用"大小"列
            '路径': 'Path',
        }
        df.rename(columns=rename_map, inplace=True)
        print(df.columns)
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
        df['Size'] = df['Size'].astype(float) # 确保是浮点数以便后续计算大小

        st.markdown("---数据预览---")
        st.dataframe(df.head())

        
        st.markdown("--- 详细分析结果 ---")
        with st.spinner('正在分析数据，请稍候...'):
            analysis_results = cache_analyze_data(df) #转成cache_analyze_data()缓存 

        if analysis_results:
            if analysis_results.error_messages:
                for error_msg in analysis_results.error_messages:
                    st.error(f"分析错误: {error_msg}")
            
            st.subheader("基本统计")
            st.metric(label="扫描项目总数", value=f"{analysis_results.total_items_count:,}")
            st.metric(label="总占用空间", value=format_size_dynamically(analysis_results.total_scan_size_bytes))

            st.subheader("占用空间最大的 Top 100 条目")
            if analysis_results.largest_items and len(analysis_results.largest_items) > 1:
                # largest_items[0] 是标题字符串，之后是 (路径, 大小) 元组
                largest_items_df_data = []
                for item in analysis_results.largest_items[1:]:
                    if isinstance(item, tuple) and len(item) == 3:
                        largest_items_df_data.append({'Path': item[0], 'Size_bytes': item[1], '文件夹内文件数量': item[2]})
                
                if largest_items_df_data:
                    largest_items_df = pd.DataFrame(largest_items_df_data)
                    largest_items_df['Size'] = largest_items_df['Size_bytes'].apply(format_size_dynamically)
                    #@discard   废啦这玩意不如直接dataframe(height=500)
                    # # 交互式Top N选择 
                    # max_n = len(largest_items_df)   # 最大条目数由deal_csv.py中的get_largest_items()决定
                    # top_n = st.slider("选择 Top N 条目", min_value=1, max_value=max_n, value=min(10, max_n), key="top_n_items")
                    # # 限定高度的滚动表格
                    # st.dataframe(largest_items_df[['Path', 'Size']].head(top_n), height=300)
                    # 可展开查看全部
                    #with st.expander("查看全部条目"):
                    #直接展示
                    st.dataframe(largest_items_df[['Path', 'Size']], height=400)
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
                        category_df_data.append({'类别': category, '统计': stats_str})
                    if category_df_data:
                        category_df = pd.DataFrame(category_df_data)
                        st.table(category_df)
                    
                    # 尝试为类别统计创建饼图 (需要从字符串中提取数值)
                    try:
                        pie_chart_data = {}
                        for category, stats_str in analysis_results.category_stats[stats_data_key].items():
                            # 尝试从 '1.23 GB (10 个条目, 12.34%)' 提取大小 (GB) 和百分比
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

            st.subheader("按文件扩展名统计")
            if analysis_results.extension_stats:
                stats_data_key = next((key for key in analysis_results.extension_stats if isinstance(analysis_results.extension_stats[key], dict)), None)
                if stats_data_key and isinstance(analysis_results.extension_stats[stats_data_key], dict):
                    st.write(f"**{stats_data_key}**")
                    ext_df_data = []
                    raw_ext_sizes = {}
                    for ext, size_bytes in analysis_results.extension_stats[stats_data_key].items():
                        ext_df_data.append({'扩展名': f"{ext}", '大小': format_size_dynamically(size_bytes)})
                        raw_ext_sizes[f".{ext}"] = size_bytes
                    if ext_df_data:
                        ext_df = pd.DataFrame(ext_df_data)
                        # 交互式Top N扩展名选择
                        max_ext = len(ext_df)
                        top_ext = st.slider("", min_value=0, max_value=max_ext, value=min(20, max_ext), key="top_n_ext")
                        st.markdown(f"选择 Top {top_ext} 扩展名"+"\n注意：请不要在 AI 分析特定文件夹时拖动该滑块，否则会使AI分析失败")
                        # 限定高度的滚动表格
                        st.dataframe(ext_df[['扩展名', '大小']].head(top_ext), height=300)
                        # 可展开查看全部扩展名
                        # with st.expander("查看全部扩展名"):
                        #     st.dataframe(ext_df[['扩展名', '大小']], height=500)
                    
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

        # AI 分析集成 
        st.markdown("--- AI 分析与建议 ---")
        analyzer = AISuggest() # AIAnalyzer 会尝试从环境变量或config读取API密钥
        
        # 以下是AI分析的摘要模式，v0.1之后弃用了
        # 准备摘要给AI
        #summary_for_ai = f"总扫描项目数: {analysis_results.total_items_count}, 总占用空间: {format_size_dynamically(analysis_results.total_scan_size_bytes)}."
        #summary_for_ai = analysis_results.to_summary_dict()
        #summary_for_ai = analyze_data_tree_for_json(df)
        # from pympler import asizeof
        # st.info(f"tree_dict占用的内存:{format_size_dynamically(asizeof.asizeof(summary_for_ai))}")
        # st.markdown(summary_for_ai)
        # print(f"summary_for_ai:{summary_for_ai}")
        
        
        # with st.spinner('AI 正在分析磁盘使用摘要...'):
        #     ai_summary_analysis = cached_aisuggest_disk_usage_summary(summary_for_ai)
        # st.subheader("AI 磁盘使用摘要分析")
        # st.markdown(ai_summary_analysis)

        # with st.spinner('AI 正在生成文件清理建议...'):
        #     # 传递整个DataFrame或其摘要给AI
        #     # summary_for_ai = analysis_results.to_summary_dict()
        #     # 
        #     ai_cleanup_suggestion = cached_aisuggest_files_for_cleanup(summary_for_ai) # 
        # st.subheader("AI 文件清理建议")
        # st.markdown(ai_cleanup_suggestion)

        # AI分析特定文件夹 
        st.markdown("--- AI 分析特定文件夹内容 ---")
        # 允许用户输入文件夹路径和问题
        with st.form("analyze_folder_form"):
            folder_path_query = st.text_input("输入您想分析的文件夹路径 (基于CSV中的路径):", key="folder_path_q")
            user_query_folder = st.text_area("您对这个文件夹有什么具体问题吗？", key="user_query_f")
            submitted = st.form_submit_button("分析指定文件夹")
            if submitted and folder_path_query:
                # 路径可能是 'C:\Folder\Subfolder'，也可能是 'C:\Folder\Subfolder\file.txt'
                folder_files_df = df.loc[df['Path'].str.startswith(folder_path_query, na=False)]# 条件列表筛选；Pands衍生定制的Series.str.startswith(pat,na=None)选择df中路径以folder_path_query开头的行，这可以获取到文件夹内所有文件，包括文件夹自身；这里不na=False在遇到NaN的'Path'列时会直接返回NaN会使df.loc()报错
                from pympler import asizeof
                import json
                st.markdown(f"""
                ℹ️ **信息**:
                - folder_files_df占用的内存: {format_size_dynamically(asizeof.asizeof(folder_files_df))}
                - 若不使用文件树处理:
                - 1. 该df直接转json内存为: {format_size_dynamically(asizeof.asizeof(folder_files_df.to_json()))}
                - 转json后'utf-8'序列化传给aiapi的字节数: {format_size_dynamically(len((folder_files_df.to_json()).encode('utf-8')))}
                - 
                - 2. 若该df直接转dict内存为: {format_size_dynamically(asizeof.asizeof(folder_files_df.to_dict()))}
                - 转dict后转json内存为: {format_size_dynamically(asizeof.asizeof(json.dumps(folder_files_df.to_dict())))}
                - 该json用'utf-8'序列化后传给aiapi的字节数: {format_size_dynamically(len((json.dumps(folder_files_df.to_dict())).encode('utf-8')))}
                """)

                if not folder_files_df.empty:
                    # --- AI调用及实时耗时显示 ---
                    ai_call_params = {  # 之后调用aisuggest_folder_contents()的参数字典
                        "folder_path": folder_path_query,
                        "file_details_df": folder_files_df,
                        "user_query": user_query_folder if user_query_folder else None
                    }
                    ai_folder_analysis = None
                    placeholder = st.empty() # 先占个位，用于实时更新耗时

                    def perform_ai_call_with_timing(is_summary_mode=False):
                        nonlocal ai_folder_analysis # 非局部变量，用于存储AI分析结果
                        current_mode_params = ai_call_params.copy()
                        current_mode_params["files_too_big"] = is_summary_mode # 是否是摘要模式
                        
                        start_time = time.time()
                        # 运行AI分析的内部函数，用于线程执行
                        result_container = {"result": None, "error": None} # 用于存储AI分析结果和错误
                        def analysis_in_thread(): # 线程执行的函数
                            try:
                                result_container["result"] = analyzer.aisuggest_folder_contents(**current_mode_params)  #**current_mode_params 解包字典作为参数传入
                            except Exception as e: 
                                result_container["error"] = e

                        thread = threading.Thread(target=analysis_in_thread)
                        thread.start()

                        while thread.is_alive():
                            elapsed = time.time() - start_time
                            placeholder.info(f"AI {'摘要' if is_summary_mode else '完整'}分析中... 花费时间: {elapsed:.1f} 秒 / 据测试，api平均等待时长为60s，请耐心等待")
                            time.sleep(0.2)
                        thread.join() # 等待线程结束

                        elapsed = time.time() - start_time
                        placeholder.info(f"AI {'摘要' if is_summary_mode else '完整'}分析完成! 花费时间: {elapsed:.1f} 秒")

                        if result_container["error"]:
                            # 如果是 FolderTooLargeError，则触发摘要模式（如果当前不是摘要模式）
                            # 否则，直接抛出其他错误
                            if isinstance(result_container["error"], FolderTooLargeError) and not is_summary_mode:# 如果已经是摘要模式那就是未预料到的错误，抛出
                                st.warning(str(result_container["error"]))
                                return perform_ai_call_with_timing(is_summary_mode=True) # 递归调用摘要模式
                            else:
                                st.error(f"AI分析时发生意外错误: {result_container['error']}")
                                return None 
                        else:
                            ai_folder_analysis = result_container["result"]
                            return ai_folder_analysis

                    # 首次尝试完整分析
                    ai_folder_analysis = perform_ai_call_with_timing(is_summary_mode=False)

                    # --- AI调用及实时耗时显示结束 ---
 
                    # 存起来统一在外面展示
                    st.session_state.ai_folder_analysis_result = ai_folder_analysis 
                    st.session_state.analyzed_folder_path = folder_path_query # 记录当前分析的路径
                else:
                    st.warning(f"在上传的CSV中没有找到路径以 '{folder_path_query}' 开头的文件/子文件夹。请确保路径正确。")
                    if 'ai_folder_analysis_result' in st.session_state:
                        del st.session_state.ai_folder_analysis_result # 如果之前有结果但这次没找到文件，清除旧结果
                    if 'analyzed_folder_path' in st.session_state:
                        del st.session_state.analyzed_folder_path

        if 'ai_folder_analysis_result' in st.session_state and st.session_state.ai_folder_analysis_result is not None:
            st.subheader(f"AI 对文件夹 '{st.session_state.get('analyzed_folder_path', '')}' 的分析结果")
            st.markdown(st.session_state.ai_folder_analysis_result)
    else:
        st.info(
        "注意:文件名不得含有中文，否则会报400解析错误"
    )

    st.sidebar.header("关于")
    st.sidebar.info(
        "这是一个使用 Streamlit 构建的 AI 磁盘空间分析助手。\n"
        "它可以帮助您理解 [WizTree](https://www.diskanalyzer.com) 导出的 CSV 文件中的磁盘使用情况，并提供 AI 驱动的分析和建议。\n"
    )
    
    st.sidebar.success(
        "此项目是开源的，您可以在 [GitHub](https://github.com/todimstar/csv_chat) 上找到它。\n"
        "如果您有任何问题或建议，请在 [GitHub](https://github.com/todimstar/csv_chat) 上提交问题或拉取请求。\n"
    )

if __name__ == "__main__":
    main()