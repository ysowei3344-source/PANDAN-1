<template>
  <view class="page">
    <!-- 第一屏：轮播广告 -->
    <swiper
      class="banner-swiper"
      indicator-dots
      indicator-color="rgba(255,255,255,0.4)"
      indicator-active-color="#ffffff"
      autoplay
      interval="4000"
      circular
    >
      <swiper-item v-for="b in banners" :key="b.id">
        <image class="banner-image" :src="staticUrl(b.image_url)" mode="aspectFill"></image>
      </swiper-item>
    </swiper>

    <!-- 第二屏：账号列表 -->
    <view class="panel">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">矩阵账号</text>
        <text class="panel-more" @click="goAccounts">全部 ›</text>
      </view>
      <view class="account-scroll">
        <view class="account-grid">
          <view class="account-item" v-for="a in accounts" :key="a.id" @click="goAccounts">
            <view class="account-avatar" :class="badgeClass(a.platform)">{{ platformInitial(a.platform) }}</view>
            <text class="account-name">{{ a.nickname }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 第三屏：今日数据分析 -->
    <view class="panel">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">今日数据分析</text>
        <text class="panel-sub">全平台 · 全部账号</text>
      </view>
      <view class="kpi-grid">
        <view class="kpi-card">
          <view class="kpi-icon badge-blue">▦</view>
          <text class="kpi-num">{{ today.videos_published }}</text>
          <text class="kpi-label">视频发布总数</text>
        </view>
        <view class="kpi-card">
          <view class="kpi-icon badge-green">▶</view>
          <text class="kpi-num">{{ formatNum(today.total_exposure) }}</text>
          <text class="kpi-label">视频曝光总数</text>
        </view>
        <view class="kpi-card">
          <view class="kpi-icon badge-amber">✉</view>
          <text class="kpi-num">{{ today.dm_conversations }}</text>
          <text class="kpi-label">私信沟通客户数</text>
        </view>
        <view class="kpi-card">
          <view class="kpi-icon badge-pink">♥</view>
          <text class="kpi-num">{{ today.wechat_added }}</text>
          <text class="kpi-label">添加微信客户数</text>
        </view>
      </view>
    </view>

    <!-- 第四屏：分平台视频 + DeepSeek 分析 -->
    <view class="panel">
      <view class="platform-tabs">
        <view
          v-for="t in platformTabs"
          :key="t.value"
          class="tab-chip"
          :class="{ active: activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
        </view>
      </view>

      <view class="content-list">
        <view class="content-card" v-for="v in filteredVideos" :key="v.id">
          <image class="content-thumb" :src="staticUrl(v.thumbnail_url)" mode="aspectFill"></image>
          <view class="content-body">
            <text class="content-title">{{ v.title }}</text>
            <view class="content-meta-row">
              <text class="content-meta">播放 {{ formatNum(v.plays) }}</text>
              <text class="content-meta">赞 {{ formatNum(v.likes) }}</text>
              <text class="content-meta">评 {{ formatNum(v.comments) }}</text>
            </view>
            <view class="analysis-box">
              <text class="analysis-tag">DeepSeek 分析</text>
              <text class="analysis-text">{{ v.deepseek_analysis }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <tab-bar current="/pages/index/index" />
  </view>
</template>

<script>
import { getAccounts, getBanners, getTodayStats, getVideos, staticUrl } from '@/utils/api.js'
import TabBar from '@/components/tab-bar/tab-bar.vue'

export default {
  components: { TabBar },
  data() {
    return {
      banners: [],
      accounts: [],
      today: {
        videos_published: 0,
        total_exposure: 0,
        dm_conversations: 0,
        wechat_added: 0,
      },
      videos: [],
      activeTab: 'douyin',
      platformTabs: [
        { value: 'douyin', label: '抖音' },
        { value: 'xiaohongshu', label: '小红书' },
        { value: 'video_channel', label: '视频号' },
      ],
    }
  },
  computed: {
    filteredVideos() {
      return this.videos.filter((v) => v.platform === this.activeTab)
    },
  },
  onLoad() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      const [banners, accounts, today, videos] = await Promise.all([
        getBanners().catch(() => []),
        getAccounts().catch(() => []),
        getTodayStats().catch(() => this.today),
        getVideos().catch(() => []),
      ])
      this.banners = banners
      this.accounts = accounts
      this.today = today
      this.videos = videos
    },
    goAccounts() {
      uni.switchTab({ url: '/pages/accounts/accounts' })
    },
    staticUrl,
    formatNum(n) {
      if (n === undefined || n === null) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return String(n)
    },
    platformInitial(platform) {
      return { douyin: '抖', video_channel: '视', xiaohongshu: '红' }[platform] || '·'
    },
    badgeClass(platform) {
      return { douyin: 'badge-dark', video_channel: 'badge-green', xiaohongshu: 'badge-pink' }[platform] || 'badge-blue'
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

/* 第一屏：轮播广告 */
.banner-swiper {
  width: 100%;
  height: 300rpx;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.banner-image {
  width: 100%;
  height: 100%;
}

/* Panels */
.panel {
  margin-top: 28rpx;
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
.panel-more {
  font-size: 22rpx;
  color: var(--ink-soft);
}

/* 第二屏：账号横滑网格 */
.account-scroll {
  overflow-x: auto;
}
.account-grid {
  display: grid;
  grid-template-rows: repeat(2, auto);
  grid-auto-flow: column;
  grid-auto-columns: 140rpx;
  gap: 24rpx 8rpx;
}
.account-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  width: 140rpx;
}
.account-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
}
.account-name {
  font-size: 21rpx;
  color: var(--ink);
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Badges */
.badge-blue { background: var(--accent-soft); color: var(--accent); }
.badge-green { background: var(--success-soft); color: var(--success); }
.badge-pink { background: var(--danger-soft); color: var(--danger); }
.badge-amber { background: var(--warning-soft); color: var(--warning); }
.badge-dark { background: #1f2430; color: #ffffff; }

/* 第三屏：今日数据 KPI */
.kpi-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.kpi-card {
  flex: 1 1 40%;
  background: var(--bg);
  border-radius: var(--radius-md);
  padding: 22rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.kpi-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
}
.kpi-num {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--ink);
}
.kpi-label {
  font-size: 21rpx;
  color: var(--ink-soft);
}

/* 第四屏：平台 tab */
.platform-tabs {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
}
.tab-chip {
  padding: 10rpx 28rpx;
  border-radius: 999px;
  font-size: 24rpx;
  font-weight: 500;
  color: var(--ink-soft);
  background: var(--bg);
}
.tab-chip.active {
  color: #ffffff;
  background: var(--accent);
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.content-card {
  display: flex;
  gap: 18rpx;
}
.content-thumb {
  width: 200rpx;
  height: 200rpx;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}
.content-body {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  flex: 1;
  min-width: 0;
}
.content-title {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--ink);
}
.content-meta-row {
  display: flex;
  gap: 16rpx;
}
.content-meta {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.analysis-box {
  background: var(--accent-soft);
  border-radius: 16rpx;
  padding: 14rpx 16rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}
.analysis-tag {
  font-size: 20rpx;
  font-weight: 700;
  color: var(--accent);
}
.analysis-text {
  font-size: 21rpx;
  color: var(--ink);
  line-height: 1.6;
}
</style>
