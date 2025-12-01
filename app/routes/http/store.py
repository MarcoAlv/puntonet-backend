from fastapi import APIRouter, File, UploadFile, Form, Depends
from app.dependencies.auth import basic_permission_dependency
from app.models.store import Product, ProductImage
from app.core.db.sessionmanager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import media as media_utils
from app.config.base import MEDIA_PRODUCTS
from app.models.users import User
from pathlib import Path
import json
import uuid

store_routes = APIRouter(prefix="/store", tags=["Store"])


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
    return {"status": "ok", "product_id": product.id}
