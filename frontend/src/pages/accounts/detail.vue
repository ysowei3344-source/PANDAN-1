<template>
  <view class="page">
    <view class="header">
      <text class="identity-name">{{ identity.name }}</text>
      <text class="identity-sub">{{ identity.phone_number }} · {{ identity.accounts.length }} 个平台绑定</text>
    </view>

    <view class="kpi-grid">
      <view class="kpi-card">
        <text class="kpi-value">{{ formatNum(identity.total_followers) }}</text>
        <text class="kpi-label">总粉丝数</text>
      </view>
      <view class="kpi-card">
        <text class="kpi-value">{{ formatNum(identity.total_videos) }}</text>
        <text class="kpi-label">总视频数</text>
      </view>
      <view class="kpi-card">
        <text class="kpi-value">¥{{ formatNum(identity.total_ad_spend) }}</text>
        <text class="kpi-label">总消耗量</text>
      </view>
      <view class="kpi-card">
        <text class="kpi-value">{{ formatNum(identity.total_customers_added) }}</text>
        <text class="kpi-label">总添加数</text>
      </view>
      <view class="kpi-card">
        <text class="kpi-value">{{ formatNum(identity.total_deals_closed) }}</text>
        <text class="kpi-label">总成交数</text>
      </view>
    </view>

    <view class="panel">
      <view class="platform-tabs">
        <view
          v-for="a in identity.accounts"
          :key="a.id"
          class="tab-chip"
          :class="{ active: activeAccountId === a.id }"
          @click="activeAccountId = a.id"
        >
          {{ platformLabel(a.platform) }}
        </view>
      </view>

      <view class="platform-row" v-if="activeAccount">
        <view class="avatar" :class="badgeClass(activeAccount.platform)">{{ initial(activeAccount.platform) }}</view>
        <view class="row-body">
          <text class="row-title">{{ platformLabel(activeAccount.platform) }} · {{ activeAccount.nickname }}</text>
          <text class="row-sub">{{ formatNum(activeAccount.video_count) }} 条视频</text>
        </view>
        <text class="row-followers">{{ formatNum(activeAccount.follower_count) }} 粉丝</text>
      </view>

      <view class="video-grid">
        <view class="video-cell" v-for="v in activeVideos" :key="v.id" @click="previewVideo(v)">
          <image class="video-cell-img" :src="staticUrl(v.poster_url)" mode="aspectFill"></image>
        </view>
        <view class="empty-hint" v-if="activeVideos.length === 0">暂无视频</view>
      </view>
    </view>

    <navigator open-type="navigateBack" class="back-link">‹ 返回矩阵号列表</navigator>
  </view>
</template>

<script>
import { getIdentity, getIdentityVideos, staticUrl } from '@/utils/api.js'

export default {
  data() {
    return {
      id: '',
      identity: { name: '', phone_number: '', accounts: [], total_followers: 0, total_videos: 0, total_ad_spend: 0, total_customers_added: 0, total_deals_closed: 0 },
      videos: [],
      activeAccountId: '',
    }
  },
  computed: {
    activeAccount() {
      return this.identity.accounts.find((a) => a.id === this.activeAccountId) || null
    },
    activeVideos() {
      return this.videos.filter((v) => v.account_id === this.activeAccountId)
    },
  },
  onLoad(query) {
    this.id = query.id
    this.load()
  },
  methods: {
    async load() {
      try {
        const [identity, videos] = await Promise.all([
          getIdentity(this.id),
          getIdentityVideos(this.id),
        ])
        this.identity = identity
        this.videos = videos
        if (identity.accounts[0]) this.activeAccountId = identity.accounts[0].id
      } catch (e) {
        // leave defaults
      }
    },
    previewVideo(v) {
      uni.previewImage({ urls: [staticUrl(v.poster_url)] })
    },
    staticUrl,
    formatNum(n) {
      if (n === undefined || n === null) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return String(n)
    },
    platformLabel(platform) {
      return { douyin: '抖音', video_channel: '视频号', xiaohongshu: '小红书' }[platform] || platform
    },
    initial(platform) {
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
  padding: 24rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.header {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: 20rpx;
}
.identity-name {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--ink);
}
.identity-sub {
  font-size: 23rpx;
  color: var(--ink-soft);
}
.kpi-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
}
.kpi-card {
  flex: 1 1 28%;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 22rpx 16rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.kpi-value {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--ink);
}
.kpi-label {
  font-size: 20rpx;
  color: var(--ink-soft);
}
.panel {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 28rpx;
}
.platform-tabs {
  display: flex;
  gap: 12rpx;
  margin-bottom: 20rpx;
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
.platform-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 16rpx 0;
  border-bottom: 1px solid var(--line);
  margin-bottom: 20rpx;
}
.avatar {
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
.badge-blue { background: var(--accent-soft); color: var(--accent); }
.badge-green { background: var(--success-soft); color: var(--success); }
.badge-pink { background: var(--danger-soft); color: var(--danger); }
.badge-dark { background: #1f2430; color: #ffffff; }
.row-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  gap: 4rpx;
}
.row-title {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--ink);
}
.row-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.row-followers {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--ink);
}
.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8rpx;
}
.video-cell {
  position: relative;
  width: 100%;
  padding-top: 177.78%;
  border-radius: 12rpx;
  background: var(--bg);
  overflow: hidden;
}
.video-cell-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.empty-hint {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 24rpx;
  color: var(--ink-soft);
  padding: 40rpx 0;
}
.back-link {
  display: block;
  text-align: center;
  margin-top: 28rpx;
  font-size: 24rpx;
  color: var(--ink-soft);
}
</style>
