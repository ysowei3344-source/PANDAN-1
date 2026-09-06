<template>
  <view class="tab-bar">
    <view
      v-for="item in leftItems"
      :key="item.path"
      class="tab-item"
      @click="go(item.path)"
    >
      <text class="tab-icon" :class="{ active: current === item.path }">{{ item.icon }}</text>
      <text class="tab-text" :class="{ active: current === item.path }">{{ item.label }}</text>
    </view>

    <view class="tab-item create-item" @click="go(createItem.path)">
      <view class="create-btn">
        <text class="create-icon">{{ createItem.icon }}</text>
      </view>
      <text class="tab-text" :class="{ active: current === createItem.path }">{{ createItem.label }}</text>
    </view>

    <view
      v-for="item in rightItems"
      :key="item.path"
      class="tab-item"
      @click="go(item.path)"
    >
      <text class="tab-icon" :class="{ active: current === item.path }">{{ item.icon }}</text>
      <text class="tab-text" :class="{ active: current === item.path }">{{ item.label }}</text>
    </view>
  </view>
</template>

<script>
const ITEMS = [
  { path: '/pages/index/index', label: '首页', icon: '⌂' },
  { path: '/pages/accounts/accounts', label: '矩阵号', icon: '▤' },
  { path: '/pages/create/create', label: '创作', icon: '✚' },
  { path: '/pages/benchmark/benchmark', label: '对标号', icon: '◎' },
  { path: '/pages/profile/profile', label: '我的', icon: '☺' },
]

export default {
  props: {
    current: { type: String, default: '/pages/index/index' },
  },
  data() {
    return {
      leftItems: ITEMS.slice(0, 2),
      createItem: ITEMS[2],
      rightItems: ITEMS.slice(3),
    }
  },
  methods: {
    go(path) {
      if (path === this.current) return
      uni.switchTab({ url: path })
    },
  },
}
</script>

<style>
.tab-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 116rpx;
  padding-bottom: env(safe-area-inset-bottom);
  background: var(--card-bg, #ffffff);
  box-shadow: 0 -4rpx 20rpx rgba(31, 58, 94, 0.08);
  display: flex;
  align-items: flex-start;
  z-index: 100;
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
  padding-top: 12rpx;
}
.tab-icon {
  font-size: 36rpx;
  color: var(--ink-soft, #8a94a6);
}
.tab-icon.active {
  color: var(--accent, #3e7bfa);
}
.tab-text {
  font-size: 20rpx;
  color: var(--ink-soft, #8a94a6);
}
.tab-text.active {
  color: var(--accent, #3e7bfa);
}
.create-item {
  position: relative;
}
.create-btn {
  width: 84rpx;
  height: 84rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--hero-from, #5b93f5), var(--hero-to, #1e4e96));
  box-shadow: 0 8rpx 20rpx rgba(30, 78, 150, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -48rpx;
}
.create-icon {
  font-size: 40rpx;
  color: #ffffff;
}
</style>
