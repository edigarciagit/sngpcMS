from pydantic import BaseModel, Field, validator
from typing import Optional

class Medication(BaseModel):
    numero_registro_produto: str = Field(..., min_length=9, description="Número de registro do produto")
    nome_produto: str = Field(..., description="Nome do produto")
    situacao_registro: Optional[str] = Field(None, description="Situação do registro (Válido, Caduco, etc.)")

    @validator('numero_registro_produto')
    def validate_registro(cls, v):
        # Remove non-digits
        v = ''.join(filter(str.isdigit, v))
        return v
