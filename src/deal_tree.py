import pandas as pd
import json

class AnalysisResult:
    """用于存储分析结果的数据结构"""
    def __init__(self):
        
        self.error_messages = []  # 存储分析过程中的错误/警告信息
        self.tree_dict = None  # 转义为树结构的字典

    def add_error(self, message):
        """添加错误信息"""
        self.error_messages.append(message)

    def to_json(self):
        """将分析结果转换为json格式，并关闭ascii编码，保留中文方便AI模块处理"""
        return json.dumps(self.tree_dict)#,ensure_ascii=False)

def analyze_data_tree_for_json(df):
    '''前端传入df，返回AnalysisResult'''

    result = AnalysisResult()

    if df is None:
        result.add_error("没有数据可供分析。")
        return result
    

    result.tree_dict = df_to_tree(df)
    # 将树结构转换为json
    json = result.to_json()
    return json

def df_to_tree(df):
    '''将df转换为树结构'''
    # 将df转换为树结构
    tree_dict = {}
    
    # 遍历df的每一行，对File Name进行拆分，分别存入tree_dict的层次中，最后才拿行中信息存入最后一层
    for index, row in df.iterrows():
        file_PathAndName = row['File Name']
        path_parts = file_PathAndName.split('\\')#转义后为\
       
        present_dict = tree_dict
        for part in path_parts:
            if part not in present_dict and part != '':
                present_dict[part] = {}
            if part != '':  # 如果part不为空，则继续向下遍历    但是如果遇到''不是最后一个，会有预想不到的结果
                present_dict = present_dict[part]
            
        if path_parts[-1] == '':
            present_dict['present_files_info'] = f"Size:{row['Size']}B,modifyTime:{row['修改时间']}"
        else:
            present_dict['file_info'] = f"Size:{row['Size']}B,modifyTime:{row['修改时间']}"
    
    return tree_dict

def df_to_briefTree(df):
    '''将df转换为文件夹路径树结构，不包含文件和文件信息'''
    briefTree = {}
    
    # with open('to_briefTree_df.json', 'w',encoding='utf-8') as f:
    #     json.dump(df, f,ensure_ascii=False,indent=4)

    # 遍历df的每一行，对File Name进行拆分，分别存入tree_dict的层次中，最后才拿行中信息存入最后一层
    for index, row in df.iterrows():
        file_PathAndName = row['File Name']
        path_parts = file_PathAndName.split('\\')#转义后为\ 且因为分析的只会是Windows路径，所以不会出现其他路径分隔符
       
        present_dict = briefTree
        for i, part in enumerate(path_parts):
            if i<len(path_parts)-1 and part not in present_dict and part != '': #多加了个判断，无脑加只到倒数第二层
                present_dict[part] = {}
            if i < len(path_parts) - 2:  # 如果part不为空，则继续向下遍历    但是如果遇到''不是最后一个，会有预想不到的结果
                present_dict = present_dict[part]
            elif i == len(path_parts) - 2 and path_parts[-1] == '': #只用遍历到倒数第二层，因为最后一层是文件
                present_dict = present_dict[part]
    return briefTree

if __name__ == '__main__':
    df = pd.read_csv('simpletest.csv',encoding='utf-8')
    briefTree = df_to_briefTree(df)
    with open('briefTree.json', 'w',encoding='utf-8') as f:
        json.dump(briefTree, f,ensure_ascii=False,indent=4)