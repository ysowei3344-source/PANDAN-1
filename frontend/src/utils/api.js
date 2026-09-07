// 前端和后端同域部署：p.rvppp.cn/ 走前端静态页，p.rvppp.cn/admin/ 由 nginx 反代到后端
const API_BASE = '/admin'

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

export function getIdentities() {
  return request('/api/identities')
}

export function getIdentity(id) {
  return request(`/api/identities/${id}`)
}

export function getIdentityVideos(id) {
  return request(`/api/identities/${id}/videos`)
}

export function getVideos(platform) {
  return request('/api/videos', platform ? { platform } : null)
}

export function getBanners() {
  return request('/api/banners')
}

export function getTodayStats() {
  return request('/api/dashboard/today')
}

export function staticUrl(path) {
  return `${API_BASE}${path}`
}
