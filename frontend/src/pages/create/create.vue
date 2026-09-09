<template>
  <view class="page">
    <decor-blocks app="frontend" page-key="create" />
    <view class="empty-card">
      <text class="empty-icon">✚</text>
      <text class="empty-title">AI 视频生产线</text>
      <text class="empty-sub">图生视频 / 文生视频，Phase 3 建设中</text>
    </view>
    <tab-bar current="/pages/create/create" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'
import DecorBlocks from '@/components/decor-blocks/decor-blocks.vue'

export default {
  components: { TabBar, DecorBlocks },
}
</script>

<style>
.page {
  padding: 24rpx 24rpx 160rpx;
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
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
