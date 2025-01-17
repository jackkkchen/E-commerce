document.addEventListener('DOMContentLoaded', function() {
    setupTreeView();
    addStyles();
});

function setupTreeView() {
    // 获取所有带有 caret 类的元素
    var toggler = document.getElementsByClassName("caret");
    
    // 初始化时关闭所有子菜单
    var allNested = document.getElementsByClassName("nested");
    for (var i = 0; i < allNested.length; i++) {
        allNested[i].classList.remove("active");
    }
    
    // 移除所有 caret-down 类
    for (var i = 0; i < toggler.length; i++) {
        toggler[i].classList.remove("caret-down");
    }

    // 为每个 caret 元素添加点击事件
    for (var i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            
            // 获取当前点击的分类名称
            var categoryName = this.getAttribute("data-category");
            
            // 切换当前节点的展开/收起状态
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("caret-down");
            
            // 更新表格内容
            if (categoryName) {
                updateTableContent(categoryName);
                
                // 移除其他分类的选中状态
                var allItems = document.querySelectorAll('.caret, .no-caret');
                allItems.forEach(item => item.classList.remove('selected'));
                
                // 添加当前分类的选中状态
                this.classList.add('selected');
            }
        });
    }

    // 为叶子节点添加点击事件
    var leafNodes = document.getElementsByClassName("no-caret");
    for (var i = 0; i < leafNodes.length; i++) {
        leafNodes[i].addEventListener("click", function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            
            var categoryName = this.getAttribute("data-category");
            if (categoryName) {
                updateTableContent(categoryName);
                
                // 移除其他分类的选中状态
                var allItems = document.querySelectorAll('.caret, .no-caret');
                allItems.forEach(item => item.classList.remove('selected'));
                
                // 添加当前分类的选中状态
                this.classList.add('selected');
            }
        });
    }
}

function updateTableContent(categoryName) {
    const table = document.getElementById('inventory-table');
    const tableBody = table.querySelector('tbody');
    
    // 显示加载状态
    tableBody.innerHTML = '<tr><td colspan="9" class="loading">数据加载中...</td></tr>';
    
    fetch('/generate_view', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category_name: categoryName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || '获取数据失败');
        }
        
        // 清空表格内容
        tableBody.innerHTML = '';
        
        // 检查是否有数据
        if (!data.data || data.data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="9" class="empty">没有找到相关数据</td></tr>';
            return;
        }

        // 添加数据行
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row['商品编码'] || ''}</td>
                <td>${row['商品名称'] || ''}</td>
                <td>${row['商品分类'] || ''}</td>
                <td>${row['规格型号'] || ''}</td>
                <td>${row['计量单位'] || ''}</td>
                <td>${row['基准批发价'] || ''}</td>
                <td>${row['参考成本'] || ''}</td>
                <td>${row['默认供应商'] || ''}</td>
                <td>${row['默认仓库'] || ''}</td>
            `;
            tableBody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="error">
                    加载失败: ${error.message}
                </td>
            </tr>`;
    });
}

function updateTableHeader(table, columns) {
    if (!columns || columns.length === 0) {
        console.warn('No columns provided');
        return;
    }
    
    const thead = table.querySelector('thead');
    thead.innerHTML = '<tr>' + 
        columns.map(col => `<th>${col}</th>`).join('') +
        '<th>操作</th></tr>';
}

function updateTableBody(tableBody, data) {
    if (!data || data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="empty">没有找到相关数据</td></tr>';
        return;
    }

    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        // 添加数据列
        Object.values(row).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value !== null ? value : '';
            tr.appendChild(td);
        });
        
        // 添加操作列
        const actionTd = document.createElement('td');
        actionTd.innerHTML = `
            <button onclick="editItem('${row[Object.keys(row)[0]]}')">编辑</button>
            <button onclick="deleteItem('${row[Object.keys(row)[0]]}')">删除</button>
        `;
        tr.appendChild(actionTd);
        
        tableBody.appendChild(tr);
    });
}

// 添加一些基本的样式
function addStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .edit-btn, .delete-btn {
            margin: 0 5px;
            padding: 3px 8px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .edit-btn {
            background-color: #4CAF50;
            color: white;
        }
        .delete-btn {
            background-color: #f44336;
            color: white;
        }
        .loading, .error, .empty {
            text-align: center;
            padding: 20px;
        }
        .error { color: #f44336; }
        .loading, .empty { color: #666; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
            white-space: nowrap;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }
        .tree-view {
            margin: 20px;
            font-family: Arial, sans-serif;
        }

        .tree-view ul {
            list-style-type: none;
            padding-left: 20px;
            margin: 0;
        }

        .caret, .no-caret {
            cursor: pointer;
            user-select: none;
            padding: 5px;
            display: block;
        }

        .caret::before {
            content: "▶";
            color: black;
            display: inline-block;
            margin-right: 6px;
            transition: transform 0.2s;
        }

        .caret-down::before {
            transform: rotate(90deg);
        }

        .nested {
            display: none;
        }

        .active {
            display: block;
        }

        .no-caret {
            padding-left: 25px;
        }

        .caret:hover, .no-caret:hover {
            background-color: #f0f0f0;
        }

        /* 选中状态的样式 */
        .selected {
            background-color: #e0e0e0;
        }
    `;
    document.head.appendChild(style);
}