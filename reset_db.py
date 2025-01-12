from app import app, db

with app.app_context():
    # 删除所有表
    db.drop_all()
    # 重新创建所有表
    db.create_all()
    
print("数据库已重置！") 