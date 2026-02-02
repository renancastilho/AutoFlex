from pydantic import BaseModel
from typing import List, Optional

class ProdutoCriar(BaseModel):
    codigo: str
    nome: str
    valor: float

class ProdutoEditar(BaseModel):
    nome: Optional[str] = None
    valor: Optional[float] = None

class ProdutoResposta(BaseModel):
    id: int
    codigo: str
    nome: str
    valor: float
    class Config:
        from_attributes = True

class MateriaPrimaCriar(BaseModel):
    codigo: str
    nome: str
    quantidade_estoque: float
    unidade_medida: str

class MateriaPrimaEditar(BaseModel):
    nome: Optional[str] = None
    quantidade_estoque: Optional[float] = None
    unidade_medida: Optional[str] = None

class MateriaPrimaResposta(BaseModel):
    id: int
    codigo: str
    nome: str
    quantidade_estoque: float
    unidade_medida: str
    class Config:
        from_attributes = True

class AssociacaoCriar(BaseModel):
    materia_prima_id: int
    quantidade_necessaria: float
    unidade_medida: str

class AssociacaoResposta(BaseModel):
    id: int
    produto_id: int
    materia_prima_id: int
    quantidade_necessaria: float
    unidade_medida: str
    class Config:
        from_attributes = True

class ProducaoItem(BaseModel):
    produto_id: int
    codigo: str
    nome: str
    quantidade: int
    valor_unitario: float
    valor_total_item: float

class ProducaoResposta(BaseModel):
    itens: List[ProducaoItem]
    valor_total: float
