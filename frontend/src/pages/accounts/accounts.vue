<template>
  <view class="page">
    <view class="panel" v-for="platform in platforms" :key="platform">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">{{ platformLabel(platform) }}</text>
      </view>
      <view class="account-list">
        <view
          class="account-row"
          v-for="a in groupedAccounts[platform]"
          :key="a.id"
        >
          <view class="avatar" :class="badgeClass(platform)">{{ initial(platform) }}</view>
          <view class="account-info">
            <text class="account-name">{{ a.nickname }}</text>
            <text class="account-sub">{{ formatNum(a.video_count) }} 条视频</text>
          </view>
          <text class="account-followers">{{ formatNum(a.follower_count) }} 粉丝</text>
        </view>
      </view>
    </view>

    <tab-bar current="/pages/accounts/accounts" />
  </view>
</template>

<script>
import { getAccounts } from '@/utils/api.js'
import TabBar from '@/components/tab-bar/tab-bar.vue'

export default {
  components: { TabBar },
  data() {
    return {
      platforms: ['douyin', 'video_channel', 'xiaohongshu'],
      accounts: [],
    }
  },
  computed: {
    groupedAccounts() {
      const groups = { douyin: [], video_channel: [], xiaohongshu: [] }
      for (const a of this.accounts) {
        if (groups[a.platform]) groups[a.platform].push(a)
      }
      return groups
    },
  },
  onLoad() {
    this.load()
  },
  methods: {
    async load() {
      try {
        this.accounts = await getAccounts()
      } catch (e) {
        this.accounts = []
      }
    },
    formatNum(n) {
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
  padding: 24rpx 24rpx 160rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
.panel {
  margin-top: 20rpx;
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
.account-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.account-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 14rpx 0;
  border-bottom: 1px solid var(--line);
}
.account-row:last-child { border-bottom: none; padding-bottom: 0; }
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
.account-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4rpx;
}
.account-name {
  font-size: 27rpx;
  font-weight: 600;
  color: var(--ink);
}
.account-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.account-followers {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--ink);
}
</style>
