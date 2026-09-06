// Phase 1 开发期先直连 ECS 公网 IP，备案 + HTTPS 就绪后切换成 https://p.rvppp.cn
const API_BASE = 'http://47.122.105.40:8000'

function request(path, params) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${path}`,
      data: params || {},
      success: (res) => resolve(res.data),
      fail: reject,
    })
  })
}

export function getDashboardSummary() {
  return request('/api/dashboard/summary')
}

export function getAccounts() {
  return request('/api/accounts')
}

export function getVideos(platform) {
  return request('/api/videos', platform ? { platform } : null)
}
