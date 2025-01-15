import os
from app import app, db
from init_categories import load_categories_from_excel
from init_products import load_products_from_excel

def init_database():
    # 1. 删除现有数据库文件
    db_path = 'instance/inventory.db'
    if os.path.exists(db_path):
        print("删除现有数据库...")
        os.remove(db_path)
    
    # 2. 创建新的数据库和表
    with app.app_context():
        print("创建新数据库和表...")
        db.create_all()
    
    # 3. 导入分类数据
    print("导入商品分类数据...")
    categories_file = '../data/product_cate.xlsx'
    load_categories_from_excel(categories_file)
    
    # 4. 导入商品数据
    print("导入商品数据...")
    products_file = '../data/product.xlsx'
    load_products_from_excel(products_file)
    
    print("数据库初始化完成！")

if __name__ == '__main__':
    init_database() 