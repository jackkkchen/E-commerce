import mysql.connector
import json
import pandas as pd

# 从外部文件读取 MySQL 配置信息
with open('data/db_config.json', 'r') as file:
    config = json.load(file)

# 连接到 MySQL 数据库
conn = mysql.connector.connect(
    host=config['host'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)

cursor = conn.cursor()

# 读取 .xlsx 文件
file_path = 'data/product_cate_organized.xlsx'
df = pd.read_excel(file_path)

# 获取表名（假设文件名即为表名）
table_name = file_path.split('/')[-1].split('.')[0]

# 获取列名
columns = df.columns.tolist()

# 创建表（如果不存在）
create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{col} TEXT' for col in columns])})"
cursor.execute(create_table_query)

# 将数据插入到 MySQL 数据库
for index, row in df.iterrows():
    # 将 NaN 值转换为 None
    row = row.where(pd.notnull(row), None)
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    cursor.execute(insert_query, tuple(row))

conn.commit()
cursor.close()
conn.close()