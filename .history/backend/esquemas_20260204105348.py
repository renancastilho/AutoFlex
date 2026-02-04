from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
ALLOWED_UNITS = {"un", "kg", "g", "mg", "l", "ml"}

class ProdutoCriar(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    valor: float = Field(..., ge=0.0)
    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str):
        if not v.strip():
            raise ValueError("Código não pode ser vazio")
        return v
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v: float):
        return round(float(v), 2)

class ProdutoEditar(BaseModel):
    nome: Optional[str] = None
    valor: Optional[float] = Field(default=None, ge=0.0)
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v: Optional[float]):
        return None if v is None else round(float(v), 2)

class ProdutoResposta(BaseModel):
    id: int
    codigo: str
    nome: str
    valor: float
    class Config:
        from_attributes = True

class MateriaPrimaCriar(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    quantidade_estoque: float = Field(..., ge=0.0)
    unidade_medida: str
    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str):
        if not v.strip():
            raise ValueError("Código não pode ser vazio")
        return v
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("quantidade_estoque")
    @classmethod
    def validar_quantidade(cls, v: float):
        return round(float(v), 2)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: str):
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

class MateriaPrimaEditar(BaseModel):
    nome: Optional[str] = None
    quantidade_estoque: Optional[float] = Field(default=None, ge=0.0)
    unidade_medida: Optional[str] = None
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("quantidade_estoque")
    @classmethod
    def validar_quantidade(cls, v: Optional[float]):
        return None if v is None else round(float(v), 2)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: Optional[str]):
        if v is None:
            return v
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

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
    quantidade_necessaria: float = Field(..., gt=0.0)
    unidade_medida: str
    @field_validator("quantidade_necessaria")
    @classmethod
    def validar_quantidade(cls, v: float):
        return round(float(v), 2)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: str):
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

class AssociacaoEditar(BaseModel):
    quantidade_necessaria: Optional[float] = Field(default=None, gt=0.0)
    unidade_medida: Optional[str] = None
    @field_validator("quantidade_necessaria")
    @classmethod
    def validar_quantidade(cls, v: Optional[float]):
        return None if v is None else round(float(v), 2)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: Optional[str]):
        if v is None:
            return v
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

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
