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

# 获取一级分类（只存在于上级分类列，不存在于分类名称列的分类，或上级分类为空的分类，或上级分类为自身的分类），并输出为列表
first_level_categories = df[(~df['上级分类'].isin(df['分类名称'])) | (
    df['上级分类'].isna()) | (df['上级分类'] == df['分类名称'])]['分类名称'].tolist()
# print(seventh_level_categories)
print(f'一级分类数量：{len(first_level_categories)}')

# 获取二级分类（上级分类为一级分类的分类），并输出为列表
second_level_categories = df[df['上级分类'].isin(
    first_level_categories)]['分类名称'].tolist()
# print(second_level_categories)
print(f'二级分类数量：{len(second_level_categories)}')

# 获取三级分类（上级分类为二级分类的分类），并输出为列表
third_level_categories = df[df['上级分类'].isin(
    second_level_categories)]['分类名称'].tolist()
# print(third_level_categories)
print(f'三级分类数量：{len(third_level_categories)}')

# 获取四级分类（上级分类为三级分类的分类），并输出为列表
fourth_level_categories = df[df['上级分类'].isin(
    third_level_categories)]['分类名称'].tolist()
# print(fourth_level_categories)
print(f'四级分类数量：{len(fourth_level_categories)}')

# 获取五级分类（上级分类为四级分类的分类），并输出为列表
fifth_level_categories = df[df['上级分类'].isin(
    fourth_level_categories)]['分类名称'].tolist()
# print(fifth_level_categories)
print(f'五级分类数量：{len(fifth_level_categories)}')

# 获取六级分类（上级分类为五级分类的分类），并输出为列表
sixth_level_categories = df[df['上级分类'].isin(
    fifth_level_categories)]['分类名称'].tolist()
# print(seventh_level_categories)
print(f'六级分类数量：{len(sixth_level_categories)}')

# 获取七级分类（上级分类为六级分类的分类），并输出为列表
seventh_level_categories = df[df['上级分类'].isin(
    sixth_level_categories)]['分类名称'].tolist()
# print(seventh_level_categories)
print(f'七级分类数量：{len(seventh_level_categories)}')

# 获取各级分类的最大长度
max_length = max(len(first_level_categories), len(second_level_categories), len(third_level_categories),
                 len(fourth_level_categories), len(fifth_level_categories), len(sixth_level_categories), len(seventh_level_categories))

# 使用 reindex 方法将所有分类列表填充到相同的长度
first_level_categories = pd.Series(first_level_categories).reindex(range(max_length), fill_value='').tolist()
second_level_categories = pd.Series(second_level_categories).reindex(range(max_length), fill_value='').tolist()
third_level_categories = pd.Series(third_level_categories).reindex(range(max_length), fill_value='').tolist()
fourth_level_categories = pd.Series(fourth_level_categories).reindex(range(max_length), fill_value='').tolist()
fifth_level_categories = pd.Series(fifth_level_categories).reindex(range(max_length), fill_value='').tolist()
sixth_level_categories = pd.Series(sixth_level_categories).reindex(range(max_length), fill_value='').tolist()
seventh_level_categories = pd.Series(seventh_level_categories).reindex(range(max_length), fill_value='').tolist()

# 重新排序各级分类列表
first_level_categories.sort()
second_level_categories.sort()
third_level_categories.sort()
fourth_level_categories.sort()
fifth_level_categories.sort()
sixth_level_categories.sort()
seventh_level_categories.sort()

# 将各级分类名称输出到 Excel 文件，每一级占一列
result = pd.DataFrame({
    '一级分类': first_level_categories,
    '二级分类': second_level_categories,
    '三级分类': third_level_categories,
    '四级分类': fourth_level_categories,
    '五级分类': fifth_level_categories,
    '六级分类': sixth_level_categories,
    '七级分类': seventh_level_categories
})

result.to_excel('output/categories.xlsx', index=False)
