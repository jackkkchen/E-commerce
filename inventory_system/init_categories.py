import pandas as pd
from app import app, db
from models import Category

def load_categories_from_excel(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path, usecols=['分类编码', '分类名称', '上级分类'])
    
    with app.app_context():
        # 先清空现有分类
        Category.query.delete()
        
        # 创建编码到ID的映射
        code_to_id = {}
        name_to_id = {}  # 添加名称到ID的映射
        
        # 第一遍循环创建所有分类
        for _, row in df.iterrows():
            code = str(row['分类编码'])
            name = row['分类名称']
            category = Category(
                code=code,
                name=name
            )
            db.session.add(category)
            db.session.flush()  # 获取ID
            code_to_id[code] = category.id
            name_to_id[name] = category.id  # 保存名称到ID的映射
        
        # 第二遍循环设置父子关系
        for _, row in df.iterrows():
            code = str(row['分类编码'])
            parent_name = row['上级分类']
            
            if pd.notna(parent_name) and parent_name in name_to_id:
                category = Category.query.filter_by(code=code).first()
                if category:
                    category.parent_id = name_to_id[parent_name]
        
        db.session.commit()

if __name__ == '__main__':
    excel_path = '../data/product_cate.xlsx'
    load_categories_from_excel(excel_path) 