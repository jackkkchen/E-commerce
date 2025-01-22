from flask import render_template, jsonify, request
from app import app
from app.utils import read_category_hierarchy
import subprocess
import sys
import os
import json
import traceback
from werkzeug.utils import secure_filename
import logging
from app.utils import connect_db
import mysql.connector
import time

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@app.route('/bom')
def bom():
    return render_template('bom.html')

@app.route('/import_excel', methods=['POST'])
def import_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有上传文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': '只支持Excel文件(.xlsx, .xls)'}), 400

        # 保存上传的文件
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        try:
            # 调用导入脚本
            script_path = os.path.join('script', 'import_xlsx_to_database.py')
            
            logger.debug(f"开始执行脚本: {script_path}")
            logger.debug(f"文件路径: {temp_path}")
            
            # 设置环境变量以确保正确的编码
            my_env = os.environ.copy()
            my_env["PYTHONIOENCODING"] = "gbk"
            
            process = subprocess.Popen(
                [sys.executable, script_path, temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='gbk',  # 使用 GBK 编码
                env=my_env,
                errors='replace'  # 处理编码错误
            )
            
            stdout, stderr = process.communicate()
            
            logger.debug(f"脚本输出: {stdout if stdout else 'None'}")
            logger.debug(f"错误输出: {stderr if stderr else 'None'}")
            
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # 检查输出是否为空
            if not stdout:
                return jsonify({
                    'success': False,
                    'message': stderr or '导入失败：没有返回数据'
                }), 200

            # 尝试解析输出
            try:
                result = json.loads(stdout.strip())
                return jsonify(result), 200
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                logger.error(f"原始输出: {stdout}")
                return jsonify({
                    'success': False,
                    'message': stdout.strip() or stderr.strip() or '数据处理失败'
                }), 200

        except Exception as e:
            logger.error(f"处理过程出错: {str(e)}", exc_info=True)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({
                'success': False,
                'message': str(e)
            }), 200

    except Exception as e:
        logger.error(f"导入过程出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 200

@app.route('/query_bom', methods=['POST'])
def query_bom_route():
    try:
        bom_code = request.form.get('bom_code')
        if not bom_code:
            return jsonify({
                'success': False,
                'message': '请输入物料清单编码'
            }), 400

        # 调用查询脚本
        script_path = os.path.join('script', 'BOM_query.py')
        
        # 设置环境变量以确保正确的编码
        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = "gbk"
        
        process = subprocess.Popen(
            [sys.executable, script_path, bom_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='gbk',  # 使用 GBK 编码
            errors='replace',  # 处理编码错误
            env=my_env
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"查询失败，错误输出：{stderr}")
            return jsonify({
                'success': False,
                'message': f'查询失败：{stderr}'
            }), 500

        try:
            # 尝试解析输出
            if stdout:
                result = json.loads(stdout)
                return jsonify(result)
            else:
                return jsonify({
                    'success': False,
                    'message': '查询失败：没有返回数据'
                }), 500
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误：{e}")
            logger.error(f"原始输出：{stdout}")
            return jsonify({
                'success': False,
                'message': f'数据解析失败：{str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"查询过程出错：{str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'查询失败：{str(e)}'
        }), 500

@app.route('/api/parent_table')
def get_parent_table():
    try:
        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)
            
            # 添加错误处理和重试逻辑
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 检查视图是否存在
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.views 
                        WHERE table_schema = DATABASE() 
                        AND table_name = 'bom_parent_view'
                    """)
                    view_exists = cursor.fetchone() is not None

                    if view_exists:
                        cursor.execute('SELECT * FROM bom_parent_view')
                    else:
                        cursor.execute('SELECT * FROM 物料清单父件')

                    data = cursor.fetchall()
                    return jsonify(data)
                    
                except mysql.connector.Error as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise e
                    time.sleep(0.5)  # 添加短暂延迟后重试
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/child_table')
def get_child_table():
    try:
        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)
            
            # 添加错误处理和重试逻辑
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 检查视图是否存在
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.views 
                        WHERE table_schema = DATABASE() 
                        AND table_name = 'bom_child_view'
                    """)
                    view_exists = cursor.fetchone() is not None

                    if view_exists:
                        cursor.execute('SELECT * FROM bom_child_view')
                    else:
                        cursor.execute('SELECT * FROM 物料清单父子件')

                    data = cursor.fetchall()
                    return jsonify(data)
                    
                except mysql.connector.Error as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise e
                    time.sleep(0.5)  # 添加短暂延迟后重试
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_query', methods=['POST'])
def clear_query():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 分别执行删除视图的操作
        try:
            cursor.execute("DROP VIEW IF EXISTS bom_parent_view")
            conn.commit()
        except Exception as e:
            logger.debug(f"删除父表视图时出错：{str(e)}")
            
        try:
            cursor.execute("DROP VIEW IF EXISTS bom_child_view")
            conn.commit()
        except Exception as e:
            logger.debug(f"删除子表视图时出错：{str(e)}")

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': '查询已清除'
        })

    except Exception as e:
        logger.error(f"清除查询失败：{str(e)}", exc_info=True)
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'message': f'清除查询失败：{str(e)}'
        }), 500

@app.route('/export_statistics', methods=['POST'])
def export_statistics():
    try:
        # 获取前端发送的数据
        bom_data = request.json
        if not bom_data:
            return jsonify({
                'success': False,
                'message': '没有数据需要导出'
            }), 400

        # 调用统计脚本
        script_path = os.path.join('script', 'BOM_statistics.py')
        
        # 将数据转换为JSON字符串
        bom_json = json.dumps(bom_data, ensure_ascii=False)
        
        # 设置环境变量以确保正确的编码
        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = "utf-8"
        
        # 增加超时时间到60秒
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            env=my_env,
            bufsize=1,  # 行缓冲
            universal_newlines=True  # 使用通用换行符
        )
        
        try:
            stdout, stderr = process.communicate(input=bom_json, timeout=120)
            
            if process.returncode != 0:
                logger.error(f"脚本执行失败，返回码：{process.returncode}")
                logger.error(f"错误输出：{stderr}")
                return jsonify({
                    'success': False,
                    'message': f'导出失败：{stderr}'
                }), 500
                
        except subprocess.TimeoutExpired:
            process.kill()
            _, stderr = process.communicate()
            logger.error("导出操作超时")
            return jsonify({
                'success': False,
                'message': '导出操作超时，请重试'
            }), 504

        if stderr:
            logger.error(f"导出错误：{stderr}")
            return jsonify({
                'success': False,
                'message': f'导出失败：{stderr}'
            }), 500

        try:
            result = json.loads(stdout.strip())
            return jsonify(result)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误：{str(e)}")
            logger.error(f"原始输出：{stdout}")
            return jsonify({
                'success': False,
                'message': f'导出失败：数据格式错误'
            }), 500

    except Exception as e:
        logger.error(f"导出过程出错：{str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导出失败：{str(e)}'
        }), 500