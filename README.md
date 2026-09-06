# PANDAN-1 — 房车矩阵中枢

房车短视频矩阵运营系统。Phase 1（数据采集与统计看板）骨架。

## 目录结构

```
backend/    FastAPI 服务，提供矩阵账号 / 视频数据的统计接口
frontend/   uni-app (Vue3) 项目，一套代码出 Web / H5 / 微信小程序
```

## 后端

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

当前用 `app/mock_data.py` 里的示例数据，等抓取管道接入后替换为真实数据源，接口契约不变。

接口一览：
- `GET /api/health`
- `GET /api/dashboard/summary` — 汇总看板数据
- `GET /api/dashboard/today` — 今日全平台数据（发布数/曝光/私信/加微信）
- `GET /api/accounts` — 矩阵账号列表
- `GET /api/accounts/{id}/videos` — 单账号视频列表
- `GET /api/videos?platform=douyin` — 按平台筛选视频
- `GET /api/banners` — 首页轮播图（数据来自 `app/data/banners.json`，由发布后台维护）

轮播图发布后台（写接口，需要 `X-Admin-Token` 请求头）：
- `GET/POST /api/admin/banners`，`PUT/DELETE /api/admin/banners/{id}`
- `POST /api/admin/upload` — 上传图片，返回 `url`

`ADMIN_TOKEN` 从环境变量读取（本地开发用 `backend/.env`，服务器上由 systemd 的 `EnvironmentFile` 加载），没配置的话所有 `/api/admin/*` 请求都会 401，`.env` 不进 git。

对应的管理页面在 `admin-console/index.html`（纯静态单文件，不走 uni-app 构建），部署时直接把它扔到 `/var/www/p.rvppp.cn/console/`，通过 `p.rvppp.cn/console/` 访问，进去先输一遍令牌。

## 前端

```bash
cd frontend
npm install
npm run dev:h5          # 本地预览 H5
npm run dev:mp-weixin   # 编译到微信小程序，用微信开发者工具打开 dist/dev/mp-weixin
```

`src/utils/api.js` 里的 `API_BASE` 是 `/admin`——前端和后端同域部署，`p.rvppp.cn/` 走前端静态页，`p.rvppp.cn/admin/` 由 nginx 反代到后端。

## 部署

线上地址：`p.rvppp.cn`

- `/` → nginx 直接托管 `frontend` 构建出的 H5 静态文件（`/var/www/p.rvppp.cn`）
- `/admin/` → nginx 反代到 `127.0.0.1:8000`（`backend` 的 FastAPI 服务，去掉 `/admin` 前缀）

nginx 配置见 `deploy/p.rvppp.cn.conf`，后端 systemd 服务见 `deploy/pandan1-backend.service`（都需要手动应用到服务器，不是自动同步的）。

`.github/workflows/deploy.yml`：push 到 `main` 后，GitHub Actions 把 `backend/` 通过 rsync 传到 ECS（服务器本身连不上 github.com，所以不采用 git pull 的方式），再重启 `pandan1-backend` systemd 服务。

需要在 GitHub 仓库 Settings → Secrets and variables → Actions 配置：

| Secret 名        | 说明                              |
|------------------|-----------------------------------|
| `ECS_HOST`       | 服务器公网 IP                     |
| `ECS_USER`       | SSH 登录用户名（如 root）         |
| `ECS_PORT`       | SSH 端口（默认 22）               |
| `ECS_SSH_KEY`    | SSH 私钥（配对的公钥需加到服务器 `~/.ssh/authorized_keys`）|
| `ECS_TARGET_DIR` | 服务器上代码所在目录（如 `/root/PANDAN-1`）|

前端目前手动构建部署（`npx uni build` 生成 H5 产物后传到 `/var/www/p.rvppp.cn`，小程序包通过微信开发者工具上传审核），暂未纳入自动化。
