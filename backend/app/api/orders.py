from fastapi import APIRouter, Depends, HTTPException

from .. import storage
from ..auth import get_current_user
from ..schemas import (
    AfterSalesInput,
    AfterSalesRecord,
    Customer,
    CustomerInput,
    Order,
    OrderInput,
    Product,
    ProductInput,
)

products_router = APIRouter(prefix="/api/admin/products", tags=["order-tracking"])
customers_router = APIRouter(prefix="/api/admin/customers", tags=["order-tracking"])
orders_router = APIRouter(prefix="/api/admin/orders", tags=["order-tracking"])
aftersales_router = APIRouter(prefix="/api/admin/aftersales", tags=["order-tracking"])


# ---- 产品信息 ----

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


# ---- 客户信息 ----

@customers_router.get("", response_model=list[Customer], dependencies=[Depends(get_current_user)])
def list_customers() -> list[Customer]:
    return storage.list_customers()


@customers_router.post("", response_model=Customer)
def create_customer(payload: CustomerInput, current: dict = Depends(get_current_user)) -> Customer:
    customer = storage.create_customer(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增客户", customer.name)
    return customer


@customers_router.put("/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, payload: CustomerInput, current: dict = Depends(get_current_user)) -> Customer:
    before = storage.get_customer(customer_id)
    customer = storage.update_customer(customer_id, payload.model_dump())
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    if before is not None and before.stage != customer.stage:
        storage.log_activity(
            current["id"], current["username"], "客户阶段变更",
            f"{customer.name}：{before.stage} → {customer.stage}",
        )
    else:
        storage.log_activity(current["id"], current["username"], "编辑客户", customer.name)
    return customer


@customers_router.delete("/{customer_id}")
def delete_customer(customer_id: str, current: dict = Depends(get_current_user)) -> dict:
    customer = storage.get_customer(customer_id)
    if customer is None or not storage.delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="customer not found")
    storage.log_activity(current["id"], current["username"], "删除客户", customer.name)
    return {"ok": True}


# ---- 订单信息：成交客户 × 产品 的人工匹配结果 ----

@orders_router.get("", response_model=list[Order], dependencies=[Depends(get_current_user)])
def list_orders() -> list[Order]:
    return storage.list_orders()


@orders_router.post("", response_model=Order)
def create_order(payload: OrderInput, current: dict = Depends(get_current_user)) -> Order:
    customer = storage.get_customer(payload.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    if storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    if storage.get_order_by_customer(payload.customer_id) is not None:
        raise HTTPException(status_code=400, detail="该客户已经有订单了")
    order = storage.create_order(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增订单", customer.name)
    return order


@orders_router.put("/{order_id}", response_model=Order)
def update_order(order_id: str, payload: OrderInput, current: dict = Depends(get_current_user)) -> Order:
    order = storage.update_order(order_id, payload.model_dump())
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    storage.log_activity(current["id"], current["username"], "编辑订单", order_id)
    return order


@orders_router.delete("/{order_id}")
def delete_order(order_id: str, current: dict = Depends(get_current_user)) -> dict:
    if not storage.delete_order(order_id):
        raise HTTPException(status_code=404, detail="order not found")
    storage.log_activity(current["id"], current["username"], "删除订单", order_id)
    return {"ok": True}


# ---- 售后运维：交付客户 × 产品 的人工匹配结果 ----

@aftersales_router.get("", response_model=list[AfterSalesRecord], dependencies=[Depends(get_current_user)])
def list_aftersales() -> list[AfterSalesRecord]:
    return storage.list_aftersales()


@aftersales_router.post("", response_model=AfterSalesRecord)
def create_aftersales(payload: AfterSalesInput, current: dict = Depends(get_current_user)) -> AfterSalesRecord:
    customer = storage.get_customer(payload.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    if storage.get_product(payload.product_id) is None:
        raise HTTPException(status_code=404, detail="product not found")
    if storage.get_aftersales_by_customer(payload.customer_id) is not None:
        raise HTTPException(status_code=400, detail="该客户已经有售后记录了")
    record = storage.create_aftersales(payload.model_dump())
    storage.log_activity(current["id"], current["username"], "新增售后记录", customer.name)
    return record


@aftersales_router.put("/{aftersales_id}", response_model=AfterSalesRecord)
def update_aftersales(aftersales_id: str, payload: AfterSalesInput, current: dict = Depends(get_current_user)) -> AfterSalesRecord:
    record = storage.update_aftersales(aftersales_id, payload.model_dump())
    if record is None:
        raise HTTPException(status_code=404, detail="record not found")
    storage.log_activity(current["id"], current["username"], "编辑售后记录", aftersales_id)
    return record


@aftersales_router.delete("/{aftersales_id}")
def delete_aftersales(aftersales_id: str, current: dict = Depends(get_current_user)) -> dict:
    if not storage.delete_aftersales(aftersales_id):
        raise HTTPException(status_code=404, detail="record not found")
    storage.log_activity(current["id"], current["username"], "删除售后记录", aftersales_id)
    return {"ok": True}
