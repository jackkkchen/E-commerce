import pandas as pd
import mysql.connector
import json
import sys
import os
import traceback

def load_db_config():
    try:
        with open('data/db_config.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"读取数据库配置文件失败: {str(e)}")

def get_db_connection():
    config = load_db_config()
    return mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8mb4'
    )

def validate_and_import_excel(file_path):
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        column_count = len(df.columns)

        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 根据列数判断表格类型并返回结果
        if column_count == 6:
            # 处理父表
            return process_parent_table(df, cursor, conn)
        elif column_count == 16:
            # 处理子表
            return process_child_table(df, cursor, conn)
        else:
            # 直接返回错误消息，不打印
            return {
                'success': False,
                'message': f'表格列数不正确。应为6列(父表)或16列(子表)，实际为{column_count}列'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'导入过程出错: {str(e)}'
        }
    finally:
        if 'conn' in locals():
            conn.close()

def process_parent_table(df, cursor, conn):
    try:
        # 获取数据库表的列名
        cursor.execute("SHOW COLUMNS FROM 物料清单父件")
        db_columns = [column[0] for column in cursor.fetchall()]

        # 检查列名匹配
        expected_columns = ['物料清单编码', '条码', '父件预入仓库', '父件商品', '生产数量', '成本金额']
        df_columns = df.columns.tolist()
        
        # 验证列名
        mismatched_columns = []
        for exp_col, df_col in zip(expected_columns, df_columns):
            if exp_col != df_col:
                mismatched_columns.append(f"预期列名: {exp_col}, 实际列名: {df_col}")

        if mismatched_columns:
            return {
                'success': False,
                'message': '列名不匹配:\n' + '\n'.join(mismatched_columns)
            }

        # 插入数据
        for _, row in df.iterrows():
            values = [row[col] if pd.notna(row[col]) else None for col in df_columns]
            placeholders = ', '.join(['%s'] * len(values))
            columns = ', '.join(df_columns)
            
            insert_query = f"INSERT INTO 物料清单父件 ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, values)

        conn.commit()
        return {
            'success': True,
            'message': f'成功导入{len(df)}条父表记录'
        }

    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'message': f'处理父表时出错: {str(e)}'
        }

def process_child_table(df, cursor, conn):
    try:
        print(f"开始处理子表，列数：{len(df.columns)}", file=sys.stderr)
        print(f"列名：{df.columns.tolist()}", file=sys.stderr)

        # 重命名生产数量列
        df_columns = df.columns.tolist()
        
        # 修改查找逻辑，同时查找 '生产数量' 和 '生产数量.1'
        production_qty_indices = []
        for i, col in enumerate(df_columns):
            if col == '生产数量' or col == '生产数量.1':
                production_qty_indices.append(i)
        
        print(f"找到的生产数量列索引：{production_qty_indices}", file=sys.stderr)
        
        if len(production_qty_indices) != 2:
            return {
                'success': False,
                'message': f'子表必须包含两个生产数量列，实际找到 {len(production_qty_indices)} 个'
            }

        # 根据列的位置确定父件和子件的生产数量
        parent_qty_idx = min(production_qty_indices)  # 第一个生产数量列
        child_qty_idx = max(production_qty_indices)   # 第二个生产数量列
        
        print(f"父件生产数量列索引：{parent_qty_idx}", file=sys.stderr)
        print(f"子件生产数量列索引：{child_qty_idx}", file=sys.stderr)

        # 重命名列
        df_columns[parent_qty_idx] = '生产数量_父件'
        df_columns[child_qty_idx] = '生产数量_子件'
        df.columns = df_columns

        # 检查列名匹配
        expected_columns = [
            '物料清单编码', '版本号', '条码', '父件预入仓库', '父件商品', 
            '生产数量_父件', '子件预出仓库', '子件商品', '规格型号', '默认供应商',
            '生产数量_子件', '子件版本号', '计量单位', '需用数量', '成本单价', '成本金额'
        ]
        
        # 验证列名
        mismatched_columns = []
        actual_columns = df_columns[:len(expected_columns)]
        for exp_col, df_col in zip(expected_columns, actual_columns):
            if exp_col != df_col:
                mismatched_columns.append(f"预期列名: {exp_col}, 实际列名: {df_col}")

        if mismatched_columns:
            print(f"列名不匹配详情：{mismatched_columns}", file=sys.stderr)
            return {
                'success': False,
                'message': '列名不匹配:\n' + '\n'.join(mismatched_columns)
            }

        # 只保留需要的列
        df = df[expected_columns]

        # 插入数据
        for _, row in df.iterrows():
            values = [row[col] if pd.notna(row[col]) else None for col in expected_columns]
            placeholders = ', '.join(['%s'] * len(values))
            columns = ', '.join(expected_columns)
            
            insert_query = f"INSERT INTO 物料清单父子件 ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, values)

        conn.commit()
        
        # 修改这里的输出方式，只输出一次结果
        result = {
            'success': True,
            'message': f'成功导入{len(df)}条子表记录'
        }
        # 不再调用 print，直接返回结果
        return result

    except Exception as e:
        print(f"处理子表时出错: {str(e)}", file=sys.stderr)
        print(f"详细错误: {traceback.format_exc()}", file=sys.stderr)
        conn.rollback()
        return {
            'success': False,
            'message': f'处理子表时出错: {str(e)}'
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        result = {
            'success': False,
            'message': '请提供Excel文件路径'
        }
    else:
        result = validate_and_import_excel(sys.argv[1])
    
    # 只输出一次结果
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get('success', False) else 1)