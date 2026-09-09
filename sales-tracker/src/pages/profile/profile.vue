<template>
  <view class="page">
    <decor-blocks app="sales-tracker" page-key="profile" />

    <view class="login-prompt" v-if="!currentUser">
      <text class="login-prompt-icon">☺</text>
      <text class="login-prompt-title">还没有登录</text>
      <button class="btn-primary login-prompt-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <view class="profile-card">
        <image v-if="currentUser.avatar_url" class="avatar" :src="staticUrl(currentUser.avatar_url)" mode="aspectFill"></image>
        <view v-else class="avatar placeholder">{{ initial }}</view>
        <text class="username">{{ currentUser.username }}</text>
        <text class="role-badge">{{ currentUser.role === 'super_admin' ? '超级管理员' : '销售跟单猿' }}</text>
      </view>

      <view class="panel">
        <view class="row" @click="goHome">
          <text class="row-label">首页</text>
          <text class="chevron">›</text>
        </view>
        <view class="row" @click="goOrderList">
          <text class="row-label">{{ currentUser.role === 'super_admin' ? '全部订单' : '我的订单' }}</text>
          <text class="chevron">›</text>
        </view>
        <view class="row" @click="goLogs">
          <text class="row-label">我的日志</text>
          <text class="chevron">›</text>
        </view>
      </view>

      <button class="btn-logout" @click="onLogout">退出登录</button>
    </template>

    <tab-bar current="/pages/profile/profile" />
  </view>
</template>

<script>
import TabBar from '@/components/tab-bar/tab-bar.vue'
import DecorBlocks from '@/components/decor-blocks/decor-blocks.vue'
import { staticUrl, getMe, setToken, safeNavigateTo } from '@/utils/api.js'

export default {
  components: { TabBar, DecorBlocks },
  data() {
    return {
      currentUser: null,
    }
  },
  computed: {
    initial() {
      return this.currentUser && this.currentUser.username ? this.currentUser.username[0] : '?'
    },
  },
  onShow() {
    this.loadMe()
  },
  methods: {
    staticUrl,
    async loadMe() {
      try {
        this.currentUser = await getMe()
      } catch (e) {
        this.currentUser = null
      }
    },
    goLogin() {
      safeNavigateTo('/pages/login/login')
    },
    goHome() {
      uni.switchTab({ url: '/pages/home/home' })
    },
    goLogs() {
      uni.switchTab({ url: '/pages/logs/logs' })
    },
    goOrderList() {
      safeNavigateTo('/pages/order-list/order-list')
    },
    onLogout() {
      uni.showModal({
        title: '确定退出登录吗？',
        success: (res) => {
          if (!res.confirm) return
          setToken('')
          this.currentUser = null
        },
      })
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
.login-prompt {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 80rpx 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 14rpx;
}
.login-prompt-icon {
  font-size: 56rpx;
  color: var(--accent);
}
.login-prompt-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--ink);
}
.login-prompt-btn {
  margin-top: 20rpx;
  width: 100%;
  border: none;
  border-radius: var(--radius-md);
  font-size: 27rpx;
  font-weight: 600;
  padding: 20rpx 0;
}
.btn-primary {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
}
.profile-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 48rpx 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14rpx;
}
.avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: var(--accent-soft);
}
.avatar.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  font-weight: 700;
  color: var(--accent);
}
.username {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--ink);
  margin-top: 8rpx;
}
.role-badge {
  font-size: 21rpx;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 4rpx 20rpx;
  border-radius: 999px;
}
.panel {
  margin-top: 24rpx;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 28rpx;
  border-bottom: 1px solid var(--line);
}
.row:last-child {
  border-bottom: none;
}
.row-label {
  font-size: 27rpx;
  color: var(--ink);
}
.chevron {
  font-size: 30rpx;
  color: var(--ink-soft);
}
.btn-logout {
  margin-top: 40rpx;
  background: var(--danger-soft);
  color: var(--danger);
  border-radius: var(--radius-md);
  font-size: 28rpx;
  font-weight: 600;
  padding: 22rpx 0;
  border: none;
}
</style>
