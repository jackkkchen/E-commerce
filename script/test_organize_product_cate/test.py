import pandas as pd

# 读取指定 .xlsx 文件
df = pd.read_excel(r'output/output_file.xlsx')

# # 统计其中 level 列的值的分布情况
# level_distribution = df['level'].value_counts().sort_index()
# print(level_distribution)

# 获取各等级分类的内容，并将其输出为 Excel 文件，每个等级占据一列
level_1 = sorted(df[df['level'] == 1]['category_name'].tolist())
level_2 = sorted(df[df['level'] == 2]['category_name'].tolist())
level_3 = sorted(df[df['level'] == 3]['category_name'].tolist())
level_4 = sorted(df[df['level'] == 4]['category_name'].tolist())
level_5 = sorted(df[df['level'] == 5]['category_name'].tolist())
level_6 = sorted(df[df['level'] == 6]['category_name'].tolist())
level_7 = sorted(df[df['level'] == 7]['category_name'].tolist())

# 获取各级分类的最大长度
max_length = max(len(level_1), len(level_2), len(level_3), len(level_4), len(level_5), len(level_6), len(level_7))

# 使用 reindex 方法将所有分类列表填充到相同的长度
level_1 = pd.Series(level_1).reindex(range(max_length), fill_value='').tolist()
level_2 = pd.Series(level_2).reindex(range(max_length), fill_value='').tolist()
level_3 = pd.Series(level_3).reindex(range(max_length), fill_value='').tolist()
level_4 = pd.Series(level_4).reindex(range(max_length), fill_value='').tolist()
level_5 = pd.Series(level_5).reindex(range(max_length), fill_value='').tolist()
level_6 = pd.Series(level_6).reindex(range(max_length), fill_value='').tolist()
level_7 = pd.Series(level_7).reindex(range(max_length), fill_value='').tolist()

# 将各等级分类内容输出为 Excel 文件
level_df = pd.DataFrame({
    'level_1': level_1,
    'level_2': level_2,
    'level_3': level_3,
    'level_4': level_4,
    'level_5': level_5,
    'level_6': level_6,
    'level_7': level_7
})
level_df.to_excel('output/level_categories.xlsx', index=False)