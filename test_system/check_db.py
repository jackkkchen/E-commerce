from app import app, db, ProductCategory, Product

def check_db_structure():
    with app.app_context():
        # 检查表结构
        inspector = db.inspect(db.engine)
        
        print("\n=== 产品表结构 ===")
        columns = inspector.get_columns('product')
        for column in columns:
            print(f"- {column['name']}: {column['type']}")
            
        print("\n=== 分类表结构 ===")
        columns = inspector.get_columns('product_category')
        for column in columns:
            print(f"- {column['name']}: {column['type']}")

def check_raw_sql():
    with app.app_context():
        # 直接查看表创建SQL
        result = db.session.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name IN ('product', 'product_category')
        """)
        for row in result:
            print("\nTable Creation SQL:")
            print(row[0])

if __name__ == "__main__":
    check_db_structure()
    check_raw_sql() 