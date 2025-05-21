# src/main.py
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from ai_analyzer import AISuggest # 导入AI分析器

def load_csv_data():
    """打开一个文件对话框，让用户选择一个CSV文件并使用pandas加载它。"""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(
        title="请选择 WizTree 导出的 CSV 文件",
        filetypes=(("CSV 文件", "*.csv"), ("所有文件", "*.*"))
    )
    if not file_path:
        print("没有选择文件。")
        return None

    try:
        print(f"正在加载文件: {file_path}")
        # 尝试使用不同的编码读取文件，以增加兼容性
        try:
            # 尝试使用不同的编码读取文件，以增加兼容性，并设置low_memory=False处理DtypeWarning
            # 跳过第一行，因为它是WizTree的生成信息
            df = pd.read_csv(file_path, skiprows=1, low_memory=False)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='gbk', skiprows=1, low_memory=False)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin1', skiprows=1, low_memory=False)
        
        print("文件加载成功！")
        # 清理列名，去除前后空格
        df.columns = df.columns.str.strip()
        print("数据预览 (前5行):\n", df.head())
        return df
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

    # 标准化大小列
    if '大小' in df.columns:
        df.rename(columns={'大小': 'Size'}, inplace=True)
    
    if 'Size' in df.columns:
        df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
        df.dropna(subset=['Size'], inplace=True)
    else:
        print("CSV文件中缺少 'Size' 或 '大小' 列，无法进行大小分析。")
        return None

    return df

def calculate_total_size(df):
    """计算总扫描大小"""
    total_scan_size_bytes = 0
    if not df.empty and 'Size' in df.columns:
        if 'Path' in df.columns and pd.api.types.is_string_dtype(df['Path']):
            df['PathDepth'] = df['Path'].astype(str).apply(lambda x: x.count('\\') + x.count('/'))
            if not df.empty and 'PathDepth' in df.columns and not df['PathDepth'].empty:
                root_entry_idx = df['PathDepth'].idxmin()
                if pd.notna(root_entry_idx) and root_entry_idx in df.index:
                    root_entry = df.loc[root_entry_idx]
                    total_scan_size_bytes = root_entry['Size']
                    print(f"使用根目录 '{root_entry.get('File Name', root_entry.get('Path', 'N/A'))}' 的大小作为总扫描大小。")
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

def get_largest_items(df, top_n=20):
    """获取最大的文件/文件夹"""
    largest_items = []
    if 'File Name' in df.columns or 'Path' in df.columns:
        largest = df.sort_values(by='Size', ascending=False).head(top_n)
        largest_items.append(f"\n占用空间最大的 {top_n} 个条目 (文件或文件夹):\n")
        for index, row in largest.iterrows():
            item_display_name = row.get('Path', row.get('File Name', 'N/A'))
            item_size = row['Size']
            item_size_formatted = format_size_dynamically(item_size)
            print(f"  - {item_display_name} ({item_size_formatted})")
            largest_items.append((item_display_name, item_size))
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
    if files_df.empty:
        category_stats["calculate_category_stats().error"] = "未能识别出任何文件条目进行分类统计。"
        return category_stats

    total_size = files_df['Size'].sum()
    files_df = add_category_column(files_df) # 确保有 'Category' 列

    category_summary = files_df.groupby('Category').agg({
        'Size': 'sum',
        'File Name': 'count'
    }).sort_values('Size', ascending=False)

    # print("\n按文件类型分类统计总大小 (基于识别出的文件):")
    category_stats["按文件类型分类统计总大小 (基于识别出的文件):"] = {}
    for category, row in category_summary.iterrows():
        size_bytes = row['Size']
        count = row['File Name']
        percentage = (size_bytes / total_size * 100) if total_size > 0 else 0
        # print(f"  - {category}: {format_size_dynamically(size_bytes)} ({count} 个条目, {percentage:.2f}%)")
        category_stats["按文件类型分类统计总大小 (基于识别出的文件):"][category] = f"{format_size_dynamically(size_bytes)} ({count} 个条目, {percentage:.2f}%)"

    return category_stats

def calculate_extension_stats(df):
    """计算各扩展名的统计信息"""
    extension_stats = {}
    if 'File Name' not in df.columns:
        extension_stats["calculate_category_stats().error"] = "CSV文件中缺少 'File Name' 列，无法按扩展名统计。"
        return extension_stats

    files_df = get_files_df(df)
    if files_df.empty:
        extension_stats["calculate_category_stats().error"] = "未能识别出任何文件条目进行扩展名统计。"
        return extension_stats

    files_df['Extension'] = files_df['File Name'].astype(str).apply(
        lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名'
    )

    extension_summary = files_df.groupby('Extension')['Size'].sum().sort_values(ascending=False)

    # print("\n按具体扩展名统计文件总大小 (Top 20, 基于识别出的文件):")
    extension_stats["按具体扩展名统计文件总大小 (Top 20, 基于识别出的文件):"] = {}
    for ext, size_bytes in extension_summary.head(20).items():
        # print(f"  - .{ext}: {format_size_dynamically(size_bytes)}")
        extension_stats["按具体扩展名统计文件总大小 (Top 20, 基于识别出的文件):"][ext] = size_bytes

    return extension_stats

def get_files_df(df):
    """获取文件DataFrame"""
    files_df = None
    if 'Folders' in df.columns:
        files_df = df[df['Folders'] == 0].copy()
    elif '文件夹' in df.columns:
        files_df = df[df['文件夹'] == 0].copy()
    
    if files_df is None or files_df.empty:
        df['Extension_temp'] = df['File Name'].astype(str).apply(
            lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名'
        )
        files_df = df[df['Extension_temp'] != '无扩展名'].copy()
        if 'Extension_temp' in df.columns:
            df.drop(columns=['Extension_temp'], inplace=True)
        if 'Extension_temp' in files_df.columns:
            files_df.drop(columns=['Extension_temp'], inplace=True)
    
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


    """对DataFrame执行更详细的分析，包括识别大文件、按类型汇总等。"""
    if df is None:
        print("没有数据可供分析。")
        return

    print("\n开始数据分析...")

    # 标准化 "文件名称" 列
    if '文件名称' in df.columns:
        df.rename(columns={'文件名称': 'File Name'}, inplace=True)
    elif 'File Name' not in df.columns:
        # 如果两者都不存在，尝试查找其他可能的列名，例如包含“文件”和“名”的列
        potential_file_name_cols = [col for col in df.columns if '文件' in col and ('名' in col or '名称' in col)]
        if potential_file_name_cols:
            print(f"警告：未找到标准的 'File Name' 或 '文件名称' 列，尝试使用推测的列名 '{potential_file_name_cols[0]}'")
            df.rename(columns={potential_file_name_cols[0]: 'File Name'}, inplace=True)

    # 确保 Path 列存在，如果不存在则从 File Name 创建
    if 'File Name' in df.columns and 'Path' not in df.columns:
        print("信息：CSV文件中缺少 'Path' 列，将使用 'File Name' 列作为路径。")
        df['Path'] = df['File Name']
    elif 'Path' not in df.columns: # 暗示 File Name 也不存在或未被标准化
        print("警告：CSV文件中缺少 'Path' 列，并且无法从 'File Name' 创建。某些路径相关的分析可能不准确。")

    # 确定文件大小列的名称，兼容 'Size' 和 '大小'
    size_column_name = None
    if 'Size' in df.columns:
        size_column_name = 'Size'
    elif '大小' in df.columns:
        size_column_name = '大小'
    
    if size_column_name:
        df[size_column_name] = pd.to_numeric(df[size_column_name], errors='coerce')
        df.dropna(subset=[size_column_name], inplace=True) # 移除Size无效的行
        # 为了后续分析统一，如果列名是中文，将其重命名为 'Size'
        if size_column_name == '大小':
            df.rename(columns={'大小': 'Size'}, inplace=True)
    else:
        print("CSV文件中缺少 'Size' 或 '大小' 列，无法进行大小分析。")
        return

    # 尝试获取更准确的总大小：WizTree通常在第一行（数据行）提供根目录的总大小
    # 注意：df已经跳过了原始CSV的标题行和WizTree的生成信息行
    total_scan_size_bytes = 0
    if not df.empty and 'Size' in df.columns:
        if 'Path' in df.columns and pd.api.types.is_string_dtype(df['Path']):
            df['PathDepth'] = df['Path'].astype(str).apply(lambda x: x.count('\\') + x.count('/'))
            if not df.empty and 'PathDepth' in df.columns and not df['PathDepth'].empty:
                root_entry_idx = df['PathDepth'].idxmin()
                if pd.notna(root_entry_idx) and root_entry_idx in df.index:
                    root_entry = df.loc[root_entry_idx]
                    total_scan_size_bytes = root_entry['Size']
                    print(f"使用根目录 '{root_entry.get('File Name', root_entry.get('Path', 'N/A'))}' 的大小作为总扫描大小。")
                else:
                    print("警告：无法通过PathDepth确定根条目，尝试使用第一个条目的大小。")
                    total_scan_size_bytes = df.iloc[0]['Size'] if not df.empty else 0
            else: 
                 print("警告：PathDepth 计算结果为空或导致DataFrame为空，尝试使用第一个条目的大小。")
                 total_scan_size_bytes = df.iloc[0]['Size'] if not df.empty else 0
            if 'PathDepth' in df.columns: df.drop(columns=['PathDepth'], inplace=True)
        elif not df.empty: 
            total_scan_size_bytes = df.iloc[0]['Size']
            print(f"警告：CSV文件中缺少 'Path' 列或 'Path' 列非字符串类型，无法精确确定根目录。尝试使用第一个条目 '{df.iloc[0].get('File Name', 'N/A')}' 的大小作为总扫描大小。这可能不准确。")
        else: 
            print("警告：无法确定总扫描大小，数据为空。")
    else: 
        print("无法计算总大小，数据为空或缺少'Size'列。")
        return

    print(f"扫描文件总大小: {format_size_dynamically(total_scan_size_bytes)} ({total_scan_size_bytes:,} 字节)")
    print(f"总文件/文件夹数量: {len(df)}")

    if 'File Name' in df.columns or 'Path' in df.columns:
        top_n = 20
        largest_items = df.sort_values(by='Size', ascending=False).head(top_n)
        print(f"\n占用空间最大的 {top_n} 个条目 (文件或文件夹):")
        for index, row in largest_items.iterrows():
            item_display_name = row.get('Path', row.get('File Name', 'N/A')) 
            item_size_formatted = format_size_dynamically(row['Size'])
            print(f"  - {item_display_name} ({item_size_formatted})")
    else:
        print("CSV文件中缺少 'File Name' 和 'Path' 列，无法准确列出最大的条目。")

    if 'File Name' in df.columns:
        files_df = None
        if 'Folders' in df.columns and isinstance(df['Folders'], pd.Series):
            print("信息：检测到 'Folders' 列，将用于区分文件。文件被假定为 'Folders' == 0 的条目。")
            files_df = df[df['Folders'] == 0].copy()
        elif '文件夹' in df.columns and isinstance(df['文件夹'], pd.Series):
            df.rename(columns={'文件夹': 'Folders'}, inplace=True)
            print("信息：检测到 '文件夹' 列 (已重命名为 'Folders')，将用于区分文件。文件被假定为 'Folders' == 0 的条目。")
            files_df = df[df['Folders'] == 0].copy()
        
        if files_df is None or files_df.empty:
            print("警告：未能通过 'Folders' 列有效区分文件，或筛选结果为空。将尝试基于扩展名区分文件（有扩展名则视为文件）。这可能不完全准确。")
            # Ensure 'File Name' is string type before applying string methods
            df['Extension_temp_for_file_filter'] = df['File Name'].astype(str).apply(lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名')
            files_df = df[df['Extension_temp_for_file_filter'] != '无扩展名'].copy()
            if 'Extension_temp_for_file_filter' in df.columns: df.drop(columns=['Extension_temp_for_file_filter'], inplace=True)
            if 'Extension_temp_for_file_filter' in files_df.columns: files_df.drop(columns=['Extension_temp_for_file_filter'], inplace=True)

        if files_df.empty:
            print("严重警告：未能识别出任何文件条目进行分类统计。文件类型和扩展名统计将为空。")
            effective_df_for_stats = pd.DataFrame() 
            total_for_percentage_calc = 0
        else:
            effective_df_for_stats = files_df.copy() # Use a copy for modifications
            total_for_percentage_calc = effective_df_for_stats['Size'].sum()
            if total_for_percentage_calc == 0:
                print("警告：识别出的文件总大小为0，百分比计算可能无意义或为0。")
        
        if not effective_df_for_stats.empty:
            effective_df_for_stats['Extension'] = effective_df_for_stats['File Name'].astype(str).apply(lambda x: x.split('.')[-1].lower() if '.' in x and len(x.split('.')) > 1 and x.split('.')[-1] != '' else '无扩展名')
            
            extension_categories = {
                '图片': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'raw'],
                '视频': ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'],
                '音频': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'wma', 'm4a'],
                '文档': ['doc', 'docx', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'md'],
                '压缩包': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2'],
                '应用程序': ['exe', 'msi', 'dmg', 'app', 'bat', 'sh'],
                '系统/缓存': ['dll', 'sys', 'tmp', 'log', 'bak', 'iso', 'vmdk', 'vhd'],
            }

            def categorize_extension(ext):
                for category, extensions_in_category in extension_categories.items():
                    if ext in extensions_in_category:
                        return category
                if ext == '无扩展名': 
                    return '无扩展名文件' 
                return '其他'

            effective_df_for_stats['Category'] = effective_df_for_stats['Extension'].apply(categorize_extension)
            category_summary_bytes = effective_df_for_stats.groupby('Category')['Size'].sum().sort_values(ascending=False)

            print("\n按文件类型分类统计总大小 (基于识别出的文件):")
            if total_for_percentage_calc > 0:
                for category, size_bytes_cat in category_summary_bytes.items():
                    count = effective_df_for_stats[effective_df_for_stats['Category'] == category].shape[0]
                    percentage = (size_bytes_cat / total_for_percentage_calc) * 100
                    print(f"  - {category}: {format_size_dynamically(size_bytes_cat)} ({count} 个条目, {percentage:.2f}%)")
            elif not category_summary_bytes.empty: 
                 for category, size_bytes_cat in category_summary_bytes.items():
                    count = effective_df_for_stats[effective_df_for_stats['Category'] == category].shape[0]
                    print(f"  - {category}: {format_size_dynamically(size_bytes_cat)} ({count} 个条目, 0.00%)")
            else: 
                print("  没有可分类的文件或识别出的文件总大小为0。")
            
            extension_summary_bytes = effective_df_for_stats.groupby('Extension')['Size'].sum().sort_values(ascending=False)
            print("\n按具体扩展名统计文件总大小 (Top 20, 基于识别出的文件):")
            for ext, size_bytes_ext in extension_summary_bytes.head(20).items():
                print(f"  - .{ext}: {format_size_dynamically(size_bytes_ext)}")
        else:
            print("\n文件类型和扩展名统计无法进行，因为未能识别出任何有效的文件条目。")

    else: 
        print("CSV文件中缺少 'File Name' 列，无法按扩展名或类型统计。")
    
    print("\n数据分析完成。")

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

if __name__ == "__main__":

    print("AI 磁盘空间分析助手")
    print("====================")
    csv_data = load_csv_data()
    if csv_data is not None:
        #analyze_data(csv_data)
        # 示例：查询特定类型的文件
        # query_files_by_type_or_extension(csv_data, 'category', '视频')# 类型
        # query_files_by_type_or_extension(csv_data, 'extension', 'exe')# 扩展名
        # query_files_by_type_or_extension(csv_data, 'extension', '.log')

        # AI 分析集成
        print("\n开始AI分析...")
        analyzer = AISuggest()

        # 1. 分析磁盘使用摘要
        #    为了简单起见，我们这里可以创建一个简单的文本摘要
        #    在实际应用中，这部分可以从 analyze_data 函数的输出或更复杂的逻辑生成
        if csv_data is not None and not csv_data.empty:
            # 尝试从 analyze_data 中获取一些关键信息用于AI摘要
            # 这里我们用一个简化的摘要，实际应用中可以更详细
            
            summary_for_ai = analyze_data(csv_data).to_summary_dict()
            # 你也可以从 analyze_data 函数中捕获更详细的分类摘要
            # 例如，提取 category_summary_bytes 的信息
            print("\n正在转送AI分析...")
            ai_summary_analysis = analyzer.aisuggest_disk_usage_summary(summary_for_ai)   #总体分析函数
            print("\n--- AI磁盘使用摘要分析 ---")
            print(ai_summary_analysis)

            # 2. 获取文件清理建议
            ai_cleanup_suggestion = analyzer.aisuggest_files_for_cleanup(summary_for_ai)
            print("\n--- AI文件清理建议 ---")
            print(ai_cleanup_suggestion)
        else:
            print("没有加载数据或数据为空，跳过AI分析。")
            
    print("\n程序结束。")