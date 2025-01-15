from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Product, Category
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return redirect(url_for('products'))

@app.route('/products')
def products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories)

@app.route('/products/add', methods=['POST'])
def add_product():
    try:
        data = request.form
        product = Product(
            product_code=data['product_code'],
            product_name=data['product_name'],
            category_id=data.get('category_id'),
            specifications=data['specifications'],
            unit=data['unit'],
            base_price=float(data['base_price']),
            model_number=data['model_number']
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/categories')
def get_categories():
    """获取第一层分类（没有父级的分类）"""
    root_categories = Category.query.filter_by(parent_id=None).order_by(Category.code).all()
    return jsonify([{
        'id': cat.id,
        'code': cat.code,
        'name': cat.name,
        'has_children': cat.children.count() > 0
    } for cat in root_categories])

@app.route('/categories/<int:parent_id>/children')
def get_subcategories(parent_id):
    """获取指定父级的子分类"""
    categories = Category.query.filter_by(parent_id=parent_id).order_by(Category.code).all()
    return jsonify([{
        'id': cat.id,
        'code': cat.code,
        'name': cat.name,
        'has_children': cat.children.count() > 0
    } for cat in categories])

@app.route('/products/by_category/<int:category_id>')
def get_products_by_category(category_id):
    """获取指定分类及其子分类下的所有商品"""
    # 获取当前分类及其所有子分类的ID
    category = Category.query.get_or_404(category_id)
    
    def get_all_child_ids(cat):
        ids = [cat.id]
        for child in cat.children:
            ids.extend(get_all_child_ids(child))
        return ids
    
    category_ids = get_all_child_ids(category)
    
    # 获取这些分类下的所有商品
    products = Product.query.filter(Product.category_id.in_(category_ids)).all()
    
    return jsonify([{
        'id': p.id,
        'product_code': p.product_code,
        'product_name': p.product_name,
        'category_name': p.category_rel.name if p.category_rel else '',  # 添加分类名称
        'unit': p.unit,
        'base_price': p.base_price,
        'specifications': p.specifications,
        'reference_cost': p.reference_cost,
        'default_supplier': p.default_supplier,
        'default_warehouse': p.default_warehouse
    } for p in products])

if __name__ == '__main__':
    app.run(debug=True) 