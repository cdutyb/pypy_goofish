let totalPages = 0;
let currentPage = 1;
let allData = [];

// 开始爬取商品数据
document.getElementById('crawlBtn').addEventListener('click', function() {
    const keyword = document.getElementById('keyword').value;
    const pages = document.getElementById('pages').value;

    if (keyword === '' || pages === '') {
        alert('请输入商品名称和页数');
        return;
    }

    const data = {
        keyword: keyword,
        pages: pages
    };

    // 显示爬取进度
    document.getElementById('console-output').style.display = 'block';
    document.getElementById('progress').innerText = '爬取开始...';

    // 禁用爬取按钮
    document.getElementById('crawlBtn').disabled = true;

    // 发送爬取请求
    fetch('/crawl', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('爬取失败');
        }
        return response.json();
    })
    .then(data => {
        totalPages = data.total_pages;
        allData = data.data;

        // 显示商品数据
        displayResults(allData);

        // 显示分页控件
        updatePagination();

        // 启用爬取按钮
        document.getElementById('crawlBtn').disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('爬取失败，请重试');
        document.getElementById('crawlBtn').disabled = false;
    });

});

// 显示商品数据
function displayResults(data) {
    const tableBody = document.getElementById('dataTable');
    tableBody.innerHTML = '';  // 清空表格

    // 显示商品数据
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${(currentPage - 1) * 30 + (index + 1)}</td> <!-- 序号 -->
            <td>${item['商品名称']}</td>
            <td>${item['价格']}</td>
            <td><a href="${item['商品链接']}" target="_blank">查看</a></td>
            <td>${item['卖家地址']}</td>
            <td>${item['卖家ID']}</td>
            <td>${item['商品标签']}</td>
            <td>${item['想要人数']}</td>
            <td><a href="${item['图片链接']}" target="_blank"><img src="${item['图片链接']}" width="50" alt="商品图片"></a></td>
            <td>${item['是否包邮']}</td>
            <td>${item['评价数']}</td>
            <td>${item['好评率']}</td>
        `;
        tableBody.appendChild(row);
    });
}

// 更新分页
function updatePagination() {
    const pageSelect = document.getElementById('pageSelect');
    pageSelect.innerHTML = '';  // 清空分页
    for (let i = 1; i <= totalPages; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.innerText = i;
        pageSelect.appendChild(option);
    }

    // 绑定分页按钮
    document.getElementById('prevPageBtn').disabled = currentPage <= 1;
    document.getElementById('nextPageBtn').disabled = currentPage >= totalPages;

    document.getElementById('prevPageBtn').onclick = goToPrevPage;
    document.getElementById('nextPageBtn').onclick = goToNextPage;
    pageSelect.onchange = goToPage;
}

// 翻页
function goToPrevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadPageData(currentPage);
    }
}

function goToNextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadPageData(currentPage);
    }
}

function goToPage() {
    currentPage = parseInt(document.getElementById('pageSelect').value);
    loadPageData(currentPage);
}

// 加载分页数据
function loadPageData(page) {
    fetch(`/page?page=${page}`)
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => console.error('Error loading page:', error));
}
