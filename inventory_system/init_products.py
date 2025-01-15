import pandas as pd
from app import app, db
from models import Product, Category

def load_products_from_excel(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    with app.app_context():
        # 先清空现有商品
        Product.query.delete()
        
        # 获取所有分类的映射（同时用编码和名称作为键）
        categories = Category.query.all()
        category_map = {}
        for cat in categories:
            category_map[cat.code] = cat.id  # 用编码映射
            category_map[cat.name] = cat.id  # 用名称映射
        
        # 创建所有商品
        for _, row in df.iterrows():
            # 处理可能的空值
            base_price = row['基准批发价'] if pd.notna(row['基准批发价']) else None
            if isinstance(base_price, str):
                base_price = float(base_price.replace(',', ''))
            
            # 尝试通过分类名称或编码找到对应的分类ID
            category_value = str(row['商品分类'])
            category_id = category_map.get(category_value)
            
            product = Product(
                product_code=str(row['商品编码']),
                product_name=row['商品名称'],
                category_id=category_id,  # 使用找到的分类ID
                specifications=row['规格型号'] if pd.notna(row['规格型号']) else None,
                unit=row['计量单位'] if pd.notna(row['计量单位']) else None,
                base_price=base_price,
                reference_cost=row['参考成本'] if pd.notna(row['参考成本']) else None,
                default_supplier=row['默认供应商'] if pd.notna(row['默认供应商']) else None,
                default_warehouse=row['默认仓库'] if pd.notna(row['默认仓库']) else None
            )
            db.session.add(product)
            
            if not category_id:
                print(f"警告: 商品 {product.product_code} 找不到对应的分类: {category_value}")
        
        db.session.commit()

if __name__ == '__main__':
    excel_path = '../data/product.xlsx'
    load_products_from_excel(excel_path) 