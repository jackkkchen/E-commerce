from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///factory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义数据模型
class ProductionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    product_code = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    popularity = db.Column(db.String(20), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    wholesale_price = db.Column(db.Float, nullable=False)
    base_cost = db.Column(db.Float, nullable=False)
    default_supplier = db.Column(db.String(50), nullable=False)
    default_warehouse = db.Column(db.String(50), nullable=False)
    production = db.Column(db.Integer, nullable=False)
    sales = db.Column(db.Integer, nullable=False)
    inventory = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 商品分类模型
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.String(20), primary_key=True)  # 分类编码
    name = db.Column(db.String(100), nullable=False)  # 分类名称
    parent_id = db.Column(db.String(20), db.ForeignKey('product_category.id'))  # 父级分类
    level = db.Column(db.Integer, default=1)  # 层级
    sort_order = db.Column(db.Integer, default=0)  # 排序
    status = db.Column(db.String(20), default='正常')  # 状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立自引用关系
    children = db.relationship('ProductCategory', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    # 关联商品
    products = db.relationship('Product', backref='category', lazy='dynamic')

# 商品信息模型
class Product(db.Model):
    __tablename__ = 'product'
    code = db.Column(db.String(20), primary_key=True)  # 商品编码
    name = db.Column(db.String(100), nullable=False)  # 商品名称
    category_id = db.Column(db.String(20), db.ForeignKey('product_category.id'))  # 分类ID
    model = db.Column(db.String(50))  # 规格型号
    wholesale_price = db.Column(db.Float, default=0)  # 基准批发价
    unit = db.Column(db.String(20))  # 计量单位
    status = db.Column(db.String(20), default='正常')  # 状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 路由：首页
@app.route('/')
def home():
    return render_template('home.html')

# 添加数据录入页面路由
@app.route('/entry')
def entry():
    return render_template('index.html')

# 路由：获取产品列表
@app.route('/get_products')
def get_products():
    try:
        # 从CSV文件读取完整的产品信息
        if os.path.exists('tv_screen_data.csv'):
            df = pd.read_csv('tv_screen_data.csv')
            # 获取唯一的产品信息
            products = df[['product_code', 'product_name', 'category', 'size', 
                         'model', 'wholesale_price', 'base_cost', 
                         'default_supplier', 'default_warehouse']].drop_duplicates().to_dict('records')
            
            # 返回完整的产品信息
            return jsonify([{
                'code': p['product_code'],
                'name': f"{p['product_code']} - {p['product_name']} ({p['size']})",
                'category': p['category'],
                'size': p['size'],
                'model': p['model'],
                'wholesale_price': p['wholesale_price'],
                'base_cost': p['base_cost'],
                'default_supplier': p['default_supplier'],
                'default_warehouse': p['default_warehouse']
            } for p in products])
        else:
            return jsonify({'status': 'error', 'message': '找不到产品数据文件'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 路由：数据录入
@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        data = request.json
        # 获取产品基本信息
        existing_product = ProductionRecord.query.filter_by(
            product_code=data['product_code']
        ).first()
        
        if not existing_product:
            return jsonify({'status': 'error', 'message': '产品不存在'})
        
        # 创建新记录
        record = ProductionRecord(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            product_code=data['product_code'],
            category=existing_product.category,
            popularity=existing_product.popularity,
            size=existing_product.size,
            model=existing_product.model,
            product_name=existing_product.product_name,
            wholesale_price=existing_product.wholesale_price,
            base_cost=existing_product.base_cost,
            default_supplier=existing_product.default_supplier,
            default_warehouse=existing_product.default_warehouse,
            production=int(data['production']),
            sales=int(data['sales']),
            inventory=int(data['inventory'])
        )
        
        db.session.add(record)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 路由：获取记录
@app.route('/get_records')
def get_records():
    records = ProductionRecord.query.order_by(ProductionRecord.date.desc()).limit(100).all()
    return jsonify([{
        'date': record.date.strftime('%Y-%m-%d'),
        'product_code': record.product_code,
        'category': record.category,
        'popularity': record.popularity,
        'size': record.size,
        'model': record.model,
        'product_name': record.product_name,
        'wholesale_price': record.wholesale_price,
        'base_cost': record.base_cost,
        'default_supplier': record.default_supplier,
        'default_warehouse': record.default_warehouse,
        'production': record.production,
        'sales': record.sales,
        'inventory': record.inventory
    } for record in records])

# 路由：导入数据
@app.route('/import_data', methods=['POST'])
def import_data():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '未选择文件'})

        # 读取文件内容
        df = pd.read_csv(file)
        
        # 导入数据到数据库
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                record = ProductionRecord(
                    date=pd.to_datetime(row['date']).date(),
                    product_code=row['product_code'],
                    category=row['category'],
                    popularity=row['popularity'],
                    size=row['size'],
                    model=row['model'],
                    product_name=row['product_name'],
                    wholesale_price=float(row['wholesale_price']),
                    base_cost=float(row['base_cost']),
                    default_supplier=row['default_supplier'],
                    default_warehouse=row['default_warehouse'],
                    production=int(row['production']),
                    sales=int(row['sales']),
                    inventory=int(row['inventory'])
                )
                db.session.add(record)
                success_count += 1
            except Exception as e:
                error_count += 1
                continue

        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'成功导入 {success_count} 条记录，失败 {error_count} 条'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 添加新的仪表板路由
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 获取销售趋势数据
@app.route('/api/sales_trend')
def sales_trend():
    # 获取最近30天的销售趋势
    query = """
    SELECT 
        date,
        SUM(sales) as total_sales,
        SUM(sales * wholesale_price) as revenue,
        SUM(production) as total_production,
        SUM(inventory) as total_inventory
    FROM production_record
    GROUP BY date
    ORDER BY date DESC
    LIMIT 30
    """
    df = pd.read_sql(query, db.engine)
    return df.to_json(orient='records')

# 获取产品类别分析
@app.route('/api/category_analysis')
def category_analysis():
    query = """
    SELECT 
        category,
        popularity,
        COUNT(*) as product_count,
        SUM(sales) as total_sales,
        SUM(sales * wholesale_price) as total_revenue,
        SUM(sales * (wholesale_price - base_cost)) as total_profit
    FROM production_record
    GROUP BY category, popularity
    """
    df = pd.read_sql(query, db.engine)
    return df.to_json(orient='records')

# 获取库存状态
@app.route('/api/inventory_status')
def inventory_status():
    query = """
    SELECT 
        product_code,
        product_name,
        category,
        SUM(inventory) as current_inventory,
        AVG(sales) as avg_daily_sales
    FROM production_record
    GROUP BY product_code, product_name, category
    """
    df = pd.read_sql(query, db.engine)
    return df.to_json(orient='records')

# 添加获取关键指标的路由
@app.route('/api/key_metrics')
def key_metrics():
    try:
        query = """
        SELECT 
            SUM(sales * wholesale_price) as total_revenue,
            SUM(sales * (wholesale_price - base_cost)) as total_profit,
            SUM(inventory) as total_inventory,
            COUNT(DISTINCT product_code) as product_count
        FROM production_record
        """
        df = pd.read_sql(query, db.engine)
        metrics = df.to_dict('records')[0]
        
        # 格式化数字
        metrics['total_revenue'] = f"¥{metrics['total_revenue']:,.2f}"
        metrics['total_profit'] = f"¥{metrics['total_profit']:,.2f}"
        metrics['total_inventory'] = f"{metrics['total_inventory']:,}"
        metrics['product_count'] = f"{metrics['product_count']}"
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)})

# 商品管理相关路由
@app.route('/products')
def products():
    return render_template('products.html')

# 获取商品分类
@app.route('/api/categories')
def get_categories():
    try:
        categories = ProductCategory.query.order_by(ProductCategory.sort_order).all()
        result = []
        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id,
                'level': category.level,
                'sort_order': category.sort_order,
                'status': category.status
            })
        return jsonify(result)
    except Exception as e:
        print('Error loading categories:', str(e))
        return jsonify({'error': str(e)})

# 搜索商品
@app.route('/api/products/search')
def search_products():
    try:
        search_text = request.args.get('q', '')
        category_id = request.args.get('category', '')
        
        query = Product.query
        
        # 应用搜索条件
        if search_text:
            query = query.filter(
                db.or_(
                    Product.code.contains(search_text),
                    Product.name.contains(search_text)
                )
            )
        
        # 应用分类筛选（包括子分类）
        if category_id:
            category = ProductCategory.query.get(category_id)
            if category:
                # 获取所有子分类ID
                category_ids = [category_id]
                for child in category.children.all():
                    category_ids.append(child.id)
                query = query.filter(Product.category_id.in_(category_ids))
        
        products = query.all()
        result = []
        for product in products:
            result.append({
                'code': product.code,
                'name': product.name,
                'model': product.model or '',
                'wholesale_price': float(product.wholesale_price or 0),
                'unit': product.unit or '',
                'status': product.status or '正常'
            })
        
        return jsonify(result)
    except Exception as e:
        print('Error:', str(e))
        return jsonify({'error': str(e)})

# 导入分类
@app.route('/api/categories/import', methods=['POST'])
def import_categories():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '未选择文件'})

        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 清空现有分类
        ProductCategory.query.delete()
        
        # 按层级顺序导入分类
        for _, row in df.iterrows():
            category = ProductCategory(
                id=str(row['分类编码']),
                name=str(row['分类名称']),
                parent_id=str(row['上级分类']) if pd.notna(row['上级分类']) else None,
                level=int(row['层级']) if '层级' in df.columns else 1,
                sort_order=int(row['排序']) if '排序' in df.columns else 0,
                status=str(row['状态']) if '状态' in df.columns else '正常'
            )
            db.session.add(category)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '分类导入成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 导入商品
@app.route('/api/products/import', methods=['POST'])
def import_products():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '未选择文件'})

        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 清空现有商品
        Product.query.delete()
        
        # 导入商品数据
        for _, row in df.iterrows():
            product = Product(
                code=str(row['商品编码']),
                name=str(row['商品名称']),
                category_id=str(row['分类编码']),
                model=str(row.get('规格型号', '')),
                wholesale_price=float(row.get('基准批发价', 0)),
                unit=str(row.get('计量单位', '')),
                status=str(row.get('状态', '正常'))
            )
            db.session.add(product)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '商品导入成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 导出分类
@app.route('/api/categories/export')
def export_categories():
    try:
        if os.path.exists('商品分类.xlsx'):
            return send_file(
                '商品分类.xlsx',
                as_attachment=True,
                download_name='商品分类.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        return jsonify({'status': 'error', 'message': '没有分类数据'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# 导出商品
@app.route('/api/products/export')
def export_products():
    try:
        if os.path.exists('商品.xlsx'):
            return send_file(
                '商品.xlsx',
                as_attachment=True,
                download_name='商品.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        return jsonify({'status': 'error', 'message': '没有商品数据'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 