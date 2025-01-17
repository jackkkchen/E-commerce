from pypinyin import pinyin, Style
import mysql.connector
import json

def get_pinyin(word):
    """获取中文的拼音，用于排序"""
    if not word:
        return ''
    return ''.join([p[0] for p in pinyin(word, style=Style.NORMAL)])

def read_category_hierarchy():
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

        query = """
        WITH RECURSIVE CategoryPath AS (
            SELECT 
                分类序号,
                分类名称,
                上级分类序号,
                CAST(分类名称 AS CHAR(1000)) as path,
                CAST(分类序号 AS CHAR(1000)) as id_path,
                1 as level
            FROM product_cate_organized
            WHERE 上级分类序号 IS NULL

            UNION ALL

            SELECT 
                c.分类序号,
                c.分类名称,
                c.上级分类序号,
                CONCAT(p.path, ' > ', c.分类名称),
                CONCAT(p.id_path, ',', c.分类序号),
                p.level + 1
            FROM product_cate_organized c
            INNER JOIN CategoryPath p ON c.上级分类序号 = p.分类序号
        )
        SELECT * FROM CategoryPath
        ORDER BY id_path;
        """

        cursor.execute(query)
        all_categories = cursor.fetchall()

        def build_tree():
            tree = []
            categories_dict = {}

            # 首先创建所有节点的字典
            for cat in all_categories:
                categories_dict[cat['分类序号']] = {
                    'id': cat['分类序号'],
                    'name': cat['分类名称'],
                    'children': [],
                    'level': cat['level'],
                    'path': cat['path'],
                    'pinyin': get_pinyin(cat['分类名称'])  # 添加拼音属性
                }

            # 构建树形结构
            for cat in all_categories:
                node = categories_dict[cat['分类序号']]
                if cat['上级分类序号'] is None:
                    tree.append(node)
                else:
                    parent = categories_dict.get(cat['上级分类序号'])
                    if parent:
                        parent['children'].append(node)

            # 递归排序函数
            def sort_tree(node):
                if node.get('children'):
                    node['children'] = sorted(node['children'], key=lambda x: x['pinyin'])
                    for child in node['children']:
                        sort_tree(child)
                return node

            # 对整个树进行排序
            tree = sorted(tree, key=lambda x: x['pinyin'])
            for node in tree:
                sort_tree(node)

            return tree

        result = build_tree()
        cursor.close()
        conn.close()
        return result

    except Exception as e:
        print(f"读取分类层级时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []