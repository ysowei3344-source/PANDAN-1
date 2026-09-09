<template>
  <view class="page">
    <view class="login-prompt" v-if="!loggedIn">
      <text class="login-prompt-icon">🔒</text>
      <text class="login-prompt-title">登录后查看商品详情</text>
      <button class="btn-primary login-prompt-btn" @click="goLogin">去登录</button>
    </view>
    <view class="empty-hint" v-else-if="!loading && !product">没有找到这个商品</view>
    <template v-else-if="product">
      <view class="detail-hero">
        <view class="hero-image-box">
          <swiper
            v-if="product.main_image_urls && product.main_image_urls.length"
            class="hero-swiper"
            :indicator-dots="product.main_image_urls.length > 1"
            indicator-active-color="#3e7bfa"
          >
            <swiper-item v-for="(url, i) in product.main_image_urls" :key="i">
              <image class="hero-swiper-image" :src="staticUrl(url)" mode="aspectFill" @click="previewMainImage(i)"></image>
            </swiper-item>
          </swiper>
          <view v-else class="hero-swiper placeholder">暂无主图</view>
        </view>

        <scroll-view v-if="matchedCustomers.length" scroll-y class="hero-customers">
          <view class="customer-avatar-grid">
            <view class="customer-avatar-item" v-for="c in matchedCustomers" :key="c.id">
              <image v-if="c.avatar_url" class="customer-avatar-img" :src="staticUrl(c.avatar_url)" mode="aspectFill"></image>
              <view v-else class="customer-avatar-img placeholder">{{ c.name ? c.name[0] : '?' }}</view>
            </view>
          </view>
        </scroll-view>
        <view v-else class="hero-customers hero-customers-empty">
          <text>暂无客户匹配这款车</text>
        </view>
      </view>

      <view class="detail-body">
        <view class="detail-head-row">
          <text class="detail-name">{{ product.name }}</text>
          <text class="detail-price" v-if="product.price">¥{{ formatNum(product.price) }}</text>
        </view>
        <view class="tag-row" v-if="categoryName || product.internal_code">
          <text class="tag" v-if="categoryName">{{ categoryName }}</text>
          <text class="tag" v-if="product.internal_code">编码：{{ product.internal_code }}</text>
        </view>

        <view class="detail-section" v-if="product.chassis_info || product.chassis_number">
          <text class="section-title">底盘信息</text>
          <text class="section-text" v-if="product.chassis_info">{{ product.chassis_info }}</text>
          <text class="section-text" v-if="product.chassis_number">底盘编号：{{ product.chassis_number }}</text>
        </view>

        <view class="detail-section" v-if="product.standard_config">
          <text class="section-title">标准配置</text>
          <text class="section-text">{{ product.standard_config }}</text>
        </view>

        <view class="detail-section" v-if="product.optional_config">
          <text class="section-title">增选配置</text>
          <text class="section-text">{{ product.optional_config }}</text>
        </view>

        <view class="detail-section" v-if="layoutFiles.length">
          <text class="section-title">配置布局</text>
          <view class="layout-grid" v-if="imageLayoutFiles.length">
            <image
              v-for="(f, i) in imageLayoutFiles"
              :key="'img' + i"
              class="layout-thumb"
              :src="staticUrl(f.url)"
              mode="aspectFill"
              @click="previewLayoutImage(i)"
            ></image>
          </view>
          <view class="layout-doc-row" v-for="(f, i) in docLayoutFiles" :key="'doc' + i" @click="openLayoutDoc(f.url)">
            <text class="layout-doc-icon">📄</text>
            <text class="layout-doc-name">{{ f.name }}</text>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script>
import { staticUrl, getMe, getSalesProducts, getProductCategories, getOrders, formatNum, safeNavigateTo } from '@/utils/api.js'

function isImageUrl(url) {
  return /\.(png|jpe?g|gif|svg|webp)$/i.test(url || '')
}

export default {
  data() {
    return {
      productId: '',
      product: null,
      categories: [],
      orders: [],
      loggedIn: true,
      loading: true,
    }
  },
  computed: {
    // 客户头像不是随便放的——订单/客户/车型三者是绑在一条 Order 记录上的
    // (product_id 就是这条订单匹配的车型)，所以"匹配这款车的客户"直接按
    // product_id 过滤订单就行，不用额外接口。
    matchedCustomers() {
      if (!this.product) return []
      return this.orders.filter((o) => o.product_id === this.product.id)
    },
    categoryName() {
      if (!this.product || !this.product.category_id) return ''
      const c = this.categories.find((x) => x.id === this.product.category_id)
      return c ? c.name : ''
    },
    layoutFiles() {
      if (!this.product) return []
      return (this.product.layout_urls || []).map((url) => ({
        url,
        name: (url || '').split('/').pop(),
        isImage: isImageUrl(url),
      }))
    },
    imageLayoutFiles() {
      return this.layoutFiles.filter((f) => f.isImage)
    },
    docLayoutFiles() {
      return this.layoutFiles.filter((f) => !f.isImage)
    },
  },
  onLoad(options) {
    this.productId = (options && options.id) || ''
    this.loadProduct()
  },
  methods: {
    staticUrl,
    formatNum,
    goLogin() {
      safeNavigateTo('/pages/login/login')
    },
    async loadProduct() {
      this.loading = true
      try {
        await getMe()
        this.loggedIn = true
      } catch (e) {
        this.loggedIn = false
        this.loading = false
        return
      }
      try {
        const [products, categories] = await Promise.all([getSalesProducts(), getProductCategories()])
        this.product = products.find((p) => p.id === this.productId) || null
        this.categories = categories
      } catch (e) {
        this.product = null
      }
      try {
        this.orders = await getOrders()
      } catch (e) {
        this.orders = []
      }
      this.loading = false
    },
    previewMainImage(i) {
      const urls = this.product.main_image_urls.map(staticUrl)
      uni.previewImage({ current: urls[i], urls })
    },
    previewLayoutImage(i) {
      const urls = this.imageLayoutFiles.map((f) => staticUrl(f.url))
      uni.previewImage({ current: urls[i], urls })
    },
    openLayoutDoc(url) {
      uni.showLoading({ title: '打开中...' })
      uni.downloadFile({
        url: staticUrl(url),
        success: (res) => {
          uni.hideLoading()
          if (res.statusCode !== 200) {
            uni.showToast({ title: '文件下载失败', icon: 'none' })
            return
          }
          uni.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            fail: () => uni.showToast({ title: '无法打开该文件', icon: 'none' }),
          })
        },
        fail: () => {
          uni.hideLoading()
          uni.showToast({ title: '文件下载失败', icon: 'none' })
        },
      })
    },
  },
}
</script>

<style>
.page {
  min-height: 100vh;
  box-sizing: border-box;
  padding-bottom: 60rpx;
  background: var(--bg);
}
.login-prompt,
.empty-hint {
  margin: 24rpx;
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
.empty-hint {
  text-align: center;
  color: var(--ink-soft);
  font-size: 24rpx;
  padding: 80rpx 0;
}
.detail-hero {
  display: flex;
  gap: 20rpx;
  padding: 24rpx 24rpx 0;
  align-items: stretch;
}
.hero-image-box {
  width: 562rpx;
  height: 999rpx;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  background: var(--card-bg);
}
.hero-swiper {
  width: 100%;
  height: 100%;
}
.hero-swiper.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-soft);
  font-size: 24rpx;
}
.hero-swiper-image {
  width: 100%;
  height: 100%;
}
.hero-customers {
  flex: 1;
  min-width: 0;
  height: 999rpx;
  box-sizing: border-box;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 14rpx 10rpx;
}
.customer-avatar-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}
.customer-avatar-item {
  width: 96rpx;
}
.customer-avatar-img {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: var(--accent-soft);
}
.customer-avatar-img.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  font-weight: 700;
  font-size: 32rpx;
}
.hero-customers-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--ink-soft);
  font-size: 22rpx;
  line-height: 1.6;
}
.detail-body {
  padding: 28rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.detail-head-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16rpx;
}
.detail-name {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--ink);
  flex: 1;
  min-width: 0;
}
.detail-price {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--danger);
  flex-shrink: 0;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}
.tag {
  font-size: 21rpx;
  color: var(--ink-soft);
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: 999rpx;
  padding: 6rpx 18rpx;
}
.detail-section {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.section-title {
  font-size: 24rpx;
  font-weight: 700;
  color: var(--ink);
}
.section-text {
  font-size: 25rpx;
  color: var(--ink-soft);
  line-height: 1.5;
  white-space: pre-wrap;
}
.layout-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}
.layout-thumb {
  width: 160rpx;
  height: 160rpx;
  border-radius: var(--radius-md);
  background: var(--bg);
}
.layout-doc-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 14rpx 0;
  border-top: 1px solid var(--line);
}
.layout-doc-row:first-child {
  border-top: none;
}
.layout-doc-icon {
  font-size: 30rpx;
}
.layout-doc-name {
  font-size: 24rpx;
  color: var(--ink);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
