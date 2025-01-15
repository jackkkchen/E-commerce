from app import app, db
import os

def reset_database():
    db_file = 'factory.db'
    
    # 删除现有数据库文件
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"已删除旧数据库文件: {db_file}")
        except Exception as e:
            print(f"删除数据库文件失败: {str(e)}")
            return False
    
    # 创建新的数据库和表
    with app.app_context():
        try:
            db.create_all()
            
            # 验证表是否创建成功
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n已创建的表: {', '.join(tables)}")
            
            # 检查 product 表的结构
            if 'product' in tables:
                columns = inspector.get_columns('product')
                print("\nProduct表结构:")
                for column in columns:
                    print(f"- {column['name']}: {column['type']}")
            
            return True
        except Exception as e:
            print(f"创建数据库失败: {str(e)}")
            return False

if __name__ == "__main__":
    if reset_database():
        print("\n数据库重置成功！")
    else:
        print("\n数据库重置失败！") 