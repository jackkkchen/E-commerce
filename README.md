# 项目结构
```
E-commerce/
├── data/
│   ├── product_cate.xlsx
│   └── product.xlsx
├── inventory_system/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── init_all.py
│   ├── init_categories.py
│   ├── init_products.py
│   └── templates/
│       └── products.html
├── .gitignore
└── README.md
```

添加 README.md 文件:

```markdown:README.md
# 库存管理系统

基于 Flask 的库存管理系统，支持商品分类管理和商品信息管理。

## 功能特点

- 多级商品分类管理
- 商品信息的增删改查
- Excel数据导入导出
- 分类树形展示
- 响应式界面设计

## 安装和运行

1. 克隆仓库:
```bash
git clone https://github.com/jackkkchen/E-commerce.git
cd E-commerce
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 初始化数据库:
```bash
cd inventory_system
python init_all.py
```

4. 运行应用:
```bash
python app.py
```

## 技术栈

- 后端: Flask + SQLAlchemy
- 前端: Bootstrap + JavaScript
- 数据库: SQLite
```


