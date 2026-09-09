<template>
  <view class="page" :class="{ 'has-avatar-rail': showAvatarRail }">
    <text class="page-title">{{ pageTitle }}</text>

    <view class="login-prompt" v-if="!currentUser">
      <text class="login-prompt-icon">🔒</text>
      <text class="login-prompt-title">登录后查看</text>
      <button class="btn-primary login-prompt-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <input class="search-input" v-model="searchQuery" placeholder="搜索姓名/电话/销售跟单猿" />

      <view class="toolbar">
        <view class="sort-btn" @click="toggleSortOrder">按时间{{ sortAsc ? '正序' : '倒序' }} {{ sortAsc ? '↑' : '↓' }}</view>
        <picker :range="stageFilterOptions" :value="stageFilterIndex" @change="onStageFilterChange">
          <view class="stage-filter-btn">{{ stageFilterOptions[stageFilterIndex] }} ▾</view>
        </picker>
      </view>

      <view class="empty-hint" v-if="!filteredOrders.length">{{ orders.length ? '没有匹配的订单' : '还没有订单' }}</view>
      <view class="order-list" v-else>
        <view class="order-row" v-for="o in filteredOrders" :key="o.id" @click="onOrderTap(o)">
          <view class="order-avatar">
            <image v-if="o.avatar_url" class="order-avatar-img" :src="staticUrl(o.avatar_url)" mode="aspectFill"></image>
            <text v-else>{{ o.name ? o.name[0] : '?' }}</text>
          </view>
          <view class="order-body">
            <view class="order-top">
              <text class="order-name">{{ o.name }}</text>
              <text class="stage-pill" :class="stageClass(o.stage)">{{ stageLabel(o.stage) }}</text>
            </view>
            <text class="order-sub">{{ o.assigned_to }} · {{ formatDate(o.created_at) }}</text>
          </view>
          <text class="chevron">›</text>
        </view>
      </view>

      <!-- 右侧竖排跟单猿头像浮层：只有超级管理员看得到，点头像单独筛选那一个人 -->
      <scroll-view v-if="showAvatarRail" scroll-y class="sales-avatar-rail">
        <view class="sales-avatar-item" @click="salesFilter = 'all'">
          <view class="sales-avatar-circle all-circle" :class="{ active: salesFilter === 'all' }">全部</view>
        </view>
        <view class="sales-avatar-item" v-for="n in salesNames" :key="n" @click="salesFilter = n">
          <view class="sales-avatar-circle" :class="{ active: salesFilter === n }">
            <image v-if="avatarOf(n)" class="sales-avatar-img" :src="staticUrl(avatarOf(n))" mode="aspectFill"></image>
            <text v-else>{{ n ? n[0] : '?' }}</text>
          </view>
        </view>
      </scroll-view>
    </template>
  </view>
</template>

<script>
import { getMe, getOrders, getSalesList, getSalesNames, stageLabel, CUSTOMER_STAGES, staticUrl, safeNavigateTo } from '@/utils/api.js'

export default {
  data() {
    return {
      currentUser: null,
      orders: [],
      salesUsers: [],
      searchQuery: '',
      salesFilter: 'all',
      sortAsc: false,
      stageFilterIndex: 0,
    }
  },
  computed: {
    pageTitle() {
      return this.currentUser && this.currentUser.role === 'super_admin' ? '全部订单' : '我的订单'
    },
    // 右侧竖排头像浮层 + 按人筛选，只对超级管理员有意义——销售跟单猿的 orders
    // 后端本来就只给了自己名下的，没有"切换看别人"这回事。
    showAvatarRail() {
      return !!(this.currentUser && this.currentUser.role === 'super_admin' && this.salesNames.length)
    },
    salesNames() {
      return getSalesNames(this.orders, this.salesUsers)
    },
    stageFilterOptions() {
      return ['全部阶段', ...CUSTOMER_STAGES.map((s, i) => `${i + 1}. ${s.label}`)]
    },
    displayOrders() {
      const dir = this.sortAsc ? 1 : -1
      return this.orders.slice().sort((a, b) => dir * ((Date.parse(a.created_at) || 0) - (Date.parse(b.created_at) || 0)))
    },
    filteredOrders() {
      let list = this.displayOrders
      if (this.currentUser && this.currentUser.role === 'super_admin' && this.salesFilter !== 'all') {
        list = list.filter((o) => o.assigned_to === this.salesFilter)
      }
      if (this.stageFilterIndex > 0) {
        const key = CUSTOMER_STAGES[this.stageFilterIndex - 1].key
        list = list.filter((o) => o.stage === key)
      }
      const q = this.searchQuery.trim().toLowerCase()
      if (q) {
        list = list.filter((o) => [o.name, o.phone, o.assigned_to].join(' ').toLowerCase().includes(q))
      }
      return list
    },
  },
  onShow() {
    this.init()
  },
  methods: {
    staticUrl,
    stageLabel,
    async init() {
      try {
        this.currentUser = await getMe()
      } catch (e) {
        this.currentUser = null
        return
      }
      try {
        const [all, salesUsers] = await Promise.all([getOrders(), getSalesList()])
        this.salesUsers = salesUsers
        // 超级管理员看全部订单，销售跟单猿只看自己名下的——跟首页那种"输口令
        // 解锁看别人"的机制不一样，这个页面对销售完全不开放别人的订单，权限
        // 更严格，不是弱化版的解锁流程。
        this.orders = this.currentUser.role === 'super_admin'
          ? all
          : all.filter((o) => o.assigned_to === this.currentUser.username)
      } catch (e) {
        this.orders = []
      }
    },
    goLogin() {
      safeNavigateTo('/pages/login/login')
    },
    toggleSortOrder() {
      this.sortAsc = !this.sortAsc
    },
    onStageFilterChange(e) {
      this.stageFilterIndex = Number(e.detail.value)
    },
    avatarOf(name) {
      const u = this.salesUsers.find((x) => x.username === name)
      return u ? u.avatar_url : null
    },
    stageClass(key) {
      const idx = CUSTOMER_STAGES.findIndex((s) => s.key === key)
      if (idx <= 2) return 'stage-early'
      if (idx <= 5) return 'stage-mid'
      if (idx === 6) return 'stage-late'
      return 'stage-done'
    },
    formatDate(iso) {
      if (!iso) return ''
      return String(iso).slice(0, 10)
    },
    onOrderTap(o) {
      safeNavigateTo(`/pages/order-form/order-form?id=${o.id}`)
    },
  },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 60rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.page-title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 24rpx;
  display: block;
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
.search-input {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  padding: 18rpx 22rpx;
  font-size: 26rpx;
  color: var(--ink);
  margin-bottom: 16rpx;
}
.page.has-avatar-rail {
  padding-right: 108rpx;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 20rpx;
}
.sort-btn,
.stage-filter-btn {
  font-size: 23rpx;
  color: var(--ink-soft);
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 12rpx 20rpx;
}
.sales-avatar-rail {
  position: fixed;
  right: 16rpx;
  top: 240rpx;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  z-index: 50;
}
.sales-avatar-item {
  padding: 8rpx 0;
  display: flex;
  justify-content: center;
}
.sales-avatar-circle {
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  background: var(--card-bg);
  box-shadow: var(--shadow);
  border: 3rpx solid transparent;
  color: var(--ink-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 700;
  overflow: hidden;
}
.sales-avatar-circle.active {
  border-color: var(--accent);
  color: var(--accent);
}
.sales-avatar-circle.all-circle {
  font-size: 20rpx;
}
.sales-avatar-img {
  width: 100%;
  height: 100%;
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
.order-list {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 0 24rpx;
}
.order-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 22rpx 0;
  border-bottom: 1px solid var(--line);
}
.order-row:last-child {
  border-bottom: none;
}
.order-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
  flex-shrink: 0;
  overflow: hidden;
}
.order-avatar-img {
  width: 100%;
  height: 100%;
}
.order-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}
.order-top {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.order-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.order-sub {
  font-size: 22rpx;
  color: var(--ink-soft);
}
.chevron {
  font-size: 32rpx;
  color: var(--ink-soft);
}
.stage-pill {
  font-size: 19rpx;
  padding: 3rpx 14rpx;
  border-radius: 999px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}
.stage-early { background: var(--accent-soft); color: var(--accent); }
.stage-mid { background: var(--warning-soft); color: var(--warning); }
.stage-late { background: var(--success-soft); color: var(--success); }
.stage-done { background: var(--ink); color: #ffffff; }
</style>
