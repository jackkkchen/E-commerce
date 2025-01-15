from app import app, db
import os

def create_tables():
    with app.app_context():
        # 删除数据库文件
        db_file = 'factory.db'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"已删除旧数据库文件: {db_file}")
        
        # 创建表
        with db.engine.connect() as conn:
            # 创建商品表
            conn.execute(db.text("""
            CREATE TABLE product (
                code VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category_id VARCHAR(20),
                unit VARCHAR(20),
                wholesale_price FLOAT,
                model VARCHAR(100),
                base_cost FLOAT,
                default_supplier VARCHAR(100),
                default_warehouse VARCHAR(100),
                status VARCHAR(20) DEFAULT '正常'
            )
            """))
            
            # 提交事务
            conn.commit()
        
        # 验证表结构
        inspector = db.inspect(db.engine)
        print("\n=== 验证表结构 ===")
        
        print("\n产品表字段:")
        for column in inspector.get_columns('product'):
            print(f"- {column['name']}: {column['type']}")
        
        print("\n表创建成功！")

if __name__ == "__main__":
    create_tables() 