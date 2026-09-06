<template>
  <view class="page">
    <view class="header">
      <text class="title">矩阵数据看板</text>
      <text class="subtitle">{{ loadError ? '接口未连接，显示为空' : '数据来自房车矩阵中枢 API' }}</text>
    </view>

    <view class="stat-row">
      <view class="stat-card">
        <text class="stat-num">{{ summary.total_accounts }}</text>
        <text class="stat-label">矩阵账号</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ formatNum(summary.total_plays) }}</text>
        <text class="stat-label">总播放</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ formatNum(summary.total_followers) }}</text>
        <text class="stat-label">总粉丝</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ summary.total_videos }}</text>
        <text class="stat-label">视频数</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">分平台数据</text>
      <view class="platform-list">
        <view class="platform-row" v-for="p in summary.by_platform" :key="p.platform">
          <text class="platform-name">{{ platformLabel(p.platform) }}</text>
          <text class="platform-meta">{{ p.account_count }} 个账号</text>
          <text class="platform-meta">{{ formatNum(p.total_plays) }} 播放</text>
          <text class="platform-meta">{{ formatNum(p.total_followers) }} 粉丝</text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">播放量 Top 视频</text>
      <view class="video-list">
        <view class="video-row" v-for="v in summary.top_videos" :key="v.id">
          <text class="video-title">{{ v.title }}</text>
          <view class="video-meta-row">
            <text class="video-tag">{{ platformLabel(v.platform) }}</text>
            <text class="video-meta">播放 {{ formatNum(v.plays) }}</text>
            <text class="video-meta">赞 {{ formatNum(v.likes) }}</text>
            <text class="video-meta">评 {{ formatNum(v.comments) }}</text>
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
  },
}
</script>

<style>
.page {
  padding: 24rpx;
  background: #f0efe6;
  min-height: 100vh;
  box-sizing: border-box;
}
.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 24rpx;
}
.title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1c2321;
}
.subtitle {
  font-size: 24rpx;
  color: #7a8079;
  margin-top: 6rpx;
}
.stat-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.stat-card {
  flex: 1 1 40%;
  background: #e6e4d6;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.stat-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #1f6f4f;
}
.stat-label {
  font-size: 22rpx;
  color: #7a8079;
}
.section {
  margin-top: 40rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1c2321;
}
.platform-list, .video-list {
  margin-top: 16rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.platform-row {
  background: #e6e4d6;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  align-items: baseline;
}
.platform-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #1c2321;
  width: 140rpx;
}
.platform-meta {
  font-size: 22rpx;
  color: #7a8079;
}
.video-row {
  background: #e6e4d6;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.video-title {
  font-size: 26rpx;
  color: #1c2321;
  font-weight: 500;
}
.video-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.video-tag {
  font-size: 20rpx;
  color: #0f3d2b;
  background: #d8e8de;
  border-radius: 999px;
  padding: 2rpx 14rpx;
}
.video-meta {
  font-size: 20rpx;
  color: #7a8079;
}
</style>
