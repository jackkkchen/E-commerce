import pandas as pd
import os

def read_category_hierarchy():
    # 使用绝对路径
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(current_dir, 'data', 'product_cate_organized.xlsx')
    
    print("Reading file from:", file_path)  # 添加调试信息
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found at {file_path}")
        
    df = pd.read_excel(file_path)
    
    def build_tree(df, parent_id=None):
        nodes = []
        rows = df[df['上级分类序号'] == parent_id] if parent_id is not None else df[df['上级分类序号'].isna()]
        
        for _, row in rows.iterrows():
            node = {
                'id': row['分类序号'],
                'name': row['分类名称'],
                'children': build_tree(df, row['分类序号'])
            }
            nodes.append(node)
        return nodes
    
    return build_tree(df)