from app.models.store import Product
from app.utils.media import full_url
from typing import Optional

def serialize_product(product: Product, review_count: int = 0, review_avg: Optional[float] = None) -> dict:
    primary = None
    secondary = []

    for img in product.images:
        url = full_url(img.path)
        if img.is_primary:
            primary = url
        else:
            secondary.append(url)

    return {
        "uuid": str(product.uuid),
        "title": product.title,
        "price": str(product.price),
        "description": product.description,
        "discount": str(product.discount) if product.discount is not None else None,
        "free_shipping": product.free_shipping,
        "specs": product.specs,
        "primary_image": primary,
        "secondary_images": secondary,
        "review_count": review_count,
        "review_avg": review_avg,
        "store_name": product.user.store_name if product.user else None,
    }
