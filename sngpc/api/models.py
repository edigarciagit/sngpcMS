from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    numero_registro = Column(String, index=True)
    nome_produto = Column(String, index=True)
    is_controlled = Column(Boolean, default=False)
    restriction_detail = Column(String, nullable=True)
