from app import app, db, ProductionRecord
import pandas as pd

def view_data():
    with app.app_context():  # 添加应用上下文
        # 获取基本统计信息
        total_records = ProductionRecord.query.count()
        print(f"\n总记录数：{total_records}")
        
        # 显示最近的记录
        print("\n最近5条记录：")
        recent_records = ProductionRecord.query.order_by(ProductionRecord.date.desc()).limit(5).all()
        for record in recent_records:
            print(f"日期: {record.date}, 产品: {record.product}, "
                  f"生产: {record.production}, 销售: {record.sales}")
        
        # 按产品统计
        print("\n按产品统计总量：")
        df = pd.read_sql(
            """
            SELECT 
                product,
                COUNT(*) as 记录数,
                SUM(production) as 总生产量,
                SUM(sales) as 总销售量,
                AVG(production) as 平均生产量,
                AVG(sales) as 平均销售量
            FROM production_record
            GROUP BY product
            """,
            db.engine
        )
        print(df.to_string())  # 使用 to_string() 确保完整显示

        # 添加每日统计
        print("\n最近7天的每日统计：")
        daily_stats = pd.read_sql(
            """
            SELECT 
                date,
                COUNT(*) as 产品数,
                SUM(production) as 总生产量,
                SUM(sales) as 总销售量
            FROM production_record
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
            """,
            db.engine
        )
        print(daily_stats.to_string())

if __name__ == "__main__":
    view_data() 