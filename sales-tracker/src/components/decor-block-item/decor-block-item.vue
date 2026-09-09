<template>
  <view>
    <image
      v-if="block.type === 'image' && block.props.image_url"
      class="decor-image"
      :class="'radius-' + (block.props.radius || 'md')"
      :src="staticUrl(block.props.image_url)"
      mode="widthFix"
      @click="onLink(block.props.link_url)"
    ></image>

    <view v-else-if="block.type === 'grid_nav'" class="decor-grid">
      <view
        class="decor-grid-item"
        v-for="(it, idx) in gridItems"
        :key="idx"
        @click="onLink(it.link_url)"
      >
        <image v-if="it.icon_url" class="decor-grid-icon" :src="staticUrl(it.icon_url)" mode="aspectFit"></image>
        <text class="decor-grid-text">{{ it.text }}</text>
      </view>
    </view>

    <view v-else-if="block.type === 'notice' && block.props.text" class="decor-notice">
      <image v-if="block.props.icon_url" class="decor-notice-icon" :src="staticUrl(block.props.icon_url)" mode="aspectFit"></image>
      <text class="decor-notice-text">{{ block.props.text }}</text>
    </view>

    <view v-else-if="block.type === 'rich_text'" class="decor-richtext">
      <text v-if="block.props.title" class="decor-richtext-title">{{ block.props.title }}</text>
      <text class="decor-richtext-content">{{ block.props.content }}</text>
    </view>

    <view v-else-if="block.type === 'spacer'" :style="{ height: (block.props.height || 24) + 'rpx' }"></view>

    <view v-else-if="block.type === 'divider'" class="decor-divider"></view>
  </view>
</template>

<script>
import { staticUrl } from '@/utils/api.js'

export default {
  props: {
    block: { type: Object, required: true },
  },
  computed: {
    gridItems() {
      return (this.block.props.items || []).filter((it) => it.text || it.icon_url)
    },
  },
  methods: {
    staticUrl,
    onLink(url) {
      if (!url) return
      uni.switchTab({ url, fail: () => uni.navigateTo({ url, fail: () => {} }) })
    },
  },
}
</script>

<style>
.decor-image {
  width: 100%;
  display: block;
  margin-bottom: 20rpx;
}
.decor-image.radius-md {
  border-radius: var(--radius-md);
}
.decor-image.radius-lg {
  border-radius: var(--radius-lg);
}
.decor-grid {
  display: flex;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 24rpx 12rpx;
  margin-bottom: 20rpx;
}
.decor-grid-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}
.decor-grid-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 16rpx;
  background: var(--accent-soft);
}
.decor-grid-text {
  font-size: 21rpx;
  color: var(--ink);
}
.decor-notice {
  display: flex;
  align-items: center;
  gap: 14rpx;
  background: #fff7e0;
  border-radius: var(--radius-md);
  padding: 16rpx 22rpx;
  margin-bottom: 20rpx;
}
.decor-notice-icon {
  width: 32rpx;
  height: 32rpx;
  flex-shrink: 0;
}
.decor-notice-text {
  font-size: 22rpx;
  color: #8a6d1a;
  flex: 1;
}
.decor-richtext {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.decor-richtext-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--ink);
}
.decor-richtext-content {
  font-size: 24rpx;
  color: var(--ink-soft);
  line-height: 1.6;
}
.decor-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.06);
  margin: 20rpx 0;
}
</style>
