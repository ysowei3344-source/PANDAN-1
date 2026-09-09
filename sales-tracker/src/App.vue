<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
}
</script>

<style>
/* 全局设计令牌：色板 / 圆角 / 阴影，各页面共用——跟 房车矩阵中枢 消费端小程序
   （frontend/ 项目）用的是同一套色值，两个独立小程序视觉风格保持一致 */
page {
  --bg: #eef4fc;
  --card-bg: #ffffff;
  --ink: #1a2b3d;
  --ink-soft: #8a94a6;
  --line: #e7edf6;

  --accent: #3e7bfa;
  --accent-soft: #e4eefd;
  --hero-from: #5b93f5;
  --hero-to: #1e4e96;

  --danger: #f35b6e;
  --danger-soft: #fde3e7;
  --success: #22b573;
  --success-soft: #e1f7e8;
  --warning: #ffa53e;
  --warning-soft: #ffeedb;

  --radius-lg: 32rpx;
  --radius-md: 20rpx;
  --shadow: 0 8rpx 28rpx rgba(31, 58, 94, 0.08);

  background: var(--bg);
  color: var(--ink);
}
</style>
