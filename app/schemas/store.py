from pydantic import BaseModel
from decimal import Decimal

class CreateProduct(BaseModel):
    title: str
    price: Decimal
    description: str
    discount: Decimal | None = None
    free_shipping: bool = False
    specs: list[str]
