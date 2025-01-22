import pandas as pd
import mysql.connector
import sys
import os
import json

with open('data/db_config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

# 连接数据库
def connect_db():
    conn = mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8mb4'
    )
    return conn

# 接受用户输入的多个「物料清单编码」及其对应的「所需商品数量」在数据库中生成临时视图「BOM」
def create_bom_view(bom_data):
    conn = connect_db()
    cursor = conn.cursor()

    # 创建临时视图
    query = """
    CREATE OR REPLACE VIEW BOM AS
    SELECT 
        物料清单编码,
        子件商品,
        规格型号,
        默认供应商,
        需用数量_单件,
        成本单价,
        成本金额,
        SUM(需用数量_总计) AS 需用数量_总计,
        SUM(成本金额_总计) AS 成本金额_总计
    FROM (
    """
    for i, (bom_code, quantity) in enumerate(bom_data.items()):
        query += f"""
        SELECT 
            物料清单编码,
            子件商品,
            规格型号,
            默认供应商,
            需用数量 AS 需用数量_单件,
            成本单价,
            成本金额,
            需用数量 * {quantity} AS 需用数量_总计,
            成本金额 * {quantity} AS 成本金额_总计
        FROM 
            物料清单父子件
        WHERE 
            物料清单编码 = '{bom_code}'
        """
        if i < len(bom_data) - 1:
            query += "UNION ALL\n"
    query += ") AS combined GROUP BY 物料清单编码, 子件商品, 规格型号, 默认供应商, 需用数量_单件, 成本单价, 成本金额;"

    cursor.execute(query)
    conn.commit()

    # 查询临时视图
    cursor.execute("SELECT * FROM BOM")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

# 在数据库中查询是否存在指定的存储过程 create_supplier_views，如果不存在则创建，如果存在则调用该存储过程，将该存储过程输出的所有视图都下载为 .xlsx 文件
# 创建或调用存储过程
def call_procedure():
    conn = connect_db()
    cursor = conn.cursor()

    # 检查存储过程是否存在
    cursor.execute("SHOW PROCEDURE STATUS LIKE 'create_supplier_views'")
    result = cursor.fetchone()

    if not result:
        # 创建存储过程
        cursor.execute("""
CREATE PROCEDURE create_supplier_views()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE supplier_name CHAR(100);
    DECLARE cur_supplier CURSOR FOR SELECT DISTINCT COALESCE(默认供应商, '未知供应商') AS 默认供应商 FROM BOM;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- 遍历所有供应商
    OPEN cur_supplier;
    read_loop: LOOP
        FETCH cur_supplier INTO supplier_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- 创建视图
        SET @sql = CONCAT(
            'CREATE OR REPLACE VIEW `', supplier_name, '` AS
            SELECT
                物料清单编码,
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

    # 获取所有视图名称
    cursor.execute("SELECT DISTINCT COALESCE(默认供应商, '未知供应商') AS 默认供应商 FROM BOM")
    views = cursor.fetchall()

    # 下载所有视图为 .xlsx 文件
    for view in views:
        view_name = view[0]
        cursor.execute(f"SELECT * FROM `{view_name}`")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=columns)

        # 计算成本金额汇总
        total_cost = df['成本金额_总计'].sum()
        summary_row = {col: '' for col in df.columns}
        summary_row['成本金额_总计'] = total_cost
        summary_row[df.columns[-2]] = '成本金额汇总：'
        summary_df = pd.DataFrame([summary_row])
        df = pd.concat([df, summary_df], ignore_index=True)

        df.to_excel(f"{view_name}.xlsx", index=False)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    bom_data = input("请输入物料清单编码及其对应的数量 (JSON 格式): ")
    bom_data = json.loads(bom_data)
    create_bom_view(bom_data)
    call_procedure()