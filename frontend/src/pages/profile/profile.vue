<template>
  <view class="page">
    <view class="empty-card">
      <text class="empty-icon">☺</text>
      <text class="empty-title">个人中心</text>
      <text class="empty-sub">账号设置 / 权限管理，暂未开放</text>
    </view>
    <tab-bar current="/pages/profile/profile" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'

export default {
  components: { TabBar },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 160rpx;
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}
.empty-card {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 64rpx 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  text-align: center;
}
.empty-icon {
  font-size: 56rpx;
  color: var(--accent);
}
.empty-title {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--ink);
}
.empty-sub {
  font-size: 24rpx;
  color: var(--ink-soft);
}
</style>
