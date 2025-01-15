from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # 建立父子关系
    children = db.relationship('Category', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    # 关联产品
    products = db.relationship('Product', backref='category_rel', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    specifications = db.Column(db.String(200))
    unit = db.Column(db.String(20))
    base_price = db.Column(db.Float)
    reference_cost = db.Column(db.Float)
    default_supplier = db.Column(db.String(100))
    default_warehouse = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 