from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import MASTER_PASSCODE, get_current_user, verify_password
from ..schemas import Order, OrderInput, Product, ProductInput, VerifySalesPasscodeInput

products_router = APIRouter(prefix="/api/admin/products", tags=["order-tracking"])
orders_router = APIRouter(prefix="/api/admin/orders", tags=["order-tracking"])


# ---- 商品信息 ----

@products_router.get("", response_model=list[Product], dependencies=[Depends(get_current_user)])
def list_products() -> list[Product]:
    return storage.list_products()


@products_router.post("", response_model=Product)
def create_product(payload: ProductInput, current: dict = Depends(get_current_user)) -> Product:
    product = storage.create_product(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增产品", product.name)
    return product


@products_router.put("/{product_id}", response_model=Product)
def update_product(product_id: str, payload: ProductInput, current: dict = Depends(get_current_user)) -> Product:
    product = storage.update_product(product_id, payload.model_dump())
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    storage.log_activity(current["id"], current["username"], "编辑产品", product.name)
    return product


@products_router.delete("/{product_id}")
def delete_product(product_id: str, current: dict = Depends(get_current_user)) -> dict:
    product = storage.get_product(product_id)
    if product is None or not storage.delete_product(product_id):
        raise HTTPException(status_code=404, detail="product not found")
    storage.log_activity(current["id"], current["username"], "删除产品", product.name)
    return {"ok": True}


# ---- 订单信息 ----
# 销售直接录入客户信息 + 匹配商品来创建一条订单，1-8 阶段之后在同一条记录上
# 调整，没有"先建客户、成交了才建订单"的两段式流程。每条订单必须归属一个
# 销售 (assigned_to)，不允许留空。

@orders_router.get("", response_model=list[Order], dependencies=[Depends(get_current_user)])
def list_orders() -> list[Order]:
    return storage.list_orders()


@orders_router.post("/verify-sales-passcode")
def verify_sales_passcode(payload: VerifySalesPasscodeInput, current: dict = Depends(get_current_user)) -> dict:
    """Unlocks another 销售's order details in the grouped list. Reuses the
    same passcode a 销售 already has for their 矩阵号详情页 gate (set in
    内部账号管理) — one passcode per salesperson, matched by username, plus
    the super_admin 万能码 override, same shape as
    identities.verify_identity_passcode."""
    if payload.passcode == MASTER_PASSCODE:
        storage.log_activity(current["id"], current["username"], "订单口令验证成功（万能码）", payload.sales_username)
        return {"ok": True}

    target = storage.get_user_by_username(payload.sales_username)
    if target and target.get("passcode_hash") and verify_password(payload.passcode, target["passcode_salt"], target["passcode_hash"]):
        storage.log_activity(current["id"], current["username"], "订单口令验证成功", payload.sales_username)
        return {"ok": True}

    storage.log_activity(current["id"], current["username"], "订单口令验证失败", payload.sales_username)
    raise HTTPException(status_code=403, detail="口令不正确")


@orders_router.post("", response_model=Order)
def create_order(payload: OrderInput, current: dict = Depends(get_current_user)) -> Order:
    if not payload.assigned_to.strip():
        raise HTTPException(status_code=400, detail="请选择归属销售")
    if payload.product_id and storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    order = storage.create_order(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增订单", f"{order.name}（{order.assigned_to}）")
    return order


@orders_router.put("/{order_id}", response_model=Order)
def update_order(order_id: str, payload: OrderInput, current: dict = Depends(get_current_user)) -> Order:
    if not payload.assigned_to.strip():
        raise HTTPException(status_code=400, detail="请选择归属销售")
    if payload.product_id and storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    before = storage.get_order(order_id)
    order = storage.update_order(order_id, payload.model_dump())
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    if before is not None and before.stage != order.stage:
        storage.log_activity(
            current["id"], current["username"], "订单阶段变更",
            f"{order.name}：{before.stage} → {order.stage}",
        )
    else:
        storage.log_activity(current["id"], current["username"], "编辑订单", order.name)
    return order


@orders_router.delete("/{order_id}")
def delete_order(order_id: str, current: dict = Depends(get_current_user)) -> dict:
    order = storage.get_order(order_id)
    if order is None or not storage.delete_order(order_id):
        raise HTTPException(status_code=404, detail="order not found")
    storage.log_activity(current["id"], current["username"], "删除订单", order.name)
    return {"ok": True}
