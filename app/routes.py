from flask import render_template, jsonify, request
from app import app
from app.utils import read_category_hierarchy
import subprocess
import sys
import os
import json
import traceback
# 主页路由
@app.route('/')
@app.route('/index')
def index():
    try:
        categories = read_category_hierarchy()
        return render_template('index.html', categories=categories)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return str(e), 500

# 生成视图的路由
@app.route('/generate_view', methods=['POST'])
def generate_view():
    try:
        category_name = request.json.get('category_name')
        if not category_name:
            return jsonify({'error': '分类名称不能为空'}), 400

        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 'script', 'generate_temporary_view_product.py')
        
        # 使用 UTF-8 编码执行脚本
        result = subprocess.run(
            [sys.executable, script_path, category_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )

        if result.returncode != 0:
            print(f"脚本错误输出: {result.stderr}")
            return jsonify({'error': f'生成视图失败: {result.stderr}'}), 500

        try:
            if not result.stdout.strip():
                return jsonify({'error': '脚本没有返回数据'}), 500

            data = json.loads(result.stdout)
            return jsonify(data)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            print(f"原始输出: {result.stdout}")
            return jsonify({'error': f'JSON解析失败: {str(e)}'}), 500

    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 添加错误处理路由
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500