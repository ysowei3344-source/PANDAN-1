from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import get_current_user
from ..schemas import DecorBlock, DecorPage, DecorPageInput

# 小程序前台"页面装修"：每个 app 下面固定几个可装修页面，运营在后台按
# 组件拼装 + 排序，小程序页面开机时拉取这份配置动态渲染。页面集合是固定的
# （新增一个可装修页面本身就是代码改动），所以直接写死在这里当作唯一数据源，
# 管理后台从 /api/admin/decor/apps 读取，不用在前端再抄一遍。
PAGE_REGISTRY: dict[str, dict] = {
    "frontend": {
        "label": "消费端小程序（房车矩阵中枢）",
        "pages": [
            {"page_key": "home", "label": "首页"},
            {"page_key": "accounts", "label": "矩阵号"},
            {"page_key": "create", "label": "创作"},
            {"page_key": "benchmark", "label": "对标号"},
            {"page_key": "profile", "label": "我的"},
        ],
    },
    "sales-tracker": {
        "label": "跟单猿小程序",
        "pages": [
            {"page_key": "home", "label": "首页"},
            {"page_key": "products", "label": "商品库"},
            {"page_key": "logs", "label": "日志"},
            {"page_key": "profile", "label": "我的"},
        ],
    },
}

# 首页这类页面本来就有一批硬编码的功能模块（轮播图/矩阵账号/团队业绩……），
# 这些模块本身绑定真实数据、不能像装修组件一样自由增删，但"要不要显示/排在
# 第几个/标题文案"应该能在后台调——所以把它们也塞进同一份 blocks 列表里，
# type 用 builtin_ 前缀区分。第一次访问（storage 里还没存过、updated_at 是
# None）时用这份默认列表兜底，代表的就是"今天线上现在长什么样"，管理员不动
# 手的话页面效果完全不变；一旦保存过一次，就完全以存的内容为准。
DEFAULT_BLOCKS: dict[tuple[str, str], list[dict]] = {
    ("frontend", "home"): [
        {"id": "builtin-banner", "type": "builtin_banner", "enabled": True, "props": {}},
        {"id": "builtin-matrix-accounts", "type": "builtin_matrix_accounts", "enabled": True, "props": {"title": "矩阵账号"}},
        {"id": "builtin-today-stats", "type": "builtin_today_stats", "enabled": True, "props": {"title": "今日数据分析"}},
        {"id": "builtin-video-feed", "type": "builtin_video_feed", "enabled": True, "props": {}},
    ],
    ("sales-tracker", "home"): [
        {"id": "builtin-hero", "type": "builtin_hero", "enabled": True, "props": {}},
        {"id": "builtin-sales-performance", "type": "builtin_sales_performance", "enabled": True, "props": {"title": "跟单猿数据"}},
        {"id": "builtin-customer-list", "type": "builtin_customer_list", "enabled": True, "props": {"title": "客户流水单"}},
    ],
}

public_router = APIRouter(prefix="/api/decor", tags=["decor"])
admin_router = APIRouter(prefix="/api/admin/decor", tags=["decor"])


def _validate_page(app: str, page_key: str) -> None:
    reg = PAGE_REGISTRY.get(app)
    if not reg or not any(p["page_key"] == page_key for p in reg["pages"]):
        raise HTTPException(status_code=404, detail="unknown app/page")


def _with_defaults(app: str, page_key: str, page: DecorPage) -> DecorPage:
    if page.updated_at is None:
        defaults = DEFAULT_BLOCKS.get((app, page_key))
        if defaults:
            page.blocks = [DecorBlock(**b) for b in defaults]
    return page


@admin_router.get("/apps")
def admin_list_apps(current: dict = Depends(get_current_user)) -> list[dict]:
    return [{"app": app, **reg} for app, reg in PAGE_REGISTRY.items()]


@admin_router.get("/pages/{app}/{page_key}", response_model=DecorPage)
def admin_get_page(app: str, page_key: str, current: dict = Depends(get_current_user)) -> DecorPage:
    _validate_page(app, page_key)
    return _with_defaults(app, page_key, storage.get_decor_page(app, page_key))


@admin_router.put("/pages/{app}/{page_key}", response_model=DecorPage)
def admin_save_page(
    app: str, page_key: str, payload: DecorPageInput, current: dict = Depends(get_current_user)
) -> DecorPage:
    _validate_page(app, page_key)
    page = storage.save_decor_page(app, page_key, [b.model_dump() for b in payload.blocks])
    storage.log_activity(current["id"], current["username"], "编辑页面装修", f"{app}/{page_key}")
    return page


@public_router.get("/pages/{app}/{page_key}", response_model=DecorPage)
def public_get_page(app: str, page_key: str) -> DecorPage:
    _validate_page(app, page_key)
    page = _with_defaults(app, page_key, storage.get_decor_page(app, page_key))
    page.blocks = [b for b in page.blocks if b.enabled]
    return page
