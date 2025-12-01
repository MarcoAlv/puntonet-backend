from app.models.store import Product
from app.utils.media import full_url
from statistics import mean

def serialize_product(product: Product) -> dict:
    primary = None
    secondary = []

    for img in product.images:
        url = full_url(img.path)
        if img.is_primary:
            primary = url
        else:
            secondary.append(url)

    ratings = [r.rating for r in product.reviews]
    review_count = len(ratings)
    review_avg = mean(ratings) if review_count > 0 else None

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
        "store_name": product.user.store_name,
    }
