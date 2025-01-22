import mysql.connector
import sys
import os
import json

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from app.utils import connect_db


def query_bom(bom_code):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 创建父表视图
        create_parent_view = """
        CREATE OR REPLACE VIEW bom_parent_view AS
        SELECT *
        FROM 物料清单父件
        WHERE 物料清单编码 = %s
        """
        cursor.execute(create_parent_view, (bom_code,))

        # 创建子表视图
        create_child_view = """
        CREATE OR REPLACE VIEW bom_child_view AS
        SELECT *
        FROM 物料清单父子件
        WHERE 物料清单编码 = %s
        """
        cursor.execute(create_child_view, (bom_code,))

        # 查询父表视图中的记录数
        cursor.execute("SELECT COUNT(*) FROM bom_parent_view")
        parent_count = cursor.fetchone()[0]

        # 查询子表视图中的记录数
        cursor.execute("SELECT COUNT(*) FROM bom_child_view")
        child_count = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return {
            'success': True,
            'message': f'查询成功：父表 {parent_count} 条记录，子表 {child_count} 条记录',
            'data': {
                'parent_count': parent_count,
                'child_count': child_count
            }
        }

    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return {
            'success': False,
            'message': f'查询失败：{str(e)}'
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        result = {
            'success': False,
            'message': '请提供物料清单编码'
        }
    else:
        result = query_bom(sys.argv[1])
    
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result['success'] else 1)


