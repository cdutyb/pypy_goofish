<template>
  <div class="app">
    <!-- 页面顶部标题 -->
    <h1>商品爬取展示</h1>

    <!-- 输入区域 -->
    <div class="input-section">
      <label for="product-name">商品名称:</label>
      <input
        id="product-name"
        v-model="productName"
        placeholder="请输入商品名称"
      />

      <label for="page-count">爬取页数:</label>
      <input
        id="page-count"
        v-model.number="pageCount"
        type="number"
        placeholder="请输入页数"
      />

      <button @click="startScraping" :disabled="isLoading">
        {{ isLoading ? '爬取中...' : '开始' }}
      </button>
    </div>

    <!-- 主内容区域 -->
    <div class="content-container" v-if="products.length > 0">
      <!-- AI过滤面板 -->
      <ai-filter-panel
        @update-products="updateDisplayedProducts"
        :raw-products="products"
      ></ai-filter-panel>

      <!-- 表格展示区域 -->
      <div class="table-section">
        <h2>展示结果 ({{ displayedProducts.length }}件商品)</h2>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>商品名称</th>
              <th>价格</th>
              <th>商品链接</th>
              <th>卖家地址</th>
              <th>卖家ID</th>
              <th>商品标签</th>
              <th>想要人数</th>
              <th>图片链接</th>
              <th>是否包邮</th>
              <th>评价数</th>
              <th>好评率</th>
              <th>综合评分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(product, index) in displayedProducts" :key="index">
              <td>{{ product['序号'] }}</td>
              <td>{{ product['商品名称'] }}</td>
              <td>{{ product['价格'] }}</td>
              <td><a :href="product['商品链接']" target="_blank">链接</a></td>
              <td>{{ product['卖家地址'] }}</td>
              <td>{{ product['卖家ID'] }}</td>
              <td>{{ product['商品标签'] }}</td>
              <td>{{ product['想要人数'] }}</td>
              <td>
                <a :href="product['图片链接']" target="_blank">
                  <img :src="product['图片链接']" alt="商品图片" width="100" />
                </a>
              </td>
              <td>{{ product['是否包邮'] }}</td>
              <td>{{ product['评价数'] }}</td>
              <td>{{ product['好评率'] }}</td>
              <td>{{ formatRating(product['综合评分']) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- 分页控制 -->
        <div class="pagination">
          <button @click="changePage(page - 1)" :disabled="page <= 1">上一页</button>

          <!-- 页码选择器 -->
          <select v-model="page" @change="loadPageData(page)">
            <option v-for="n in totalPages" :key="n" :value="n">{{ n }}</option>
          </select>

          <span>当前页: {{ page }} / {{ totalPages }}</span>
          <button @click="changePage(page + 1)" :disabled="page >= totalPages">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import AiFilterPanel from "./components/AiFilterPanel.vue";

export default {
  name: "App",
  components: {
    AiFilterPanel
  },
  data() {
    return {
      productName: "",       // 商品名称
      pageCount: 1,          // 爬取页数
      page: 1,               // 当前页
      pageSize: 30,          // 每页商品数量
      products: [],          // 存储爬取结果（原始已过滤数据）
      displayedProducts: [], // 当前展示的商品（可能经过AI筛选）
      totalPages: 0,         // 总页数
      totalItems: 0,         // 总商品数
      isLoading: false       // 加载状态
    };
  },
  methods: {
    async startScraping() {
      if (!this.productName || this.pageCount < 1) {
        alert("请输入有效的商品名称和页数！");
        return;
      }

      this.isLoading = true;

      try {
        const response = await axios.post("http://localhost:8000/cp", {
          keyword: this.productName,
          pages: this.pageCount,
        });

        // 设置分页数据
        this.totalPages = response.data.totalPages;
        this.totalItems = response.data.totalPages * this.pageSize;

        // 加载第一页数据
        this.page = 1;
        await this.loadPageData(this.page);
      } catch (error) {
        console.error("爬取失败:", error);
        alert("爬取失败，请检查后端服务或输入内容！");
      } finally {
        this.isLoading = false;
      }
    },

    // 加载指定页的数据（后端已进行语义过滤）
    async loadPageData(page) {
      try {
        const response = await axios.get(`http://localhost:8000/page?page=${page}`);
        this.products = response.data.data || [];
        this.displayedProducts = [...this.products]; // 初始显示全部过滤后的商品
      } catch (error) {
        console.error("加载分页数据失败:", error);
        alert("加载分页数据失败，请重试！");
      }
    },

    // 更新显示的商品数据（来自AI筛选结果）
    updateDisplayedProducts(filteredProducts) {
      this.displayedProducts = filteredProducts;
    },

    // 切换页面
    changePage(newPage) {
      if (newPage > 0 && newPage <= this.totalPages) {
        this.page = newPage;
        this.loadPageData(this.page);
      }
    },

    // 格式化评分，保留两位小数
    formatRating(rating) {
      return parseFloat(rating).toFixed(2);
    },
  },
};
</script>

<style scoped>
.app {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
}

.input-section {
  margin-bottom: 20px;
  text-align: center;
}

.input-section label {
  margin-right: 10px;
}

.input-section input {
  margin-right: 10px;
  padding: 5px;
  width: 150px;
}

.input-section button {
  padding: 5px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-section button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.input-section button:not(:disabled):hover {
  background-color: #45a049;
}

.content-container {
  display: flex;
  margin-top: 20px;
}

.table-section {
  flex-grow: 1;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th, table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

table th {
  background-color: #f2f2f2;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.pagination button {
  padding: 5px 10px;
  margin: 0 5px;
}

.pagination select {
  padding: 5px;
  margin: 0 5px;
}

.pagination span {
  margin: 0 10px;
}
</style>