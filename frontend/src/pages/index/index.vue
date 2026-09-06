<template>
  <view class="page">
    <!-- Hero -->
    <view class="hero">
      <view class="hero-text">
        <text class="hero-title">矩阵数据看板</text>
        <text class="hero-sub">{{ loadError ? '接口未连接，显示为空' : '抖音 · 视频号 · 小红书，一屏看完' }}</text>
      </view>
      <view class="hero-deco">
        <view class="deco-circle c1"></view>
        <view class="deco-circle c2"></view>
        <view class="deco-glyph">📊</view>
      </view>
    </view>

    <!-- KPI 卡片 -->
    <view class="kpi-grid">
      <view class="kpi-card">
        <view class="kpi-icon badge-blue">👥</view>
        <text class="kpi-num">{{ summary.total_accounts }}</text>
        <text class="kpi-label">矩阵账号</text>
      </view>
      <view class="kpi-card">
        <view class="kpi-icon badge-green">▶</view>
        <text class="kpi-num">{{ formatNum(summary.total_plays) }}</text>
        <text class="kpi-label">总播放</text>
      </view>
      <view class="kpi-card">
        <view class="kpi-icon badge-pink">♥</view>
        <text class="kpi-num">{{ formatNum(summary.total_followers) }}</text>
        <text class="kpi-label">总粉丝</text>
      </view>
      <view class="kpi-card">
        <view class="kpi-icon badge-amber">▦</view>
        <text class="kpi-num">{{ summary.total_videos }}</text>
        <text class="kpi-label">视频数</text>
      </view>
    </view>

    <!-- 分平台数据 -->
    <view class="panel">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">分平台数据</text>
      </view>
      <view class="platform-list">
        <view class="platform-row" v-for="p in summary.by_platform" :key="p.platform">
          <view class="platform-icon" :class="platformBadgeClass(p.platform)">{{ platformInitial(p.platform) }}</view>
          <view class="platform-info">
            <text class="platform-name">{{ platformLabel(p.platform) }}</text>
            <text class="platform-sub">{{ p.account_count }} 个账号</text>
          </view>
          <view class="platform-nums">
            <text class="platform-num">{{ formatNum(p.total_plays) }}</text>
            <text class="platform-num-label">播放</text>
          </view>
          <view class="platform-nums">
            <text class="platform-num">{{ formatNum(p.total_followers) }}</text>
            <text class="platform-num-label">粉丝</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 播放量 Top 视频 -->
    <view class="panel">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">播放量 Top 视频</text>
      </view>
      <view class="video-list">
        <view class="video-row" v-for="(v, i) in summary.top_videos" :key="v.id">
          <text class="video-rank">{{ i + 1 }}</text>
          <view class="video-body">
            <text class="video-title">{{ v.title }}</text>
            <view class="video-meta-row">
              <text class="video-tag" :class="platformBadgeClass(v.platform)">{{ platformLabel(v.platform) }}</text>
              <text class="video-meta">播放 {{ formatNum(v.plays) }}</text>
              <text class="video-meta">赞 {{ formatNum(v.likes) }}</text>
              <text class="video-meta">评 {{ formatNum(v.comments) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getDashboardSummary } from '@/utils/api.js'

export default {
  data() {
    return {
      loadError: false,
      summary: {
        total_accounts: 0,
        total_videos: 0,
        total_plays: 0,
        total_followers: 0,
        by_platform: [],
        top_videos: [],
      },
    }
  },
  onLoad() {
    this.loadSummary()
  },
  methods: {
    async loadSummary() {
      try {
        this.summary = await getDashboardSummary()
        this.loadError = false
      } catch (e) {
        this.loadError = true
      }
    },
    formatNum(n) {
      if (n === undefined || n === null) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return String(n)
    },
    platformLabel(platform) {
      return { douyin: '抖音', video_channel: '视频号', xiaohongshu: '小红书' }[platform] || platform
    },
    platformInitial(platform) {
      return { douyin: '抖', video_channel: '视', xiaohongshu: '红' }[platform] || '·'
    },
    platformBadgeClass(platform) {
      return { douyin: 'badge-dark', video_channel: 'badge-green', xiaohongshu: 'badge-pink' }[platform] || 'badge-blue'
    },
  },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 48rpx;
  min-height: 100vh;
  box-sizing: border-box;
}

/* Hero */
.hero {
  position: relative;
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  border-radius: var(--radius-lg);
  padding: 40rpx 32rpx;
  min-height: 180rpx;
  display: flex;
  align-items: center;
  overflow: hidden;
  box-shadow: var(--shadow);
}
.hero-text {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  position: relative;
  z-index: 1;
}
.hero-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
}
.hero-sub {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.82);
}
.hero-deco {
  position: absolute;
  right: 0;
  top: 0;
  width: 260rpx;
  height: 100%;
}
.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}
.c1 { width: 200rpx; height: 200rpx; right: -60rpx; top: -60rpx; }
.c2 { width: 120rpx; height: 120rpx; right: 40rpx; bottom: -50rpx; background: rgba(255, 255, 255, 0.16); }
.deco-glyph {
  position: absolute;
  right: 36rpx;
  bottom: 24rpx;
  font-size: 56rpx;
  opacity: 0.9;
}

/* KPI grid */
.kpi-grid {
  margin-top: 20rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.kpi-card {
  flex: 1 1 40%;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.kpi-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
}
.kpi-num {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--ink);
}
.kpi-label {
  font-size: 22rpx;
  color: var(--ink-soft);
}

/* Badges */
.badge-blue { background: var(--accent-soft); color: var(--accent); }
.badge-green { background: var(--success-soft); color: var(--success); }
.badge-pink { background: var(--danger-soft); color: var(--danger); }
.badge-amber { background: var(--warning-soft); color: var(--warning); }
.badge-dark { background: #1f2430; color: #ffffff; }

/* Panels */
.panel {
  margin-top: 32rpx;
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
}

/* Platform rows */
.platform-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.platform-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 16rpx 0;
  border-bottom: 1px solid var(--line);
}
.platform-row:last-child { border-bottom: none; padding-bottom: 0; }
.platform-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  flex-shrink: 0;
}
.platform-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4rpx;
}
.platform-name {
  font-size: 27rpx;
  font-weight: 600;
  color: var(--ink);
}
.platform-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.platform-nums {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2rpx;
  min-width: 100rpx;
}
.platform-num {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--ink);
}
.platform-num-label {
  font-size: 20rpx;
  color: var(--ink-soft);
}

/* Video list */
.video-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.video-row {
  display: flex;
  gap: 20rpx;
  padding: 16rpx 0;
  border-bottom: 1px solid var(--line);
}
.video-row:last-child { border-bottom: none; padding-bottom: 0; }
.video-rank {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--bg);
  color: var(--ink-soft);
  font-size: 22rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.video-body {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  flex: 1;
}
.video-title {
  font-size: 26rpx;
  color: var(--ink);
  font-weight: 500;
}
.video-meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14rpx;
}
.video-tag {
  font-size: 20rpx;
  font-weight: 600;
  border-radius: 999px;
  padding: 3rpx 16rpx;
}
.video-meta {
  font-size: 21rpx;
  color: var(--ink-soft);
}
</style>
