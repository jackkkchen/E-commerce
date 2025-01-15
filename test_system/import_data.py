from app import app, db, ProductCategory, Product
import pandas as pd
import os

def import_initial_data():
    with app.app_context():
        try:
            print("\n=== 开始导入商品数据 ===")
            # 导入商品数据
            try:
                products_df = pd.read_excel('data/product_cate.xlsx')  # 修改为你的文件名
                products_df = products_df.fillna('')
                
                # 清空现有商品
                Product.query.delete()
                db.session.commit()
                
                success_count = 0
                error_records = []
                
                for index, row in products_df.iterrows():
                    try:
                        # 创建商品记录
                        product = Product(
                            code=str(row['商品编码']),
                            name=str(row['商品名称']),
                            category_id=str(row['商品分类']),  # 直接使用商品分类作为category_id
                            unit=str(row['计量单位']) if row['计量单位'] else None,
                            wholesale_price=float(row['基准批发价']) if row['基准批发价'] else None,
                            model=str(row['规格型号']) if row['规格型号'] else None,
                            base_cost=float(row['参考成本']) if row['参考成本'] else None,
                            default_supplier=str(row['默认供应商']) if row['默认供应商'] else None,
                            default_warehouse=str(row['默认仓库']) if row['默认仓库'] else None,
                            status='正常'
                        )
                        db.session.add(product)
                        success_count += 1
                        
                    except Exception as e:
                        error_records.append(f"行 {index + 2}: {str(e)}")
                        print(f"商品导入错误: {str(e)}")
                
                db.session.commit()
                print(f"成功导入 {success_count} 个商品")
                if error_records:
                    print("\n导入错误:")
                    for error in error_records:
                        print(error)
                        
            except Exception as e:
                db.session.rollback()
                print(f"商品导入失败: {str(e)}")
            
        except Exception as e:
            print(f"导入失败: {str(e)}")

def print_products():
    """打印商品信息（用于调试）"""
    with app.app_context():
        products = Product.query.all()
        print(f"\n商品总数: {len(products)}")
        print("\n商品列表:")
        for product in products:
            print(f"- {product.code}: {product.name} (分类: {product.category_id})")

if __name__ == "__main__":
    # 导入数据
    import_initial_data()
    # 打印商品信息进行验证
    print_products() 