# PANDAN-1

Python 项目，通过 GitHub Actions 自动部署到阿里云 ECS。

## 部署流程

1. 本地 push 到 `main` 分支
2. GitHub Actions 触发 `.github/workflows/deploy.yml`
3. Actions 通过 SSH 登录 ECS，执行 `git pull` + 安装依赖

## 需要在 GitHub 仓库 Settings → Secrets and variables → Actions 中配置

| Secret 名        | 说明                              |
|------------------|-----------------------------------|
| `ECS_HOST`       | 服务器公网 IP                     |
| `ECS_USER`       | SSH 登录用户名（如 root）         |
| `ECS_PORT`       | SSH 端口（默认 22）               |
| `ECS_SSH_KEY`    | SSH 私钥（配对的公钥需加到服务器 `~/.ssh/authorized_keys`）|
| `ECS_TARGET_DIR` | 服务器上代码所在目录              |

## 服务器初始化（首次手动执行一次）

```bash
git clone https://github.com/ysowei3344-source/PANDAN-1.git /path/to/target
cd /path/to/target
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
