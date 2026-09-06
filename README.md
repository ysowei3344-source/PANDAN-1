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
- `GET /api/accounts` — 矩阵账号列表
- `GET /api/accounts/{id}/videos` — 单账号视频列表
- `GET /api/videos?platform=douyin` — 按平台筛选视频

## 前端

```bash
cd frontend
npm install
npm run dev:h5          # 本地预览 H5
npm run dev:mp-weixin   # 编译到微信小程序，用微信开发者工具打开 dist/dev/mp-weixin
```

`src/utils/api.js` 里配置了后端地址，开发阶段直连 ECS 公网 IP，备案 + HTTPS 就绪后切换成 `https://p.rvppp.cn`。

## 部署

`.github/workflows/deploy.yml`：push 到 `main` 后，GitHub Actions 把 `backend/` 通过 rsync 传到 ECS（服务器本身连不上 github.com，所以不采用 git pull 的方式），再重启 `pandan1-backend` systemd 服务。

需要在 GitHub 仓库 Settings → Secrets and variables → Actions 配置：

| Secret 名        | 说明                              |
|------------------|-----------------------------------|
| `ECS_HOST`       | 服务器公网 IP                     |
| `ECS_USER`       | SSH 登录用户名（如 root）         |
| `ECS_PORT`       | SSH 端口（默认 22）               |
| `ECS_SSH_KEY`    | SSH 私钥（配对的公钥需加到服务器 `~/.ssh/authorized_keys`）|
| `ECS_TARGET_DIR` | 服务器上代码所在目录（如 `/root/PANDAN-1`）|

前端目前手动构建部署（H5 静态文件传到服务器由 nginx 托管，小程序通过微信开发者工具上传审核），暂未纳入自动化。
