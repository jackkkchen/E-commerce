import pandas as pd
import mysql.connector
import sys
import os
import json
import tkinter as tk
from tkinter import filedialog

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from app.utils import connect_db

# 接受用户输入的多个「物料清单编码」及其对应的「所需商品数量」在数据库中生成临时视图「BOM」
def create_bom_view(bom_data):
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 创建临时视图
        query = """
        CREATE OR REPLACE VIEW BOM AS
        SELECT 
            子件商品,
            规格型号,
            默认供应商,
            SUM(需用数量) AS 需用数量_单件,
            成本单价,
            SUM(成本金额) AS 成本金额,
            SUM(需用数量 * multiplier) AS 需用数量_总计,
            SUM(成本金额 * cost_multiplier) AS 成本金额_总计
        FROM (
        """
        for i, (bom_code, quantity) in enumerate(bom_data.items()):
            if i > 0:
                query += "UNION ALL\n"
            query += f"""
            SELECT 
                子件商品,
                规格型号,
                默认供应商,
                需用数量,
                成本单价,
                成本金额,
                {quantity} AS multiplier,
                {quantity} AS cost_multiplier
            FROM 
                物料清单父子件
            WHERE 
                物料清单编码 = '{bom_code}'
            """
        query += ") AS combined GROUP BY 子件商品, 规格型号, 默认供应商, 成本单价;"

        cursor.execute(query)
        conn.commit()
        return True

    except Exception as e:
        print(json.dumps({'success': False, 'message': f'创建视图失败：{str(e)}'}, ensure_ascii=False))
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_export_directory():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    directory = filedialog.askdirectory(title="选择导出文件夹")
    return directory

def call_procedure():
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 检查并删除已存在的存储过程
        cursor.execute("DROP PROCEDURE IF EXISTS create_supplier_views")
        conn.commit()

        # 创建存储过程
        cursor.execute("""
        CREATE PROCEDURE create_supplier_views()
        BEGIN
            DECLARE done INT DEFAULT FALSE;
            DECLARE supplier_name VARCHAR(100);
            DECLARE cur_supplier CURSOR FOR SELECT DISTINCT COALESCE(默认供应商, '未知供应商') FROM BOM;
            DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

            OPEN cur_supplier;
            read_loop: LOOP
                FETCH cur_supplier INTO supplier_name;
                IF done THEN
                    LEAVE read_loop;
                END IF;

                SET @sql = CONCAT(
                    'CREATE OR REPLACE VIEW `', supplier_name, '` AS
                    SELECT
                        子件商品,
                        规格型号,
                        需用数量_单件,
                        成本单价,
                        成本金额,
                        需用数量_总计,
                        成本金额_总计
                    FROM BOM
                    WHERE COALESCE(默认供应商, ''未知供应商'') = ''', supplier_name, ''''
                );

                PREPARE stmt FROM @sql;
                EXECUTE stmt;
                DEALLOCATE PREPARE stmt;
            END LOOP;

            CLOSE cur_supplier;
        END;
        """)
        conn.commit()

        # 调用存储过程
        cursor.execute("CALL create_supplier_views()")
        conn.commit()

        # 获取导出目录
        export_dir = get_export_directory()
        if not export_dir:
            print(json.dumps({'success': False, 'message': '未选择导出目录'}, ensure_ascii=False))
            return

        # 获取所有供应商
        cursor.execute("SELECT DISTINCT COALESCE(默认供应商, '未知供应商') FROM BOM")
        suppliers = cursor.fetchall()
        
        if not suppliers:
            print(json.dumps({'success': False, 'message': '没有找到供应商数据'}, ensure_ascii=False))
            return

        # 导出每个供应商的数据
        for supplier in suppliers:
            supplier_name = supplier[0]
            try:
                cursor.execute(f"SELECT * FROM `{supplier_name}`")
                data = cursor.fetchall()
                if not data:
                    continue

                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(data, columns=columns)

                # 计算成本金额汇总
                total_cost = df['成本金额_总计'].sum()
                summary_row = {col: '' for col in df.columns}
                summary_row['成本金额_总计'] = total_cost
                summary_row[df.columns[0]] = '成本金额汇总：'
                summary_df = pd.DataFrame([summary_row])
                df = pd.concat([df, summary_df], ignore_index=True)

                # 保存文件
                file_path = os.path.join(export_dir, f"{supplier_name}.xlsx")
                df.to_excel(file_path, index=False)
                
            except Exception as e:
                print(json.dumps({
                    'success': False, 
                    'message': f'导出供应商 {supplier_name} 数据时出错：{str(e)}'
                }, ensure_ascii=False))
                return

        print(json.dumps({'success': True, 'message': '导出成功'}, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({'success': False, 'message': f'导出失败：{str(e)}'}, ensure_ascii=False))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        bom_data = json.loads(input())
        if create_bom_view(bom_data):
            call_procedure()
    except Exception as e:
        print(json.dumps({'success': False, 'message': str(e)}, ensure_ascii=False))