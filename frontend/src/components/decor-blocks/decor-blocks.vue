<template>
  <view v-if="blocks.length" class="decor-blocks">
    <decor-block-item v-for="b in blocks" :key="b.id" :block="b" />
  </view>
</template>

<script>
import { getDecorBlocks } from '@/utils/api.js'
import DecorBlockItem from '@/components/decor-block-item/decor-block-item.vue'

export default {
  components: { DecorBlockItem },
  props: {
    app: { type: String, required: true },
    pageKey: { type: String, required: true },
  },
  data() {
    return { blocks: [] }
  },
  async mounted() {
    this.blocks = await getDecorBlocks(this.app, this.pageKey).catch(() => [])
  },
}
</script>

<style>
.decor-blocks {
  width: 100%;
  align-self: stretch;
  margin-bottom: 8rpx;
}
</style>
