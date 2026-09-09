<template>
  <view class="page">
    <decor-blocks app="sales-tracker" page-key="products" />

    <view class="page-head">
      <text class="page-title">商品库</text>
      <input class="search-input" v-model="query" placeholder="搜索名称/编码/底盘" />
    </view>

    <view class="login-prompt" v-if="!loggedIn">
      <text class="login-prompt-icon">🔒</text>
      <text class="login-prompt-title">登录后查看商品库</text>
      <button class="btn-primary login-prompt-btn" @click="goLogin">去登录</button>
    </view>
    <template v-else>
      <view class="empty-hint" v-if="!products.length">还没有商品</view>
      <view class="menu-layout" v-else>
        <scroll-view scroll-y class="menu-sidebar" v-if="!query.trim()">
          <view
            v-for="c in categoryTabs"
            :key="c.id"
            class="menu-sidebar-item"
            :class="{ active: activeCategoryId === c.id }"
            @click="selectCategory(c.id)"
          >{{ c.name }}</view>
        </scroll-view>
        <scroll-view scroll-y class="menu-products">
          <view class="empty-hint" v-if="!visibleProducts.length">
            {{ query.trim() ? '没有匹配的商品' : '这个分类还没有商品' }}
          </view>
          <view class="product-card" v-for="p in visibleProducts" :key="p.id" @click="goDetail(p.id)">
            <image
              v-if="p.main_image_urls && p.main_image_urls.length"
              class="product-image"
              :src="staticUrl(p.main_image_urls[0])"
              mode="aspectFill"
            ></image>
            <view v-else class="product-image placeholder">暂无主图</view>
            <view class="product-body">
              <text class="product-name">{{ p.name }}</text>
              <text class="product-code" v-if="p.internal_code">编码：{{ p.internal_code }}</text>
              <text class="product-price" v-if="p.price">¥{{ formatNum(p.price) }}</text>
              <text class="product-chassis" v-if="p.chassis_info">{{ p.chassis_info }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </template>

    <tab-bar current="/pages/products/products" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'
import DecorBlocks from '@/components/decor-blocks/decor-blocks.vue'
import { staticUrl, getMe, getSalesProducts, getProductCategories, formatNum, safeNavigateTo } from '@/utils/api.js'

const UNCATEGORIZED = '__uncategorized__'

export default {
  components: { TabBar, DecorBlocks },
  data() {
    return {
      products: [],
      categories: [],
      query: '',
      loggedIn: false,
      activeCategoryId: 'all',
    }
  },
  computed: {
    categoryTabs() {
      const tabs = [{ id: 'all', name: '全部' }, ...this.categories.map((c) => ({ id: c.id, name: c.name }))]
      const knownIds = new Set(this.categories.map((c) => c.id))
      if (this.products.some((p) => !p.category_id || !knownIds.has(p.category_id))) {
        tabs.push({ id: UNCATEGORIZED, name: '其他' })
      }
      return tabs
    },
    visibleProducts() {
      const q = this.query.trim().toLowerCase()
      if (q) {
        return this.products.filter((p) =>
          [p.name, p.internal_code, p.chassis_info, p.chassis_number].join(' ').toLowerCase().includes(q)
        )
      }
      if (this.activeCategoryId === 'all') return this.products
      const knownIds = new Set(this.categories.map((c) => c.id))
      if (this.activeCategoryId === UNCATEGORIZED) {
        return this.products.filter((p) => !p.category_id || !knownIds.has(p.category_id))
      }
      return this.products.filter((p) => p.category_id === this.activeCategoryId)
    },
  },
  onShow() {
    this.loadProducts()
  },
  methods: {
    staticUrl,
    formatNum,
    goLogin() {
      safeNavigateTo('/pages/login/login')
    },
    selectCategory(id) {
      this.activeCategoryId = id
    },
    goDetail(id) {
      safeNavigateTo(`/pages/product-detail/product-detail?id=${id}`)
    },
    async loadProducts() {
      try {
        await getMe()
        this.loggedIn = true
      } catch (e) {
        this.loggedIn = false
        this.products = []
        this.categories = []
        return
      }
      try {
        const [products, categories] = await Promise.all([getSalesProducts(), getProductCategories()])
        this.products = products
        this.categories = categories
      } catch (e) {
        this.products = []
        this.categories = []
      }
    },
  },
}
</script>

<style>
.page {
  height: 100vh;
  box-sizing: border-box;
  padding: 24rpx 24rpx 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.login-prompt {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 80rpx 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14rpx;
}
.login-prompt-icon {
  font-size: 56rpx;
}
.login-prompt-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--ink);
}
.login-prompt-btn {
  margin-top: 20rpx;
  width: 100%;
  border: none;
  border-radius: var(--radius-md);
  font-size: 27rpx;
  font-weight: 600;
  padding: 20rpx 0;
}
.btn-primary {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
}
.page-head {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 20rpx;
  flex-shrink: 0;
}
.page-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--ink);
}
.search-input {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  padding: 18rpx 22rpx;
  font-size: 26rpx;
  color: var(--ink);
}
.empty-hint {
  text-align: center;
  color: var(--ink-soft);
  font-size: 24rpx;
  padding: 80rpx 0;
}
.menu-layout {
  flex: 1;
  min-height: 0;
  display: flex;
  margin: 0 -24rpx;
}
.menu-sidebar {
  width: 176rpx;
  flex-shrink: 0;
  height: 100%;
  background: var(--bg);
}
.menu-sidebar-item {
  padding: 26rpx 10rpx;
  text-align: center;
  font-size: 24rpx;
  line-height: 1.3;
  color: var(--ink-soft);
  border-left: 6rpx solid transparent;
  box-sizing: border-box;
}
.menu-sidebar-item.active {
  background: var(--card-bg);
  color: var(--ink);
  font-weight: 700;
  border-left-color: var(--accent);
}
.menu-products {
  flex: 1;
  min-width: 0;
  height: 100%;
  box-sizing: border-box;
  padding: 20rpx 24rpx 160rpx;
}
.product-card {
  display: flex;
  gap: 20rpx;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.product-image {
  width: 160rpx;
  height: 284rpx;
  border-radius: var(--radius-md);
  flex-shrink: 0;
  background: var(--bg);
}
.product-image.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  color: var(--ink-soft);
  text-align: center;
}
.product-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding: 6rpx 0;
}
.product-name {
  font-size: 28rpx;
  font-weight: 700;
  color: var(--ink);
}
.product-code,
.product-chassis {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.product-price {
  font-size: 26rpx;
  font-weight: 700;
  color: var(--danger);
}
</style>
