from app import app, db, ProductCategory, Product
import pandas as pd

def import_initial_data():
    with app.app_context():
        try:
            # 清空现有数据
            ProductCategory.query.delete()
            Product.query.delete()
            
            # 导入分类数据
            categories_df = pd.read_excel('data/product_cate.xlsx')
            
            # 按层级顺序导入分类
            for _, row in categories_df.iterrows():
                category = ProductCategory(
                    id=str(row['分类编码']),
                    name=str(row['分类名称']),
                    parent_id=str(row['上级分类']) if pd.notna(row['上级分类']) else None,
                    level=int(row['层级']) if '层级' in categories_df.columns else 1
                )
                db.session.add(category)
            
            # 导入商品数据
            products_df = pd.read_excel('data/products.xlsx')  # 假设你的商品数据文件名
            
            for _, row in products_df.iterrows():
                product = Product(
                    code=str(row['商品编码']),
                    name=str(row['商品名称']),
                    category_id=str(row['分类编码']),
                    model=str(row.get('规格型号', '')),
                    wholesale_price=float(row.get('基准批发价', 0)),
                    unit=str(row.get('计量单位', '')),
                    status=str(row.get('状态', '正常'))
                )
                db.session.add(product)
            
            db.session.commit()
            print("数据导入成功！")
            
        except Exception as e:
            db.session.rollback()
            print(f"导入失败: {str(e)}")

if __name__ == "__main__":
    import_initial_data() 