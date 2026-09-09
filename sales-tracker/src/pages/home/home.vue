<template>
  <view class="page">
    <view v-for="b in pageBlocks" :key="b.id">
      <!-- 本月成交总额大卡片 -->
      <template v-if="b.type === 'builtin_hero'">
        <view v-if="currentUser" class="hero">
          <picker mode="date" fields="month" :value="monthPickerValue" @change="onMonthChange" class="hero-month-picker">
            <view class="hero-month-pill">{{ monthLabel }} ▾</view>
          </picker>
          <view class="hero-top-row">
            <view class="hero-top-text">
              <text class="hero-label">当月客户总数</text>
              <text class="hero-amount">{{ formatNum(monthlyCustomerCount) }}</text>
              <text class="hero-compare">
                同比：<text :class="monthlyCompareDiff >= 0 ? 'compare-up' : 'compare-down'">{{ monthlyCompareDiff >= 0 ? '+' : '-' }}{{ Math.abs(monthlyCompareDiff) }}</text>人
              </text>
            </view>
            <view class="hero-mascot-wrap">
              <image class="hero-mascot" src="/static/001.png" mode="aspectFit"></image>
            </view>
          </view>
          <view class="hero-strip">
            <view class="hero-strip-item">
              <text class="hero-strip-num num-all">{{ monthlyCustomerCount }}</text>
              <text class="hero-strip-label">全部客户</text>
            </view>
            <view class="hero-strip-div"></view>
            <view class="hero-strip-item">
              <text class="hero-strip-num num-intent">{{ monthlyIntentCount }}</text>
              <text class="hero-strip-label">意向客户</text>
            </view>
            <view class="hero-strip-div"></view>
            <view class="hero-strip-item">
              <text class="hero-strip-num num-deal">{{ monthlyDealCustomerCount }}</text>
              <text class="hero-strip-label">成交客户</text>
            </view>
          </view>
        </view>
      </template>

      <!-- 跟单猿数据 -->
      <template v-else-if="b.type === 'builtin_sales_performance'">
        <view v-if="currentUser" class="panel">
          <view class="panel-head">
            <view class="head-bar"></view>
            <text class="panel-title">{{ b.props.title || '跟单猿数据' }}</text>
          </view>
          <view class="people-scroll">
            <view class="people-row">
              <view class="person-item" v-for="name in salesNames" :key="name" @click="onPersonTap(name)">
                <view class="person-avatar" :class="{ me: name === (currentUser && currentUser.username) }">
                  <image v-if="avatarOf(name)" class="person-avatar-img" :src="staticUrl(avatarOf(name))" mode="aspectFill"></image>
                  <text v-else>{{ name ? name[0] : '?' }}</text>
                </view>
                <text class="person-name">{{ name }}</text>
                <text class="person-amount" v-if="isUnlocked(name)">{{ perfOf(name).newThisMonth }}人</text>
                <text class="person-amount locked" v-else>🔒</text>
              </view>
            </view>
          </view>
        </view>
      </template>

      <!-- 客户流水单 -->
      <template v-else-if="b.type === 'builtin_customer_list'">
        <view v-if="currentUser" class="panel">
          <view class="panel-head">
            <view class="head-bar"></view>
            <text class="panel-title">{{ b.props.title || '客户流水单' }}</text>
            <text class="panel-sub" v-if="!showAllOrders && orders.length > 15">
              仅显示前15条 <text class="panel-sub-link" @click="toggleShowAllOrders">查看全部</text>
            </text>
            <text class="panel-sub panel-sub-link" v-else-if="showAllOrders && orders.length > 15" @click="toggleShowAllOrders">收起</text>
          </view>
          <view class="empty-hint" v-if="!orders.length">还没有订单，点底部"搞订单"新建一个</view>
          <view class="customer-list" v-else>
            <view
              class="customer-row"
              v-for="o in recentOrders"
              :key="o.id"
              @click="onOrderTap(o)"
            >
              <view class="customer-avatar">{{ o.name ? o.name[0] : '?' }}</view>
              <view class="customer-body">
                <view class="customer-top">
                  <text class="customer-name">{{ isUnlocked(o.assigned_to) ? o.name : '***' }}</text>
                  <text class="stage-pill" :class="stageClass(o.stage)">{{ stageLabel(o.stage) }}</text>
                </view>
                <text class="customer-sub">{{ o.assigned_to }} · {{ formatDate(o.created_at) }}</text>
              </view>
              <text class="chevron">›</text>
            </view>
          </view>
        </view>
      </template>

      <!-- 后台自由拼装的装修组件：不管登没登录都显示 -->
      <decor-block-item v-else :block="b" />
    </view>

    <view class="login-prompt" v-if="!currentUser">
      <text class="login-prompt-icon">🔒</text>
      <text class="login-prompt-title">登录后查看团队业绩和客户数据</text>
      <text class="login-prompt-sub">订单/业绩这些数据涉及客户隐私，需要先登录才能看</text>
      <button class="btn-primary login-prompt-btn" @click="goLogin">去登录</button>
      <text class="login-prompt-debug" v-if="loginError">（{{ loginError }}）</text>
    </view>

    <view class="modal-overlay" v-if="passcodeVisible" @click="closePasscode">
      <view class="passcode-card" @click.stop>
        <text class="passcode-title">需要管理口令</text>
        <text class="passcode-sub">查看「{{ passcodeTarget }}」的详细业绩/订单，需要输入这位销售跟单猿的管理口令</text>
        <input class="field-input" v-model="passcodeInput" password placeholder="输入管理口令" />
        <text class="msg error" v-if="passcodeMsg">{{ passcodeMsg }}</text>
        <view class="passcode-actions">
          <button class="btn-ghost" @click="closePasscode">取消</button>
          <button class="btn-primary" @click="submitPasscode">解锁</button>
        </view>
      </view>
    </view>

    <tab-bar current="/pages/home/home" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'
import DecorBlockItem from '@/components/decor-block-item/decor-block-item.vue'
import {
  getMe,
  getOrders,
  getSalesList,
  getDecorBlocks,
  computeSalesPerformance,
  getSalesNames,
  isSalesGroupUnlocked,
  unlockedSalesGroups,
  verifySalesPasscode,
  stageLabel,
  CUSTOMER_STAGES,
  formatNum,
  safeNavigateTo,
  staticUrl,
} from '@/utils/api.js'

export default {
  components: { TabBar, DecorBlockItem },
  data() {
    const now = new Date()
    return {
      pageBlocks: [],
      currentUser: null,
      loginError: '',
      orders: [],
      salesUsers: [],
      passcodeVisible: false,
      passcodeTarget: '',
      passcodeInput: '',
      passcodeMsg: '',
      selectedMonth: { year: now.getFullYear(), month: now.getMonth() }, // month 0-indexed
      showAllOrders: false,
    }
  },
  computed: {
    salesNames() {
      return getSalesNames(this.orders, this.salesUsers)
    },
    // 蓝色浮层三栏，都按当月（月份选择器选中的那个月）统计，跟上面"当月客户总数"
    // 用的是同一个月份口径：
    // 全部客户 = 当月所有订单，不管阶段
    // 意向客户 = 阶段 3/4/5（电话/视频/看车客户）
    // 成交客户 = 阶段 6/7/8（定金/成交/交付客户）
    monthlyIntentCount() {
      const keys = new Set(CUSTOMER_STAGES.slice(2, 5).map((s) => s.key))
      return this.ordersInMonth(this.selectedMonth).filter((o) => keys.has(o.stage)).length
    },
    monthlyDealCustomerCount() {
      const keys = new Set(CUSTOMER_STAGES.slice(5, 8).map((s) => s.key))
      return this.ordersInMonth(this.selectedMonth).filter((o) => keys.has(o.stage)).length
    },
    sortedOrders() {
      return this.orders.slice().sort((a, b) => (Date.parse(b.created_at) || 0) - (Date.parse(a.created_at) || 0))
    },
    recentOrders() {
      return this.showAllOrders ? this.sortedOrders : this.sortedOrders.slice(0, 15)
    },
    monthLabel() {
      return `${this.selectedMonth.month + 1}月`
    },
    monthPickerValue() {
      return `${this.selectedMonth.year}-${String(this.selectedMonth.month + 1).padStart(2, '0')}`
    },
    monthlyCustomerCount() {
      return this.ordersInMonth(this.selectedMonth).length
    },
    monthlyCompareDiff() {
      const prevMonth = this.selectedMonth.month === 0 ? 11 : this.selectedMonth.month - 1
      const prevYear = this.selectedMonth.month === 0 ? this.selectedMonth.year - 1 : this.selectedMonth.year
      const prevCount = this.ordersInMonth({ year: prevYear, month: prevMonth }).length
      return this.monthlyCustomerCount - prevCount
    },
  },
  onShow() {
    this.loadAll()
  },
  methods: {
    formatNum,
    stageLabel,
    staticUrl,
    avatarOf(name) {
      const u = this.salesUsers.find((x) => x.username === name)
      return u ? u.avatar_url : null
    },
    async loadAll() {
      this.pageBlocks = await getDecorBlocks('sales-tracker', 'home').catch(() => [])
      // 没登录也能打开首页——只是拿不到 orders/salesUsers 这些接口都要求
      // Authorization，登录失败就留空态，展示"登录后查看"，不强制跳转。
      try {
        this.currentUser = await getMe()
        this.loginError = ''
      } catch (e) {
        // 显示具体原因——"未登录"（token没有/过期）跟"网络错误"（请求根本没打
        // 通，比如小程序后台域名白名单没配）看着都是一个提示卡，但原因完全不同，
        // 不加这行没法从截图看出来是哪种。
        this.currentUser = null
        this.loginError = e.message || ''
        this.orders = []
        this.salesUsers = []
        return
      }
      try {
        const [orders, salesUsers] = await Promise.all([getOrders(), getSalesList()])
        this.orders = orders
        this.salesUsers = salesUsers
      } catch (e) {
        this.orders = []
        this.salesUsers = []
      }
    },
    goLogin() {
      safeNavigateTo('/pages/login/login')
    },
    toggleShowAllOrders() {
      this.showAllOrders = !this.showAllOrders
    },
    ordersInMonth(m) {
      return this.orders.filter((o) => {
        const d = new Date(o.created_at)
        return d.getFullYear() === m.year && d.getMonth() === m.month
      })
    },
    onMonthChange(e) {
      const [y, m] = e.detail.value.split('-').map(Number)
      this.selectedMonth = { year: y, month: m - 1 }
    },
    perfOf(name) {
      return computeSalesPerformance(this.orders, name)
    },
    isUnlocked(name) {
      return isSalesGroupUnlocked(this.currentUser, name)
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
    onPersonTap(name) {
      if (this.isUnlocked(name)) return
      this.openPasscode(name)
    },
    onOrderTap(o) {
      if (!this.isUnlocked(o.assigned_to)) {
        this.openPasscode(o.assigned_to)
        return
      }
      safeNavigateTo(`/pages/order-form/order-form?id=${o.id}`)
    },
    openPasscode(name) {
      this.passcodeTarget = name
      this.passcodeInput = ''
      this.passcodeMsg = ''
      this.passcodeVisible = true
    },
    closePasscode() {
      this.passcodeVisible = false
    },
    async submitPasscode() {
      if (!this.passcodeInput.trim()) {
        this.passcodeMsg = '请输入口令'
        return
      }
      try {
        await verifySalesPasscode(this.passcodeTarget, this.passcodeInput.trim())
        unlockedSalesGroups.add(this.passcodeTarget)
        this.passcodeVisible = false
      } catch (e) {
        this.passcodeMsg = e.message
      }
    },
  },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 160rpx;
  min-height: 100vh;
  box-sizing: border-box;
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
.login-prompt-sub {
  font-size: 22rpx;
  color: var(--ink-soft);
  line-height: 1.6;
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
.login-prompt-debug {
  margin-top: 12rpx;
  font-size: 20rpx;
  color: var(--ink-soft);
}

.hero {
  position: relative;
  height: 520rpx;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 40rpx 32rpx 0;
  display: flex;
  flex-direction: column;
  color: var(--ink);
  box-sizing: border-box;
}
.hero-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}
.hero-top-text {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}
.hero-month-picker {
  position: absolute;
  top: 24rpx;
  right: 32rpx;
  z-index: 3;
}
.hero-month-pill {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  font-size: 24rpx;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 999px;
  padding: 4rpx 18rpx;
}
.hero-label {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--ink);
}
.hero-amount {
  font-size: 60rpx;
  font-weight: 700;
  margin-top: 10rpx;
  color: var(--ink);
}
.hero-compare {
  font-size: 24rpx;
  color: var(--ink-soft);
  margin-top: 8rpx;
}
.compare-up {
  color: var(--danger);
  font-weight: 600;
}
.compare-down {
  color: var(--success);
  font-weight: 600;
}
.hero-mascot-wrap {
  width: 451rpx;
  height: 550rpx;
  flex-shrink: 0;
  overflow: hidden;
  margin-top: -70rpx;
}
.hero-mascot {
  width: 451rpx;
  height: 571rpx;
  flex-shrink: 0;
}
.hero-strip {
  position: absolute;
  left: 32rpx;
  right: 32rpx;
  bottom: 30rpx;
  z-index: 2;
  background: rgba(20, 48, 110, 0.88);
  border-radius: var(--radius-md);
  padding: 22rpx 12rpx;
  display: flex;
  align-items: center;
}
.hero-strip-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}
.hero-strip-num {
  font-size: 34rpx;
  font-weight: 700;
  color: #ffffff;
}
.hero-strip-num.num-all {
  color: #7fc4ff;
}
.hero-strip-num.num-intent {
  color: var(--success);
}
.hero-strip-num.num-deal {
  color: var(--danger);
}
.hero-strip-label {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.85);
}
.hero-strip-div {
  width: 1px;
  height: 44rpx;
  background: rgba(255, 255, 255, 0.3);
}

.panel {
  margin-top: 24rpx;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 28rpx;
}
.panel-head {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-bottom: 20rpx;
}
.head-bar {
  width: 6rpx;
  height: 26rpx;
  border-radius: 6rpx;
  background: var(--accent);
}
.panel-title {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--ink);
  flex: 1;
}
.panel-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.panel-sub-link {
  color: var(--accent);
  font-weight: 600;
}

.people-scroll {
  overflow-x: auto;
}
.people-row {
  display: flex;
  gap: 32rpx;
  padding-bottom: 4rpx;
}
.person-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  width: 108rpx;
  flex-shrink: 0;
}
.person-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  overflow: hidden;
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
}
.person-avatar.me {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
}
.person-avatar-img {
  width: 100%;
  height: 100%;
}
.person-name {
  font-size: 24rpx;
  color: var(--ink);
  max-width: 108rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.person-amount {
  font-size: 20rpx;
  color: var(--success);
  font-weight: 700;
}
.person-amount.locked {
  color: var(--ink-soft);
}

.empty-hint {
  text-align: center;
  color: var(--ink-soft);
  font-size: 24rpx;
  padding: 48rpx 0;
}

.customer-list {
  display: flex;
  flex-direction: column;
}
.customer-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 18rpx 0;
  border-bottom: 1px solid var(--line);
}
.customer-row:last-child {
  border-bottom: none;
}
.customer-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: var(--bg);
  color: var(--ink-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  flex-shrink: 0;
}
.customer-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.customer-top {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.customer-name {
  font-size: 27rpx;
  font-weight: 600;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.customer-sub {
  font-size: 21rpx;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(20, 30, 50, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 48rpx;
}
.passcode-card {
  width: 100%;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 40rpx 32rpx;
  display: flex;
  flex-direction: column;
}
.passcode-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--ink);
}
.passcode-sub {
  font-size: 23rpx;
  color: var(--ink-soft);
  margin-top: 10rpx;
  margin-bottom: 24rpx;
  line-height: 1.6;
}
.field-input {
  width: 100%;
  box-sizing: border-box;
  padding: 20rpx 22rpx;
  border-radius: var(--radius-md);
  background: var(--bg);
  border: 1px solid var(--line);
  font-size: 27rpx;
  color: var(--ink);
}
.msg { font-size: 23rpx; margin-top: 12rpx; }
.msg.error { color: var(--danger); }
.passcode-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 24rpx;
}
.passcode-actions button {
  flex: 1;
  border-radius: var(--radius-md);
  font-size: 27rpx;
  font-weight: 600;
  padding: 18rpx 0;
  border: none;
}
.btn-ghost {
  background: var(--bg);
  color: var(--ink);
}
.btn-primary {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
}
</style>
