document.addEventListener('DOMContentLoaded', function() {
    setupTreeView();
    setupTableHandlers();
    addStyles();
});

function setupTreeView() {
    var carets = document.getElementsByClassName('caret');
    for (var i = 0; i < carets.length; i++) {
        carets[i].addEventListener('click', function(e) {
            this.classList.toggle('caret-down');
            var nestedList = this.parentElement.querySelector('.nested');
            if (nestedList) {
                nestedList.classList.toggle('active');
            }
            updateTableContent(this.textContent.trim());
            e.stopPropagation();
        });
    }

    var noCarets = document.getElementsByClassName('no-caret');
    for (var i = 0; i < noCarets.length; i++) {
        noCarets[i].addEventListener('click', function() {
            updateTableContent(this.textContent.trim());
        });
    }
}

function updateTableContent(categoryName) {
    const table = document.getElementById('inventory-table');
    const tableBody = table.querySelector('tbody');
    
    // 显示加载状态
    tableBody.innerHTML = '<tr><td colspan="10" class="loading">数据加载中...</td></tr>';
    
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
        
        // 更新表格内容
        if (!data.data || data.data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="10" class="empty">没有找到相关数据</td></tr>';
            return;
        }

        // 清空表格内容
        tableBody.innerHTML = '';
        
        // 添加数据行
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.商品编码 || ''}</td>
                <td>${row.商品名称 || ''}</td>
                <td>${row.商品分类 || ''}</td>
                <td>${row.规格型号 || ''}</td>
                <td>${row.计量单位 || ''}</td>
                <td>${row.基准批发价 || ''}</td>
                <td>${row.参考成本 || ''}</td>
                <td>${row.默认供应商 || ''}</td>
                <td>${row.默认仓库 || ''}</td>
                <td>
                    <button class="edit-btn" onclick="editItem('${row.商品编码}')">编辑</button>
                    <button class="delete-btn" onclick="deleteItem('${row.商品编码}')">删除</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });

        // 更新表头
        const thead = table.querySelector('thead');
        thead.innerHTML = `
            <tr>
                <th>商品编码</th>
                <th>商品名称</th>
                <th>商品分类</th>
                <th>规格型号</th>
                <th>计量单位</th>
                <th>基准批发价</th>
                <th>参考成本</th>
                <th>默认供应商</th>
                <th>默认仓库</th>
                <th>操作</th>
            </tr>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="error">
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

// 编辑和删除功能的占位函数
function editItem(id) {
    console.log('编辑项目:', id);
    // TODO: 实现编辑功能
}

function deleteItem(id) {
    console.log('删除项目:', id);
    // TODO: 实现删除功能
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
    `;
    document.head.appendChild(style);
}