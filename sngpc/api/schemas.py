from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    numero_registro: str
    nome_produto: str
    is_controlled: bool
    restriction_detail: Optional[str] = None

class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
