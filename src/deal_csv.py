# src/deal_csv.py
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

def path_to_file_name(path):
    """将路径转换为文件名"""
    idx1 = path.rfind('\\')#windows
    idex2 = path.rfind('/')#mac、Linux等
    idx = max(idx1, idex2)
    if idx == -1:
        if path.rfind(':') == -1:
            return path
        else:
            return path[path.rfind(':')+1:]
    return path[idx+1:]

def load_csv_file():
    """打开一个文件对话框，让用户选择一个CSV文件并使用pandas加载它。"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        file_path = filedialog.askopenfilename(
            title="请选择 WizTree 导出的 CSV 文件",
            filetypes=(("CSV 文件", "*.csv"), ("所有文件", "*.*"))
        )
        if not file_path:
            print("没有选择文件。")
            return None
        return file_path
    except Exception as e:
        print(f"加载文件失败: {e}")
        return None

def format_size_dynamically(size_bytes):
    """将字节大小格式化为KB, MB, GB, TB等易读单位。"""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

def to_read_csv(file_input, sep=',', encoding='utf-8'):
    """
    智能读取CSV文件，自动判断表头位置，并兼容本地文件路径和Streamlit UploadedFile对象。
    """
    try:
        first_line_str = ""
        # 预读取第一行，用于判断表头
        if hasattr(file_input, 'seek') and hasattr(file_input, 'readline'):
            # 如果是 UploadedFile 或已打开的文件对象
            file_input.seek(0)  # 确保从文件开头读取
            # UploadedFile.readline() 返回 bytes, 需要解码
            first_line_bytes = file_input.readline()
            try:
                first_line_str = first_line_bytes.decode(encoding).strip()
            except AttributeError: # 如果readline()直接返回了str (不太可能，但做兼容)
                 first_line_str = first_line_bytes.strip()
            file_input.seek(0)  # 再次重置指针，以便pandas完整读取
        elif isinstance(file_input, str):
            # 如果是文件路径字符串
            with open(file_input, 'r', encoding=encoding) as f:
                first_line_str = f.readline().strip()
        else:
            # 其他无法处理的类型
            print(f"错误：无法识别的输入类型 {type(file_input)}，无法预读取第一行。")
            # 尝试直接让pandas处理，可能会失败或行为不符合预期
            if hasattr(file_input, 'read'): # 如果是 UploadedFile
                 return pd.read_csv(file_input, sep=sep, encoding=encoding) # pandas 内部会处理 UploadedFile
            else: # 如果是其他不支持的类型
                 raise ValueError("输入必须是文件路径或支持 seek/readline 的文件对象")


        # 智能判断表头是否在第二行
        title_is_second = False
        if first_line_str: # 确保第一行内容不是空的
            title_is_second = any([
                first_line_str.count(sep) < 3,
                any(note_keyword in first_line_str for note_keyword in ["生成由", "通过捐赠", "隐藏此信息)"]),
                not any(head_keyword in first_line_str for head_keyword in ["文件名称", "大小", "分配", "修改时间", "属性", "文件", "文件夹", "Name", "Size", "Modified"]) # 增加了英文关键词
            ])

        # 根据判断读取CSV
        header_row = 1 if title_is_second else 0

        # 让 pandas 处理 UploadedFile 或文件路径
        # pd.read_csv 本身就能很好地处理 UploadedFile 对象和文件路径
        df = pd.read_csv(file_input, sep=sep, header=header_row, encoding=encoding)
        return df

    except Exception as e:
        print(f"处理 '{file_input}' 文件遇到意外错误: {e}")
        return None
#-------------------------------------------

#-------------------------------------------
class AnalysisResult:
    """用于存储分析结果的数据结构"""
    def __init__(self):
        self.total_scan_size_bytes = 0  # 总扫描大小(字节)
        self.total_items_count = 0  # 总文件/文件夹数量
        self.largest_items = []  # 存储最大的文件/文件夹列表，每项为(路径, 大小)元组
        self.category_stats = {}  # 按类别统计，格式: {类别: (总大小, 文件数, 百分比)}
        self.extension_stats = {}  # 按扩展名统计，格式: {扩展名: 总大小}
        self.error_messages = []  # 存储分析过程中的错误/警告信息
        #self.raw_data = None  # 存储原始DataFrame以供进一步分析    原始数据太大不能传给ai

    def add_error(self, message):
        """添加错误信息"""
        self.error_messages.append(message)

    def to_summary_dict(self):
        """将分析结果转换为字典格式，方便AI模块处理"""
        return {
            "total_size": self.total_scan_size_bytes,
            "total_items": self.total_items_count,
            "largest_items": self.largest_items,
            "category_statistics": self.category_stats,
            "extension_statistics": self.extension_stats,
            "errors": self.error_messages
        }
def analyze_data(df):
    """对DataFrame执行更详细的分析，包括识别大文件、按类型汇总等。"""
    if df is None:
        print("没有数据可供分析。")
        return None

    # 创建分析结果对象
    result = AnalysisResult()
    #result.raw_data = df.copy()  # 保存原始数据 #原始数据太大不能传给ai

    print("\n开始数据分析...")

    # 标准化列名和数据预处理
    df = standardize_columns(df)
    if df is None:
        result.add_error("列标准化失败")
        return result

    # 计算总扫描大小
    total_scan_size = calculate_total_size(df)
    result.total_scan_size_bytes = total_scan_size
    result.total_items_count = len(df)

    print(f"扫描文件总大小: {format_size_dynamically(total_scan_size)} ({total_scan_size:,} 字节)")
    print(f"总文件/文件夹数量: {len(df)}")

    # 获取最大条目
    largest_items = get_largest_items(df)
    result.largest_items = largest_items

    # 按类别统计
    category_stats = calculate_category_stats(df)
    result.category_stats = category_stats

    # 按扩展名统计
    extension_stats = calculate_extension_stats(df)
    result.extension_stats = extension_stats

    print("\n数据分析完成。")
    return result

def standardize_columns(df):
    """标准化DataFrame的列名"""
    # 标准化 "文件名称" 列
    if '文件名称' in df.columns:
        df.rename(columns={'文件名称': 'File Name'}, inplace=True)
    elif 'File Name' not in df.columns:
        potential_file_name_cols = [col for col in df.columns if '文件' in col and ('名' in col or '名称' in col)]
        if potential_file_name_cols:
            print(f"警告：未找到标准的 'File Name' 或 '文件名称' 列，尝试使用推测的列名 '{potential_file_name_cols[0]}'")
            df.rename(columns={potential_file_name_cols[0]: 'File Name'}, inplace=True)

    # 确保 Path 列存在
    if 'File Name' in df.columns and 'Path' not in df.columns:
        print("信息：CSV文件中缺少 'Path' 列，将使用 'File Name' 列作为路径。")
        df['Path'] = df['File Name']
    elif 'Path' not in df.columns:
        print("警告：CSV文件中缺少 'Path' 列，并且无法从 'File Name' 创建。某些路径相关的分析可能不准确。")

    # 标准化分配列
    if '分配' in df.columns:
        df.rename(columns={'分配': 'Size'}, inplace=True)
    
    if 'Size' in df.columns:
        df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
        df.dropna(subset=['Size'], inplace=True)
    else:
        print("CSV文件中缺少 'Size' 或 '分配' 列，无法进行大小分析。")
        return None

    return df

def calculate_total_size(df):
    """计算总扫描大小"""
    total_scan_size_bytes = 0
    if not df.empty and 'Size' in df.columns:
        if 'Path' in df.columns and pd.api.types.is_string_dtype(df['Path']):
            df['PathDepth'] = df['Path'].astype(str).apply(lambda x: x.count('\\') + x.count('/'))  #计算路径深度
            if not df.empty and 'PathDepth' in df.columns and not df['PathDepth'].empty:
                root_row_idx = df['PathDepth'].idxmin()
                if pd.notna(root_row_idx) and root_row_idx in df.index:
                    root_row = df.loc[root_row_idx]
                    total_scan_size_bytes = root_row['Size']
                    print(f"使用根目录 '{root_row.get('File Name', root_row.get('Path', 'N/A'))}' 的大小作为总扫描大小。")  # get(key, default)通用获取字典值结构
                else:
                    print("警告：无法通过PathDepth确定根条目，尝试使用第一个条目的大小。")
                    total_scan_size_bytes = df.iloc[0]['Size'] if not df.empty else 0
            else:
                print("警告：PathDepth 计算结果为空或导致DataFrame为空，尝试使用第一个条目的大小。")
                total_scan_size_bytes = df.iloc[0]['Size'] if not df.empty else 0
            if 'PathDepth' in df.columns: 
                df.drop(columns=['PathDepth'], inplace=True)
        elif not df.empty:
            total_scan_size_bytes = df.iloc[0]['Size']
            print(f"警告：CSV文件中缺少 'Path' 列或 'Path' 列非字符串类型，无法精确确定根目录。尝试使用第一个条目 '{df.iloc[0].get('File Name', 'N/A')}' 的大小作为总扫描大小。这可能不准确。")
    return total_scan_size_bytes

def get_largest_items(df, top_n=100):
    """获取最大的文件/文件夹,回传list包含FileName、Size和文件夹内文件数量"""
    largest_items = []  #回传的是列表所以st那边不会显示二级标题，只有下面的返回dict的才会显示
    if 'File Name' in df.columns or 'Path' in df.columns:
        largest = df.sort_values(by='Size', ascending=False).head(top_n)
        largest_items.append(f"\n占用空间最大的 {top_n} 个条目 (文件或文件夹):\n")
        for index, row in largest.iterrows():
            item_display_name = row.get('Path', row.get('File Name', 'N/A'))
            item_size = row['Size']
            item_size_formatted = format_size_dynamically(item_size)
            item_files_count = row['文件夹']
            print(f"  - {item_display_name} ({item_size_formatted})")
            largest_items.append((item_display_name, item_size, item_files_count))
    else:
        largest_items.append("CSV文件中缺少 'File Name' 和 'Path' 列，无法准确列出最大的条目。")
    return largest_items

def calculate_category_stats(df):
    """计算各类别的统计信息"""
    category_stats = {}
    if 'File Name' not in df.columns:
        category_stats["calculate_category_stats().error"] = "CSV文件中缺少 'File Name' 列，无法按类别统计。"
        return category_stats

    files_df = get_files_df(df) #
    if files_df is None or files_df.empty:
        category_stats["calculate_category_stats().error"] = "未能识别出任何文件条目进行分类统计。"
        return category_stats

    total_size = files_df['Size'].sum()
    files_df = add_category_column(files_df) # 确保有 'Category' 列

    
    category_summary = files_df.groupby('Category').agg({
        'Size': 'sum',  # 计算每个分类的总大小
        'File Name': 'count'  # 计算每个分类的文件数量
    }).sort_values('Size', ascending=False)  # 按大小降序排列

    # print("\n按文件类型分类统计总大小 (基于识别出的文件):")
    category_stats["按文件类型分类统计总大小 (基于识别出的文件):"] = {}
    for category, row in category_summary.iterrows():
        size_bytes = row['Size']
        count = row['File Name']
        percentage = (size_bytes / total_size * 100) if total_size > 0 else 0
        # print(f"  - {category}: {format_size_dynamically(size_bytes)} ({count} 个条目, {percentage:.2f}%)")
        category_stats["按文件类型分类统计总大小 (基于识别出的文件):"][category] = f"{format_size_dynamically(size_bytes)} ({count} 个条目, {percentage:.2f}%)"

    return category_stats

def calculate_extension_stats(df,top_n=100):
    """计算各扩展名的统计信息"""
    extension_stats = {}
    if 'File Name' not in df.columns:
        extension_stats["calculate_category_stats().error"] = "CSV文件中缺少 'File Name' 列，无法按扩展名统计。"
        return extension_stats

    files_df = get_files_df(df)
    if files_df is None or files_df.empty:
        extension_stats["calculate_category_stats().error"] = "未能识别出任何文件条目进行扩展名统计。"
        return extension_stats
    
    #新增拓展名列
    files_df['Extension'] = files_df['File Name'].astype(str).apply(
        lambda x:os.path.splitext(x)[1].lower() if os.path.splitext(x)[1] != '' else '无扩展名'
    )   #直接用系统函数提取拓展名，如果文件名中没有'\'和'/'，则将.后内容作为拓展名，否则为无拓展名
    #对于lower化后的文件名，如果含有.且没有'\'和'/'且.前还有文件名内容且.后不是空拓展名，则将.后内容作为拓展名，否则为无拓展名

    extension_summary = files_df.groupby('Extension')['Size'].sum().sort_values(ascending=False)

    # print("\n按具体扩展名统计文件总大小 (Top 20, 基于识别出的文件):")
    extension_str = f"按具体扩展名统计文件总大小 (Top {top_n}, 基于识别出的文件):"
    extension_stats[extension_str] = {}
    for ext, size_bytes in extension_summary.head(top_n).items():
        # print(f"  - .{ext}: {format_size_dynamically(size_bytes)}")
        extension_stats[extension_str][ext] = size_bytes

    return extension_stats

def get_files_df(df):
    """获取文件DataFrame"""
    files_df = None
    if 'Folders' in df.columns:
        files_df = df[df['Folders'] == 0].copy()
    elif '文件夹' in df.columns:
        files_df = df[df['文件夹'] == 0].copy()
    
    return files_df

def add_category_column(df):
    """添加文件类别列"""
    extension_categories = {
        '图片': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'raw'],
        '视频': ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'],
        '音频': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'wma', 'm4a'],
        '文档': ['doc', 'docx', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'md'],
        '压缩包': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2'],
        '应用程序': ['exe', 'msi', 'dmg', 'app', 'bat', 'sh'],
        '系统/缓存': ['dll', 'sys', 'tmp', 'log', 'bak', 'iso', 'vmdk', 'vhd'],
    }

    df['Extension'] = df['File Name'].astype(str).apply(
        lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名'
    )

    def categorize_extension(ext):
        for category, extensions in extension_categories.items():
            if ext in extensions:
                return category
        return '其他' if ext != '无扩展名' else '无扩展名文件'

    df['Category'] = df['Extension'].apply(categorize_extension)
    return df


def query_files_by_type_or_extension(df, query_type, query_value):
    """根据指定类型（'category' 或 'extension'）和值查询文件列表。"""
    if df is None or df.empty:
        print("没有数据可供查询。")
        return pd.DataFrame()

    if 'File Name' not in df.columns:
        print("CSV文件中缺少 'File Name' 列，无法执行查询。")
        return pd.DataFrame()

    # 确保用于分类的列存在
    if 'Category' not in df.columns or 'Extension' not in df.columns:
        # 尝试重新生成分类和扩展名列，如果它们在分析中未生成或丢失
        # 这部分逻辑与 analyze_data 中的文件识别和分类逻辑类似
        files_df_query = None
        if 'Folders' in df.columns and isinstance(df['Folders'], pd.Series):
            files_df_query = df[df['Folders'] == 0].copy()
        elif '文件夹' in df.columns and isinstance(df['文件夹'], pd.Series):
            files_df_query = df[df['文件夹'] == 0].copy()
        
        if files_df_query is None or files_df_query.empty:
            df['Extension_temp_for_query'] = df['File Name'].astype(str).apply(lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名')
            files_df_query = df[df['Extension_temp_for_query'] != '无扩展名'].copy()
            if 'Extension_temp_for_query' in df.columns: df.drop(columns=['Extension_temp_for_query'], inplace=True)
            if 'Extension_temp_for_query' in files_df_query.columns: files_df_query.drop(columns=['Extension_temp_for_query'], inplace=True)

        if not files_df_query.empty:
            if 'Extension' not in files_df_query.columns:
                 files_df_query['Extension'] = files_df_query['File Name'].astype(str).apply(lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名')
            
            extension_categories = {
                '图片': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'raw'],
                '视频': ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'],
                '音频': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'wma', 'm4a'],
                '文档': ['doc', 'docx', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'md'],
                '压缩包': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2'],
                '应用程序': ['exe', 'msi', 'dmg', 'app', 'bat', 'sh'],
                '系统/缓存': ['dll', 'sys', 'tmp', 'log', 'bak', 'iso', 'vmdk', 'vhd'],
            }
            def categorize_extension_query(ext):
                for category, extensions_in_category in extension_categories.items():
                    if ext in extensions_in_category:
                        return category
                if ext == '无扩展名': 
                    return '无扩展名文件' 
                return '其他'
            if 'Category' not in files_df_query.columns:
                files_df_query['Category'] = files_df_query['Extension'].apply(categorize_extension_query)
            # 将新生成的列合并回原始df，或决定仅在files_df_query上操作
            # 为了简单起见，这里我们假设 analyze_data 已经填充了这些列
            # 如果没有，下面的查询可能在原始 df 上失败，除非我们合并或使用 files_df_query
            # 对于此函数，我们将依赖 analyze_data 已经准备好 df
            if 'Category' not in df.columns and 'Category' in files_df_query.columns:
                df = df.merge(files_df_query[['Category', 'Extension']], left_index=True, right_index=True, how='left')

    print(f"\n正在查询类型为 '{query_type}'，值为 '{query_value}' 的文件...")
    results_df = pd.DataFrame()

    if query_type == 'category':
        if 'Category' not in df.columns:
            print("错误：DataFrame中缺少 'Category' 列，无法按类别查询。请确保已运行 analyze_data。")
            return results_df
        results_df = df[df['Category'].astype(str).str.lower() == query_value.lower()]
    elif query_type == 'extension':
        if 'Extension' not in df.columns:
            # 如果 'Extension' 列不存在，尝试从 'File Name' 创建它
            # 仅针对那些看起来是文件的条目（例如，有扩展名）
            temp_extensions = df['File Name'].astype(str).apply(lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else None)
            results_df = df[temp_extensions == query_value.lower().lstrip('.')] 
        else:
            results_df = df[df['Extension'].astype(str).str.lower() == query_value.lower().lstrip('.')] 
    else:
        print(f"不支持的查询类型: {query_type}。请使用 'category' 或 'extension'。")
        return results_df

    if results_df.empty:
        print(f"未找到类型为 '{query_type}'，值为 '{query_value}' 的文件。")
    else:
        print(f"找到 {len(results_df)} 个匹配文件:")
        for index, row in results_df.iterrows():
            item_display_name = row.get('Path', row.get('File Name', 'N/A')) 
            item_size_formatted = format_size_dynamically(row['Size'])
            print(f"  - {item_display_name} ({item_size_formatted})")
    return results_df

# if __name__ == "__main__":

#     print("AI 磁盘空间分析助手")
#     print("====================")
#     csv_data = load_csv_data()
#     if csv_data is not None:
#         #analyze_data(csv_data)
#         # 示例：查询特定类型的文件
#         # query_files_by_type_or_extension(csv_data, 'category', '视频')# 类型
#         # query_files_by_type_or_extension(csv_data, 'extension', 'exe')# 扩展名
#         # query_files_by_type_or_extension(csv_data, 'extension', '.log')

#         # AI 分析集成
#         print("\n开始AI分析...")
#         analyzer = AISuggest()

#         # 1. 分析磁盘使用摘要
#         #    为了简单起见，我们这里可以创建一个简单的文本摘要
#         #    在实际应用中，这部分可以从 analyze_data 函数的输出或更复杂的逻辑生成
#         if csv_data is not None and not csv_data.empty:
#             # 尝试从 analyze_data 中获取一些关键信息用于AI摘要
#             # 这里我们用一个简化的摘要，实际应用中可以更详细
            
#             summary_for_ai = analyze_data(csv_data).to_summary_dict()
#             # 你也可以从 analyze_data 函数中捕获更详细的分类摘要
#             # 例如，提取 category_summary_bytes 的信息
#             print("\n正在转送AI分析...")
#             ai_summary_analysis = analyzer.aisuggest_disk_usage_summary(summary_for_ai)   #总体分析函数
#             print("\n--- AI磁盘使用摘要分析 ---")
#             print(ai_summary_analysis)

#             # 2. 获取文件清理建议
#             ai_cleanup_suggestion = analyzer.aisuggest_files_for_cleanup(summary_for_ai)
#             print("\n--- AI文件清理建议 ---")
#             print(ai_cleanup_suggestion)
#         else:
#             print("没有加载数据或数据为空，跳过AI分析。")
            
#     print("\n程序结束。")