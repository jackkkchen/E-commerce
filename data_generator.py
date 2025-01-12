import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置随机种子
np.random.seed(42)

# 基础数据定义
PRODUCT_CATEGORIES = {
    'LCD': {'hot_rate': 0.8, 'base_cost': 1000},
    'OLED': {'hot_rate': 0.9, 'base_cost': 2000},
    'QLED': {'hot_rate': 0.85, 'base_cost': 1800},
    'Mini-LED': {'hot_rate': 0.95, 'base_cost': 2500}
}

SIZES = {
    43: {'cost_factor': 1.0},
    50: {'cost_factor': 1.2},
    55: {'cost_factor': 1.5},
    65: {'cost_factor': 2.0},
    75: {'cost_factor': 2.5},
    85: {'cost_factor': 3.0}
}

SUPPLIERS = ['富士康', '京东方', '华星光电', 'LG Display', '三星显示']
WAREHOUSES = ['成品仓-A', '成品仓-B', '物料仓-A', '物料仓-B']

def generate_product_code(category, size, index):
    """生成商品编码"""
    return f"{category[:2]}{size}{str(index).zfill(4)}"

def generate_products():
    products = []
    index = 1
    
    for category, cat_info in PRODUCT_CATEGORIES.items():
        for size, size_info in SIZES.items():
            # 基准成本
            base_cost = cat_info['base_cost'] * size_info['cost_factor']
            
            # 批发价（成本加成30-50%）
            wholesale_price = base_cost * np.random.uniform(1.3, 1.5)
            
            # 随机选择供应商和仓库
            default_supplier = np.random.choice(SUPPLIERS)
            default_warehouse = np.random.choice(WAREHOUSES)
            
            # 判断是否热门款
            is_hot = np.random.random() < cat_info['hot_rate']
            popularity = '热门款' if is_hot else '冷门款'
            
            product = {
                'product_code': generate_product_code(category, size, index),
                'category': category,
                'popularity': popularity,
                'size': f"{size}寸",
                'model': f"{category}-{size}",
                'product_name': f"{category} {size}寸 智能电视",
                'wholesale_price': round(wholesale_price, 2),
                'base_cost': round(base_cost, 2),
                'default_supplier': default_supplier,
                'default_warehouse': default_warehouse
            }
            products.append(product)
            index += 1
    
    return products

def generate_daily_data(products, start_date, days=365):
    data = []
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        for product in products:
            # 根据是否热门款调整基础生产量
            base_production = 150 if product['popularity'] == '热门款' else 50
            
            # 生产数量（考虑随机波动）
            production = max(0, int(np.random.normal(base_production, base_production * 0.2)))
            
            # 销售数量（基于生产数量，但略少）
            max_sales = production + (np.random.randint(-10, 10))  # 可能销售一些库存
            sales = max(0, min(production, int(max_sales * np.random.uniform(0.7, 0.95))))
            
            # 库存量计算
            if day == 0:
                inventory = production - sales
            else:
                # 找到前一天的记录
                prev_records = [r for r in data if r['product_code'] == product['product_code'] 
                              and r['date'] == current_date - timedelta(days=1)]
                prev_inventory = prev_records[0]['inventory'] if prev_records else 0
                inventory = prev_inventory + production - sales
            
            record = {
                'date': current_date,
                **product,
                'production': production,
                'sales': sales,
                'inventory': inventory
            }
            data.append(record)
    
    return pd.DataFrame(data)

if __name__ == '__main__':
    # 生成产品数据
    products = generate_products()
    
    # 生成每日生产销售数据
    start_date = datetime(2023, 1, 1)
    df = generate_daily_data(products, start_date)
    
    # 保存为CSV文件
    df.to_csv('tv_screen_data.csv', index=False, encoding='utf-8-sig')
    
    # 打印数据预览
    print("\n数据预览:")
    print(df.head())
    
    # 打印产品列表
    print("\n产品列表:")
    products_df = pd.DataFrame(products)
    print(products_df.to_string()) 