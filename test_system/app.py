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
    id = db.Column(db.String(20), primary_key=True)  # 分类编码，如 '0570'
    name = db.Column(db.String(100), nullable=False)  # 分类名称
    parent_id = db.Column(db.String(20), db.ForeignKey('product_category.id'))  # 父级分类ID
    level = db.Column(db.Integer, default=1)  # 层级，1表示第一层
    sort_order = db.Column(db.Integer, default=0)  # 排序号
    status = db.Column(db.String(20), default='正常')
    
    # 建立自引用关系，用于获取子分类
    children = db.relationship(
        'ProductCategory',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )
    
    # 关联商品
    products = db.relationship('Product', backref='category', lazy='dynamic')

# 商品信息模型
class Product(db.Model):
    __tablename__ = 'product'
    code = db.Column(db.String(20), primary_key=True)         # 商品编码
    name = db.Column(db.String(100), nullable=False)          # 商品名称
    category_id = db.Column(db.String(20), db.ForeignKey('product_category.id'))  # 关联分类ID
    unit = db.Column(db.String(20))                          # 计量单位
    wholesale_price = db.Column(db.Float, nullable=True)      # 基准批发价
    model = db.Column(db.String(100))                        # 规格型号
    base_cost = db.Column(db.Float, nullable=True)           # 参考成本
    default_supplier = db.Column(db.String(100))             # 默认供应商
    default_warehouse = db.Column(db.String(100))            # 默认仓库
    status = db.Column(db.String(20), default='正常')

    def __repr__(self):
        return f'<Product {self.code}: {self.name}>'

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
        parent_id = request.args.get('parent', None)
        query = ProductCategory.query
        
        if parent_id:
            # 获取特定父级的子分类
            query = query.filter_by(parent_id=parent_id)
        else:
            # 获取顶级分类（没有上级分类的）
            query = query.filter(
                db.or_(
                    ProductCategory.parent_id.is_(None),
                    ProductCategory.parent_id == ''
                )
            )
        
        categories = query.order_by(ProductCategory.id).all()
        result = []
        
        for category in categories:
            # 检查是否有子分类
            has_children = ProductCategory.query.filter_by(parent_id=category.id).count() > 0
            
            result.append({
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id,
                'has_children': has_children  # 添加这个标志来控制是否显示箭头
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
        
        # 应用分类筛选
        if category_id:
            category = ProductCategory.query.get(category_id)
            if category:
                # 获取当前分类及其所有子分类
                category_ids = [category_id]
                category_names = [category.name]
                
                # 获取所有子分类
                children = ProductCategory.query.filter_by(parent_id=category_id).all()
                for child in children:
                    category_ids.append(child.id)
                    category_names.append(child.name)
                
                # 使用分类名称筛选商品
                query = query.filter(Product.category_id.in_(category_ids))
        
        products = query.all()
        result = []
        for product in products:
            # 获取商品的分类名称
            category = ProductCategory.query.get(product.category_id)
            category_name = category.name if category else ''
            
            result.append({
                'code': product.code,
                'name': product.name,
                'category': category_name,  # 添加分类名称
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
        try:
            df = pd.read_excel(file)
            print("Excel文件读取成功，数据预览:")
            print(df.head())
            print("\n列名:", df.columns.tolist())
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Excel文件读取失败: {str(e)}'})

        # 清空现有商品
        Product.query.delete()
        
        # 获取所有分类的映射
        categories = {cat.name: cat.id for cat in ProductCategory.query.all()}
        
        # 导入商品数据
        success_count = 0
        error_records = []
        
        for index, row in df.iterrows():
            try:
                # 处理分类
                category_name = str(row['商品分类']) if pd.notna(row['商品分类']) else None
                if category_name and category_name in categories:
                    category_id = categories[category_name]
                else:
                    error_records.append(f"行 {index + 2}: 分类 '{category_name}' 不存在")
                    continue

                # 创建商品记录
                product = Product(
                    code=str(row['商品编码']),
                    name=str(row['商品名称']),
                    category_id=category_id,
                    unit=str(row['计量单位']) if pd.notna(row['计量单位']) else None,
                    wholesale_price=float(row['基准批发价']) if pd.notna(row['基准批发价']) else None,
                    model=str(row['规格型号']) if pd.notna(row['规格型号']) else None,
                    base_cost=float(row['参考成本']) if pd.notna(row['参考成本']) else None,
                    default_supplier=str(row['默认供应商']) if pd.notna(row['默认供应商']) else None,
                    default_warehouse=str(row['默认仓库']) if pd.notna(row['默认仓库']) else None,
                    status='正常'
                )
                
                db.session.add(product)
                success_count += 1
                
            except Exception as e:
                error_records.append(f"行 {index + 2}: {str(e)}")
                print(f"错误详情: {str(e)}")  # 添加详细错误日志
        
        try:
            db.session.commit()
            message = f"成功导入 {success_count} 个商品"
            if error_records:
                message += f"\n\n导入错误:\n" + "\n".join(error_records)
            return jsonify({'status': 'success', 'message': message})
        except Exception as e:
            db.session.rollback()
            print(f"提交错误: {str(e)}")  # 添加详细错误日志
            return jsonify({'status': 'error', 'message': f'数据库提交失败: {str(e)}'})
            
    except Exception as e:
        print(f"导入错误: {str(e)}")  # 添加详细错误日志
        return jsonify({'status': 'error', 'message': f'导入失败: {str(e)}'})

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

# 清空所有分类
@app.route('/api/categories/clear', methods=['POST'])
def clear_categories():
    try:
        # 先删除所有商品（因为有外键关联）
        Product.query.delete()
        # 再删除所有分类
        ProductCategory.query.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': '所有分类已清空'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 添加单个分类
@app.route('/api/categories/add', methods=['POST'])
def add_category():
    try:
        data = request.json
        category = ProductCategory(
            id=data['id'],
            name=data['name'],
            parent_id=data.get('parent_id'),
            level=data.get('level', 1),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', '正常')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '分类添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 删除分类
@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        # 检查是否有子分类
        if ProductCategory.query.filter_by(parent_id=category_id).first():
            return jsonify({'status': 'error', 'message': '请先删除子分类'})
        
        # 检查是否有关联商品
        if Product.query.filter_by(category_id=category_id).first():
            return jsonify({'status': 'error', 'message': '请先移除该分类下的商品'})
        
        category = ProductCategory.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return jsonify({'status': 'success', 'message': '分类删除成功'})
        return jsonify({'status': 'error', 'message': '分类不存在'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 添加新增商品的API
@app.route('/api/products/add', methods=['POST'])
def add_product():
    try:
        data = request.json
        
        # 验证分类是否存在
        category = ProductCategory.query.filter_by(name=data['category']).first()
        if not category:
            return jsonify({'status': 'error', 'message': '商品分类不存在'})
        
        product = Product(
            code=data['code'],
            name=data['name'],
            category_id=category.id,
            unit=data['unit'],
            wholesale_price=float(data['wholesale_price']),
            model=data.get('model', ''),
            base_cost=float(data.get('base_cost', 0)),
            default_supplier=data.get('default_supplier', ''),
            default_warehouse=data.get('default_warehouse', ''),
            status='正常'
        )
        
        db.session.add(product)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '商品添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 删除商品
@app.route('/api/products/<product_code>', methods=['DELETE'])
def delete_product(product_code):
    try:
        product = Product.query.get(product_code)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'status': 'success', 'message': '商品删除成功'})
        return jsonify({'status': 'error', 'message': '商品不存在'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 