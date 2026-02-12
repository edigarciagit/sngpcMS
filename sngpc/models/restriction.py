from pydantic import BaseModel, Field
from typing import Optional

class Restriction(BaseModel):
    no_produto: str = Field(..., description="Nome do produto (Chave de ligação)")
    ds_restricao_uso: Optional[str] = Field(None, description="Restrição de uso")
    st_restrito_hospital: Optional[str] = Field(None, description="Restrito hospitalar")
