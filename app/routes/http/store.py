from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from app.dependencies.auth import basic_permission_dependency
from app.models.store import Product, ProductImage
from app.core.db.sessionmanager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.store import serialize_product
from app.utils import media as media_utils
from app.config.base import MEDIA_PRODUCTS
from sqlalchemy.orm import joinedload
from app.models.users import User
from sqlalchemy import select
from decimal import Decimal
from uuid import UUID
import json


store_routes = APIRouter(prefix="/store", tags=["Store"])


@store_routes.get("/productos/store/")
async def list_my_products(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(basic_permission_dependency([])),
):
    stmt = (
        select(Product)
        .where(Product.user_id == user.id)
        .options(
            joinedload(Product.images),
            joinedload(Product.reviews),
            joinedload(Product.user)
        )
    )
    result = await db.execute(stmt)
    products = result.scalars().all()

    return [serialize_product(p) for p in products]


@store_routes.get("/productos")
async def list_products(db: AsyncSession = Depends(get_session)):
    stmt = select(Product).options(
        joinedload(Product.images),
        joinedload(Product.reviews),
        joinedload(Product.user)
    )
    result = await db.execute(stmt)
    products = result.scalars().all()

    return [serialize_product(p) for p in products]


@store_routes.get("/producto/{product_uuid}")
async def get_product(product_uuid: UUID, db: AsyncSession = Depends(get_session)):
    stmt = (
        select(Product)
        .where(Product.uuid == product_uuid)
        .options(
            joinedload(Product.images),
            joinedload(Product.reviews),
            joinedload(Product.user)
        )
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(404, "Product not found")

    return serialize_product(product)


@store_routes.post("/producto")
async def create_product(
    title: str = Form(...),
    price: str = Form(...),
    description: str = Form(...),
    discount: str | None = Form(None),
    free_shipping: bool = Form(False),
    specs: str = Form(...),
    primary_image: UploadFile = File(...),
    optional_1: UploadFile | None = File(None),
    optional_2: UploadFile | None = File(None),
    optional_3: UploadFile | None = File(None),
    optional_4: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(basic_permission_dependency([])),
):
    product = Product(
        user_id=user.id,
        title=title,
        price=price,
        description=description,
        discount=discount,
        free_shipping=free_shipping,
        specs=json.loads(specs)
    )

    db.add(product)
    await db.flush()

    def add_image(file: UploadFile, primary=False):
        filename = media_utils.process_image(file, MEDIA_PRODUCTS)
        db.add(ProductImage(
            product_id=product.id,
            path=f"/media/products/{filename}",
            is_primary=primary
        ))

    add_image(primary_image, primary=True)

    for img in [optional_1, optional_2, optional_3, optional_4]:
        if img:
            add_image(img)

    await db.commit()
    return {"status": "ok", "product_uuid": product.uuid}


@store_routes.put("/producto/{product_uuid}")
async def update_product(
    product_uuid: UUID,
    title: str = Form(None),
    price: str = Form(None),
    description: str = Form(None),
    discount: str | None = Form(None),
    free_shipping: bool | None = Form(None),
    specs: str | None = Form(None),

    primary_image: UploadFile | None = File(None),
    optional_1: UploadFile | None = File(None),
    optional_2: UploadFile | None = File(None),
    optional_3: UploadFile | None = File(None),
    optional_4: UploadFile | None = File(None),

    db: AsyncSession = Depends(get_session),
    user: User = Depends(basic_permission_dependency([])),
):
    stmt = (
        select(Product)
        .where(Product.uuid == product_uuid)
        .options(
            joinedload(Product.images),
            joinedload(Product.reviews),
            joinedload(Product.user)
        )
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")

    if product.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    # update fields (only if provided)
    if title is not None: product.title = title
    if description is not None: product.description = description
    
    try:
        if price is not None: product.price = Decimal(price)
        if discount is not None: product.discount = Decimal(discount)
    except:
        raise HTTPException(403, "Forbidden")
        
    
    if free_shipping is not None: product.free_shipping = free_shipping
    if specs is not None: product.specs = json.loads(specs)

    # replace primary image if provided
    if primary_image:
        for img in product.images:
            if img.is_primary:
                await db.delete(img)
        filename = media_utils.process_image(primary_image, MEDIA_PRODUCTS)
        db.add(ProductImage(
            product_id=product.id,
            path=f"/media/products/{filename}",
            is_primary=True
        ))

    # replace optional images
    optionals = [optional_1, optional_2, optional_3, optional_4]
    for upload in optionals:
        if upload:
            filename = media_utils.process_image(upload, MEDIA_PRODUCTS)
            db.add(ProductImage(
                product_id=product.id,
                path=f"/media/products/{filename}",
                is_primary=False
            ))

    await db.commit()
    await db.refresh(product)
    return serialize_product(product)


@store_routes.delete("/producto/{product_uuid}")
async def delete_product(
    product_uuid: int,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(basic_permission_dependency([])),
):
    stmt = (
        select(Product)
        .where(Product.uuid == product_uuid)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Not found")

    if product.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    await db.delete(product)
    await db.commit()
    return {"status": "deleted"}


@store_routes.delete("/producto/{product_uuid}/image/{image_uuid}")
async def delete_image(
    product_uuid: UUID,
    image_uuid: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(basic_permission_dependency([])),
):
    
    stmt = (
        select(ProductImage)
        .where(ProductImage.uuid == image_uuid)
    )
    result = await db.execute(stmt)
    img = result.scalar_one_or_none()

    if not img:
        raise HTTPException(404, "Image not found")
    stmt = (
        select(Product)
        .where(Product.uuid == product_uuid)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if product:
        if img.product_id != product.id:
            raise HTTPException(404, "Image not found")
        if product.user_id != user.id:
            raise HTTPException(403, "Forbidden")
        if img.is_primary:
            raise HTTPException(400, "Cannot delete primary image")

    await db.delete(img)
    await db.commit()
    return {"status": "deleted"}
