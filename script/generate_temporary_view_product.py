import mysql.connector
import json
import sys
import traceback
import os

# 设置环境变量以强制使用 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

def create_category_view(input_category):
    try:
        with open('data/db_config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)

        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )

        cursor = conn.cursor(dictionary=True)

        # 首先获取目标分类及其所有子分类
        category_query = """
        WITH RECURSIVE CategoryTree AS (
            SELECT 
                分类序号,
                分类名称,
                上级分类序号
            FROM product_cate_organized
            WHERE 分类名称 = %s
            
            UNION ALL
            
            SELECT 
                c.分类序号,
                c.分类名称,
                c.上级分类序号
            FROM product_cate_organized c
            INNER JOIN CategoryTree ct ON c.上级分类序号 = ct.分类序号
        )
        SELECT 分类名称 FROM CategoryTree;
        """

        cursor.execute(category_query, (input_category,))
        categories = cursor.fetchall()
        category_names = [cat['分类名称'] for cat in categories]
        
        # 如果没有找到子分类，至少包含输入的分类
        if not category_names:
            category_names = [input_category]

        # 构建产品查询
        placeholders = ', '.join(['%s'] * len(category_names))
        product_query = f"""
        SELECT 
            商品编码,
            商品分类,
            计量单位,
            基准批发价,
            规格型号,
            参考成本,
            默认供应商,
            商品名称,
            默认仓库
        FROM product 
        WHERE 商品分类 IN ({placeholders})
        ORDER BY 商品编码;
        """

        cursor.execute(product_query, tuple(category_names))
        results = cursor.fetchall()

        # 处理查询结果
        processed_results = []
        for row in results:
            processed_row = {}
            for key, value in row.items():
                # 处理特殊类型的值
                if isinstance(value, (int, float)):
                    processed_row[key] = str(value)
                elif value is None:
                    processed_row[key] = ''
                else:
                    processed_row[key] = str(value).strip()
            processed_results.append(processed_row)

        cursor.close()
        conn.close()

        # 构造返回数据
        response = {
            'success': True,
            'data': processed_results
        }

        # 使用 UTF-8 编码输出
        sys.stdout.reconfigure(encoding='utf-8')
        print(json.dumps(response, ensure_ascii=False))
        return 0

    except Exception as e:
        error_response = {
            'success': False,
            'error': str(e)
        }
        # 使用 UTF-8 编码输出错误信息
        sys.stdout.reconfigure(encoding='utf-8')
        print(json.dumps(error_response, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        error_response = {
            'success': False,
            'error': '请提供分类名称'
        }
        sys.stdout.reconfigure(encoding='utf-8')
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)

    try:
        sys.exit(create_category_view(sys.argv[1]))
    except Exception as e:
        error_response = {
            'success': False,
            'error': str(e)
        }
        sys.stdout.reconfigure(encoding='utf-8')
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)