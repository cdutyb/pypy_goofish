<template>
  <div class="ai-filter-panel">
    <h3>AI 智能筛选</h3>

    <!-- 筛选输入框 -->
    <div class="filter-input">
      <input
        v-model="userQuery"
        @keyup.enter="sendQuery"
        placeholder="描述您需要的商品特点..."
        :disabled="isProcessing"
      />
      <button @click="sendQuery" :disabled="isProcessing || !userQuery">
        {{ isProcessing ? '处理中...' : '筛选' }}
      </button>
      <button @click="resetFilter" :disabled="isProcessing">重置</button>
    </div>

    <!-- 展示AI回复 -->
    <div v-if="aiResponse" class="ai-response">
      <p><strong>AI助手:</strong> {{ aiResponse }}</p>
      <p v-if="filterReason" class="filter-reason">
        <strong>筛选原因:</strong> {{ filterReason }}
      </p>
    </div>

    <!-- 筛选结果统计 -->
    <div v-if="filteredProducts.length > 0" class="filter-stats">
      <p>
        匹配 {{ filteredProducts.length }} 件商品
        <span v-if="rawProducts.length !== filteredProducts.length">
          (从 {{ rawProducts.length }} 件商品中)
        </span>
      </p>
    </div>

    <!-- 推荐筛选条件 -->
    <div v-if="suggestedFilters.length > 0" class="suggested-filters">
      <p><strong>推荐筛选条件:</strong></p>
      <div class="filter-tags">
        <div
          v-for="(filter, index) in suggestedFilters"
          :key="index"
          class="filter-tag"
          @click="applyFilter(filter)"
        >
          {{ filter }}
        </div>
      </div>
    </div>

    <!-- 筛选历史 -->
    <div v-if="filterHistory.length > 0" class="filter-history">
      <p><strong>筛选历史:</strong></p>
      <div class="history-items">
        <div
          v-for="(item, index) in filterHistory"
          :key="index"
          class="history-item"
          @click="applyFilter(item)"
        >
          {{ item }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AiFilterPanel',
  props: {
    rawProducts: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      userQuery: '',
      aiResponse: '',
      filterReason: '',
      filteredProducts: [],
      suggestedFilters: [],
      filterHistory: [],
      sessionId: null,
      isProcessing: false
    };
  },
  mounted() {
    // 初始化时显示所有已经过语义过滤的商品
    this.filteredProducts = [...this.rawProducts];
    this.sessionId = this.generateSessionId();
  },
  watch: {
    // 监听原始商品数据变化，重置筛选
    rawProducts: {
      handler(newProducts) {
        this.resetFilterState();
        this.filteredProducts = [...newProducts];
      },
      deep: true
    }
  },
  methods: {
    async sendQuery() {
      if (!this.userQuery || this.isProcessing) return;

      this.isProcessing = true;

      try {
        const response = await axios.post('http://localhost:8000/chat', {
          query: this.userQuery,
          session_id: this.sessionId
        });

        // 更新状态
        this.aiResponse = response.data.response;
        this.filterReason = response.data.filter_reason;
        this.filteredProducts = response.data.filtered_products;
        this.suggestedFilters = response.data.suggested_filters || [];

        // 添加到筛选历史
        if (!this.filterHistory.includes(this.userQuery)) {
          this.filterHistory.unshift(this.userQuery);
          // 最多保留5条历史记录
          if (this.filterHistory.length > 5) {
            this.filterHistory.pop();
          }
        }

        // 向父组件发送筛选后的商品数据
        this.$emit('update-products', this.filteredProducts);

        // 清空查询输入框
        this.userQuery = '';
      } catch (error) {
        console.error('AI筛选请求失败:', error);
        alert('AI筛选失败，请重试');
      } finally {
        this.isProcessing = false;
      }
    },

    applyFilter(filter) {
      this.userQuery = filter;
      this.sendQuery();
    },

    resetFilter() {
      this.resetFilterState();
      this.filteredProducts = [...this.rawProducts];
      this.$emit('update-products', this.filteredProducts);
    },

    resetFilterState() {
      this.userQuery = '';
      this.aiResponse = '';
      this.filterReason = '';
      this.suggestedFilters = [];
    },

    generateSessionId() {
      // 生成简单的随机会话ID
      return 'session_' + Math.random().toString(36).substring(2, 15);
    }
  }
}
</script>

<style scoped>
.ai-filter-panel {
  width: 300px;
  padding: 15px;
  margin-right: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

h3 {
  margin-top: 0;
  text-align: center;
  color: #333;
}

.filter-input {
  display: flex;
  margin-bottom: 15px;
}

.filter-input input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 5px;
}

.filter-input button {
  padding: 6px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 5px;
  white-space: nowrap;
}

.filter-input button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.ai-response {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f0f8ff;
  border-radius: 4px;
  border-left: 4px solid #1e88e5;
}

.filter-reason {
  font-size: 0.9em;
  color: #666;
}

.filter-stats {
  margin-bottom: 15px;
  color: #333;
}

.suggested-filters, .filter-history {
  margin-top: 15px;
  margin-bottom: 15px;
}

.filter-tags, .history-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag, .history-item {
  padding: 6px 12px;
  background-color: #e0e0e0;
  border-radius: 16px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tag:hover, .history-item:hover {
  background-color: #d0d0d0;
}

.filter-tag {
  background-color: #e3f2fd;
  color: #1976d2;
}

.filter-tag:hover {
  background-color: #bbdefb;
}

.history-item {
  background-color: #f5f5f5;
  color: #616161;
}

.history-item:hover {
  background-color: #eeeeee;
}
</style>