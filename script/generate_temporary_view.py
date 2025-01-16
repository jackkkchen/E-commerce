import mysql.connector
import json
import sys
import traceback
import codecs

# 设置标准输出编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def create_category_view(input_category):
    try:
        print(f"开始处理分类: {input_category}", file=sys.stderr)
        
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

        # 首先检查分类是否存在
        cursor.execute("SELECT * FROM product_cate_organized WHERE 分类名称 = %s", (input_category,))
        category_exists = cursor.fetchone()
        print(f"分类查询结果: {category_exists}", file=sys.stderr)

        # 修改查询语句，直接查询该分类下的所有商品
        query = """
        SELECT 
            p.`商品编码`,
            p.`商品名称`,
            p.`商品分类`,
            p.`规格型号`,
            p.`计量单位`,
            p.`基准批发价`,
            p.`参考成本`,
            p.`默认供应商`,
            p.`默认仓库`
        FROM 
            product p
        WHERE 
            p.`商品分类` = %s
        """

        cursor.execute(query, (input_category,))
        results = cursor.fetchall()
        print(f"查询到 {len(results)} 条记录", file=sys.stderr)

        # 处理结果
        processed_results = []
        for row in results:
            processed_row = {}
            for key, value in row.items():
                processed_row[key] = str(value) if value is not None else ''
            processed_results.append(processed_row)

        cursor.close()
        conn.close()

        # 返回结果
        response = {
            'success': True,
            'data': processed_results
        }
        
        print(f"返回数据: {json.dumps(response, ensure_ascii=False)}", file=sys.stderr)
        print(json.dumps(response, ensure_ascii=False))
        return 0

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        print(f"错误堆栈: {traceback.format_exc()}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '请提供分类名称'
        }, ensure_ascii=False))
        sys.exit(1)

    sys.exit(create_category_view(sys.argv[1]))