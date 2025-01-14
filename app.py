from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

# 连接到 MySQL 数据库
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="wenxi.Zhao0115",
    database="your_database"
)

# 从数据库加载数据
def load_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_cate_sorted")
    data = cursor.fetchall()
    cursor.close()
    return data

# 将数据转换为层级结构
def build_category_tree(data):
    tree = {}
    for row in data:
        category_id = row['产品编号']
        parent_id = row['上级分类编号']
        category_name = row['分类名称']
        
        if parent_id not in tree:
            tree[parent_id] = []
        tree[parent_id].append({'id': category_id, 'name': category_name})
    
    return tree

data = load_data()
category_tree = build_category_tree(data)

@app.route('/categories')
def categories():
    # 返回顶级分类
    top_level_categories = category_tree.get(None, [])
    return jsonify({'categories': top_level_categories})

@app.route('/categories/<int:category_id>')
def subcategories(category_id):
    # 返回子分类
    subcategories = category_tree.get(category_id, [])
    return jsonify({'subcategories': subcategories})

if __name__ == '__main__':
    app.run(debug=True)