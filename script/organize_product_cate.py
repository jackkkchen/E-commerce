import pandas as pd
import numpy as np

# 读取 csv 文件
df = pd.read_csv(r'data/product_cate.csv', encoding='utf-8')

# 将空单元格转为 NaN
df.fillna(value=np.nan, inplace=True)

# 确保表格内容都是字符串类型，以避免数据类型不一致的问题
df['分类编码'] = df['分类编码'].astype(str)
df['分类名称'] = df['分类名称'].astype(str)
df['上级分类'] = df['上级分类'].astype(str)

# 初始化结果 DataFrame
result = pd.DataFrame(columns=['分类序号', '分类名称', '上级分类序号', '分类等级', '分类编码'])

# 初始化分类 ID 和层级
category_id = 1
level = 1

# 获取一级分类（只存在于上级分类列，不存在于分类名称列的分类，或上级分类为空的分类，或上级分类为自身的分类），并输出为列表
first_level_categories = df[(~df['上级分类'].isin(df['分类名称'])) | (
    df['上级分类'].isna()) | (df['上级分类'] == df['分类名称'])]['分类名称'].tolist()

# 递归函数来处理分类层级
def process_category(categories, parent_id, level):
    global category_id
    rows = []
    for category in categories:
        rows.append({
            '分类序号': category_id,
            '分类名称': category,
            '上级分类序号': int(parent_id) if parent_id is not None else None,
            '分类等级': level,
            '分类编码': None
        })
        category_id += 1
        sub_categories = df[df['上级分类'] == category]['分类名称'].tolist()
        rows.extend(process_category(sub_categories, category_id - 1, level + 1))
    return rows

# 处理一级分类
result = pd.concat([result, pd.DataFrame(process_category(first_level_categories, None, 1))], ignore_index=True)

# 处理产品分类编码
for index, row in df.iterrows():
    category_name = row['分类名称']
    product_id = row['分类编码']
    result.loc[result['分类名称'] == category_name, '分类编码'] = product_id

# 输出结果到 Excel 文件
result.to_excel('data/product_cate_organized.xlsx', index=False)