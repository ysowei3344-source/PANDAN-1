<template>
  <view class="page">
    <view class="login-card">
      <text class="login-title">跟单猿</text>
      <text class="login-sub">房车矩阵中枢 · 销售跟单猿专用入口</text>
      <view class="field">
        <text class="field-label">用户名</text>
        <input class="field-input" v-model="username" placeholder="请输入用户名" />
      </view>
      <view class="field">
        <text class="field-label">密码</text>
        <input class="field-input" v-model="password" password placeholder="请输入密码" />
      </view>
      <button class="btn-primary" :loading="loading" @click="doLogin">登录</button>
      <text class="msg" :class="{ error: !!msg }">{{ msg }}</text>
    </view>
  </view>
</template>

<script>
import { login, setToken, getMe } from '@/utils/api.js'

export default {
  data() {
    return {
      username: '',
      password: '',
      msg: '',
      loading: false,
      redirect: '',
    }
  },
  onLoad(options) {
    // 从"操作"入口（比如搞订单）跳过来的会带 ?redirect=，登录成功后跳回去，
    // 不会把用户刚才想干的事弄丢；没带就是从"我的"/浏览页手动点的登录，登完回首页。
    this.redirect = (options && options.redirect) ? decodeURIComponent(options.redirect) : ''
    // 已经登录过、token 还有效就直接跳走，不用每次都重新输
    getMe()
      .then(() => uni.reLaunch({ url: this.redirect || '/pages/home/home' }))
      .catch(() => {})
  },
  methods: {
    async doLogin() {
      const username = this.username.trim()
      const password = this.password
      if (!username || !password) {
        this.msg = '请输入用户名和密码'
        return
      }
      this.loading = true
      this.msg = ''
      try {
        const res = await login(username, password)
        setToken(res.token)
        uni.reLaunch({ url: this.redirect || '/pages/home/home' })
      } catch (e) {
        this.msg = e.message
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
  box-sizing: border-box;
}
.login-card {
  width: 100%;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 56rpx 44rpx;
  display: flex;
  flex-direction: column;
}
.login-title {
  font-size: 44rpx;
  font-weight: 700;
  color: var(--ink);
}
.login-sub {
  font-size: 24rpx;
  color: var(--ink-soft);
  margin-top: 8rpx;
  margin-bottom: 44rpx;
}
.field {
  margin-bottom: 28rpx;
}
.field-label {
  font-size: 24rpx;
  color: var(--ink-soft);
  display: block;
  margin-bottom: 10rpx;
}
.field-input {
  width: 100%;
  box-sizing: border-box;
  padding: 22rpx 24rpx;
  border-radius: var(--radius-md);
  background: var(--bg);
  border: 1px solid var(--line);
  font-size: 28rpx;
  color: var(--ink);
}
.btn-primary {
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  color: #ffffff;
  border-radius: var(--radius-md);
  font-size: 30rpx;
  font-weight: 600;
  padding: 22rpx 0;
  margin-top: 12rpx;
  border: none;
}
.msg {
  font-size: 24rpx;
  color: var(--ink-soft);
  margin-top: 18rpx;
  text-align: center;
  min-height: 32rpx;
}
.msg.error {
  color: var(--danger);
}
</style>
