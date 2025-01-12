from app import app, db, ProductionRecord

def check_database():
    with app.app_context():
        # 检查记录总数
        total_records = ProductionRecord.query.count()
        print(f"数据库中总记录数: {total_records}")

        if total_records > 0:
            # 获取一条示例记录
            sample = ProductionRecord.query.first()
            print("\n示例记录:")
            print(f"日期: {sample.date}")
            print(f"产品: {sample.product_name}")
            print(f"销售: {sample.sales}")
            print(f"库存: {sample.inventory}")
            
            # 计算关键指标
            query = db.session.query(
                db.func.sum(ProductionRecord.sales * ProductionRecord.wholesale_price).label('revenue'),
                db.func.count(db.distinct(ProductionRecord.product_code)).label('product_count')
            ).first()
            
            print("\n关键指标:")
            print(f"总销售额: ¥{query.revenue or 0:,.2f}")
            print(f"产品数量: {query.product_count or 0}")
        else:
            print("警告: 数据库中没有记录！")

if __name__ == "__main__":
    check_database() 