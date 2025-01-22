import pandas as pd
# 将 xlsx 文件转为 csv 文件
df = pd.read_excel('data/product_cate.xlsx')
df.to_csv('data/product_cate.csv', index=False)
# 输出csv文件
