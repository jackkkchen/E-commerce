from flask import Flask
import os

# 获取模板和静态文件的绝对路径
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

# 创建 Flask 应用实例
app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir)

# 导入路由
from app import routes