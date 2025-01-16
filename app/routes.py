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

        print(f"接收到的分类名称: {category_name}")  # 调试输出

        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 'script', 'generate_temporary_view.py')
        
        result = subprocess.run(
            [sys.executable, script_path, category_name],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"脚本输出 (stdout): {result.stdout}")  # 调试输出
        print(f"脚本错误 (stderr): {result.stderr}")  # 调试输出
        print(f"返回码: {result.returncode}")  # 调试输出

        if result.returncode != 0:
            return jsonify({'error': f'生成视图失败: {result.stderr}'}), 500

        try:
            data = json.loads(result.stdout)
            if not data.get('success'):
                return jsonify({'error': data.get('error', '未知错误')}), 500
            return jsonify(data)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {str(e)}")  # 调试输出
            print(f"原始输出: {result.stdout}")  # 调试输出
            return jsonify({'error': f'JSON解析失败: {str(e)}'}), 500

    except Exception as e:
        print(f"生成视图时发生错误: {str(e)}")  # 调试输出
        print(f"完整错误信息: {traceback.format_exc()}")  # 调试输出
        return jsonify({'error': str(e)}), 500

# 添加错误处理路由
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500