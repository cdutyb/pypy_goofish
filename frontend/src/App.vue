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

      <button @click="startScraping">开始</button>
    </div>

    <!-- 表格展示区域 -->
    <div v-if="products.length > 0" class="table-section">
      <h2>爬取结果</h2>
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
          </tr>
        </thead>
        <tbody>
          <tr v-for="(product, index) in products" :key="index">
            <td>{{ product['序号'] }}</td>
            <td>{{ product['商品名称'] }}</td>
            <td>{{ product['价格'] }}</td>
            <td><a :href="product['商品链接']" target="_blank">链接</a></td>
            <td>{{ product['卖家地址'] }}</td>
            <td>{{ product['卖家ID'] }}</td>
            <td>{{ product['商品标签'] }}</td>
            <td>{{ product['想要人数'] }}</td>
            <td><img :src="product['图片链接']" alt="商品图片" width="100" /></td>
            <td>{{ product['是否包邮'] }}</td>
            <td>{{ product['评价数'] }}</td>
            <td>{{ product['好评率'] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      productName: "", // 商品名称
      pageCount: 1,    // 爬取页数
      products: [],    // 存储爬取结果
    };
  },
  methods: {
    async startScraping() {
      if (!this.productName || this.pageCount < 1) {
        alert("请输入有效的商品名称和页数！");
        return;
      }

      try {
        // 调用后端 API 获取爬取数据
        const response = await axios.post("http://localhost:8000/cp", {
          keyword: this.productName,
          pages: this.pageCount,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
        );

        // 更新表格数据
        this.products = response.data || [];
      } catch (error) {
        console.error("爬取失败:", error);
        alert("爬取失败，请检查后端服务或输入内容！");
      }
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

.input-section button:hover {
  background-color: #45a049;
}

.table-section {
  margin-top: 20px;
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
</style>