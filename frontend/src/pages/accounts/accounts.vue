<template>
  <view class="page">
    <decor-blocks app="frontend" page-key="accounts" />

    <view class="panel">
      <view class="panel-head">
        <view class="head-bar"></view>
        <text class="panel-title">矩阵号</text>
        <text class="panel-sub">{{ identities.length }} 个矩阵号</text>
      </view>
      <view class="identity-list">
        <view
          class="identity-row"
          v-for="i in identities"
          :key="i.id"
          @click="goDetail(i.id)"
        >
          <view class="avatar">{{ i.name[0] }}</view>
          <view class="identity-info">
            <text class="identity-name">{{ i.name }}</text>
            <text class="identity-sub" v-if="i.phone_number">{{ i.phone_number }}</text>
            <view class="platform-tags">
              <text
                class="mini-tag"
                :class="badgeClass(a.platform)"
                v-for="a in i.accounts"
                :key="a.id"
              >{{ initial(a.platform) }}</text>
            </view>
          </view>
          <view class="identity-stats">
            <text class="stat-num">{{ formatNum(i.total_followers) }}</text>
            <text class="stat-label">总粉丝</text>
          </view>
          <text class="chevron">›</text>
        </view>
      </view>
    </view>

    <tab-bar current="/pages/accounts/accounts" />
  </view>
</template>

<script>
import { getIdentities } from '@/utils/api.js'
import TabBar from '@/components/tab-bar/tab-bar.vue'
import DecorBlocks from '@/components/decor-blocks/decor-blocks.vue'

export default {
  components: { TabBar, DecorBlocks },
  data() {
    return {
      identities: [],
    }
  },
  onLoad() {
    this.load()
  },
  methods: {
    async load() {
      try {
        this.identities = await getIdentities()
      } catch (e) {
        this.identities = []
      }
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/accounts/detail?id=${id}` })
    },
    formatNum(n) {
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return String(n)
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
  flex: 1;
}
.panel-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.identity-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.identity-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 14rpx 0;
  border-bottom: 1px solid var(--line);
}
.identity-row:last-child { border-bottom: none; padding-bottom: 0; }
.avatar {
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 600;
  flex-shrink: 0;
  background: var(--accent-soft);
  color: var(--accent);
}
.identity-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  gap: 6rpx;
}
.identity-name {
  font-size: 27rpx;
  font-weight: 600;
  color: var(--ink);
}
.identity-sub {
  font-size: 21rpx;
  color: var(--ink-soft);
}
.platform-tags {
  display: flex;
  gap: 8rpx;
}
.mini-tag {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18rpx;
  font-weight: 600;
}
.badge-blue { background: var(--accent-soft); color: var(--accent); }
.badge-green { background: var(--success-soft); color: var(--success); }
.badge-pink { background: var(--danger-soft); color: var(--danger); }
.badge-dark { background: #1f2430; color: #ffffff; }
.identity-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2rpx;
  flex-shrink: 0;
}
.stat-num {
  font-size: 28rpx;
  font-weight: 700;
  color: var(--ink);
}
.stat-label {
  font-size: 20rpx;
  color: var(--ink-soft);
}
.chevron {
  color: var(--ink-soft);
  font-size: 28rpx;
  flex-shrink: 0;
}
</style>
