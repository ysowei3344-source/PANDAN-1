// 跟单猿小程序的接口层——调用的就是 PANDAN-1 后台已有的 /api/admin/... 那一整套
// （跟 admin-console/mobile-sales 共用同一个后端、同一批账号、同一个数据库），
// 这个小程序本身不需要任何新后端接口。
//
// 小程序 wx.request 不支持相对路径（跟浏览器不一样，没有"当前页面地址"这个
// 概念可以拿来补全），必须写完整的协议+域名。ICP 备案下来、有真实 HTTPS
// 域名之后，只需要改这一个 SERVER_ORIGIN 常量。
const SERVER_ORIGIN = 'http://47.122.105.40'
const AUTH_API_BASE = `${SERVER_ORIGIN}/admin/api/admin`
const PUBLIC_API_BASE = `${SERVER_ORIGIN}/admin/api`
const STATIC_BASE = `${SERVER_ORIGIN}/admin`
const TOKEN_KEY = 'rv_admin_token'

export function staticUrl(path) {
  return `${STATIC_BASE}${path}`
}

export function getToken() {
  try {
    return uni.getStorageSync(TOKEN_KEY) || ''
  } catch (e) {
    return ''
  }
}

export function setToken(token) {
  try {
    if (token) uni.setStorageSync(TOKEN_KEY, token)
    else uni.removeStorageSync(TOKEN_KEY)
  } catch (e) {
    /* 存储不可用就算了，登录态退化成"每次都要重新登录" */
  }
}

function authRequest(path, { method = 'GET', data } = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${AUTH_API_BASE}${path}`,
      method,
      data: data || {},
      header: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.statusCode === 401) {
          // 不在这里强制跳转登录页——首页/商品/日志这些是可以先逛的，401 只是
          // "这批数据看不了"，具体怎么提示（空态文案/登录按钮）交给调用页面自己
          // 处理。真正需要登录才能做的操作走 ensureLoggedIn()。
          setToken('')
          reject(new Error('未登录'))
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const detail = res.data && res.data.detail
          reject(new Error(typeof detail === 'string' ? detail : `请求失败（${res.statusCode}）`))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络错误')),
    })
  })
}

// uni.navigateTo 不传 fail 回调的话，跳转失败（比如页面栈超过10层这种开发时
// 常见情况）会完全没有任何提示——点了跟没点一样，调试起来像是"按钮没反应"，
// 实际是跳转本身失败了。统一套一层，把失败原因用 toast 亮出来。
export function safeNavigateTo(url) {
  uni.navigateTo({
    url,
    fail: (err) => {
      uni.showToast({ title: '跳转失败：' + (err && err.errMsg ? err.errMsg : '未知错误'), icon: 'none' })
    },
  })
}

// 页面在"浏览"场景（打开首页/商品/日志列表）不用这个——没登录就让内容留空、
// 展示"登录后查看"提示。只有真正要"做操作"（新建/编辑订单、写日志、解锁口令）
// 之前才调用这个：登录有效就返回当前用户，没登录就跳转登录页（可选带
// redirectUrl，登录成功后跳回来，保留原本想做的操作）。
export async function ensureLoggedIn(redirectUrl) {
  try {
    return await getMe()
  } catch (e) {
    const url = redirectUrl ? `/pages/login/login?redirect=${encodeURIComponent(redirectUrl)}` : '/pages/login/login'
    safeNavigateTo(url)
    return null
  }
}

export function login(username, password) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${AUTH_API_BASE}/auth/login`,
      method: 'POST',
      data: { username, password },
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)
        else reject(new Error((res.data && res.data.detail) || '登录失败'))
      },
      fail: (err) => reject(new Error(err.errMsg || '网络错误')),
    })
  })
}

export function getMe() {
  return authRequest('/auth/me')
}

export function getOrders() {
  return authRequest('/orders')
}
export function createOrder(payload) {
  return authRequest('/orders', { method: 'POST', data: payload })
}
export function updateOrder(id, payload) {
  return authRequest(`/orders/${id}`, { method: 'PUT', data: payload })
}
export function deleteOrder(id) {
  return authRequest(`/orders/${id}`, { method: 'DELETE' })
}
export function verifySalesPasscode(salesUsername, passcode) {
  return authRequest('/orders/verify-sales-passcode', {
    method: 'POST',
    data: { sales_username: salesUsername, passcode },
  })
}

export function getSalesProducts() {
  return authRequest('/products')
}

export function getProductCategories() {
  return authRequest('/products/categories')
}

export function getSalesList() {
  return authRequest('/users/sales-list')
}

export function getDecorBlocks(app, pageKey) {
  return new Promise((resolve) => {
    uni.request({
      url: `${PUBLIC_API_BASE}/decor/pages/${app}/${pageKey}`,
      success: (res) => resolve((res.data && res.data.blocks) || []),
      fail: () => resolve([]),
    })
  })
}

export function getWorkLogs() {
  return authRequest('/worklogs')
}
export function createWorkLog(payload) {
  return authRequest('/worklogs', { method: 'POST', data: payload })
}
export function updateWorkLog(id, payload) {
  return authRequest(`/worklogs/${id}`, { method: 'PUT', data: payload })
}
export function deleteWorkLog(id) {
  return authRequest(`/worklogs/${id}`, { method: 'DELETE' })
}

export const CUSTOMER_STAGES = [
  { key: 'initial_chat', label: '初聊客户' },
  { key: 'deep_chat', label: '深聊客户' },
  { key: 'phone_call', label: '电话客户' },
  { key: 'video_call', label: '视频客户' },
  { key: 'car_viewing', label: '看车客户' },
  { key: 'deposit', label: '定金客户' },
  { key: 'deal_closed', label: '成交客户' },
  { key: 'delivered', label: '交付客户' },
]

export function stageLabel(key) {
  return (CUSTOMER_STAGES.find((s) => s.key === key) || {}).label || key
}

// 跟单猿业绩：不单独存数据，直接拿 orders 按 assigned_to 分组统计——跟
// admin-console「跟单猿业绩」页用的是同一套口径（本月新增/8阶段分布/成交/交付）。
export function computeSalesPerformance(orders, username) {
  const mine = orders.filter((o) => o.assigned_to === username)
  const now = new Date()
  const monthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const newThisMonth = mine.filter((o) => String(o.created_at || '').slice(0, 7) === monthKey).length
  const stageCounts = {}
  CUSTOMER_STAGES.forEach((s) => {
    stageCounts[s.key] = 0
  })
  mine.forEach((o) => {
    if (stageCounts[o.stage] != null) stageCounts[o.stage]++
  })
  const dealOrders = mine.filter((o) => o.stage === 'deal_closed' || o.stage === 'delivered')
  const deliveredCount = mine.filter((o) => o.stage === 'delivered').length
  return {
    total: mine.length,
    newThisMonth,
    stageCounts,
    dealCount: dealOrders.length,
    dealAmount: dealOrders.reduce((sum, o) => sum + (o.amount || 0), 0),
    deliveredCount,
  }
}

// 模块级单例，不放在某个页面的 data 里——首页/日志之间口令解锁状态得跨页面
// 记住，同一次小程序会话里解锁一次，其它页面也认。
export const unlockedSalesGroups = new Set()

export function isSalesGroupUnlocked(currentUser, salesName) {
  // 没登录就什么都别放开——以前这里 !currentUser 直接判"已解锁"是因为旧版本
  // 强制登录、currentUser 不可能是 null；现在首页可以不登录直接逛，得补上这个判断。
  return (
    !!currentUser &&
    (currentUser.role === 'super_admin' || salesName === currentUser.username || unlockedSalesGroups.has(salesName))
  )
}

export function getSalesNames(orders, salesUsers) {
  const names = new Set(salesUsers.map((u) => u.username))
  orders.forEach((o) => {
    if (o.assigned_to) names.add(o.assigned_to)
  })
  return Array.from(names)
}

export function formatNum(n) {
  if (n === undefined || n === null) return '0'
  const num = Number(n) || 0
  if (Math.abs(num) >= 10000) return (num / 10000).toFixed(1) + '万'
  return Math.round(num).toLocaleString('zh-CN')
}
