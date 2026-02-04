from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
ALLOWED_UNITS = {"un", "kg", "g", "mg", "l", "ml"}
from decimal import Decimal, ROUND_HALF_UP

class ProdutoCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    valor: Decimal = Field(..., ge=Decimal("0.00"))
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v):
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class ProdutoEditar(BaseModel):
    nome: Optional[str] = None
    valor: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v: Optional[Decimal]):
        if v is None:
            return v
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class ProdutoResposta(BaseModel):
    id: int
    codigo: int
    nome: str
    valor: Decimal
    class Config:
        from_attributes = True

class MateriaPrimaCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    quantidade_estoque: Decimal = Field(..., ge=Decimal("0.00"))
    unidade_medida: str
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("quantidade_estoque")
    @classmethod
    def validar_quantidade(cls, v):
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: str):
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

class MateriaPrimaEditar(BaseModel):
    nome: Optional[str] = None
    quantidade_estoque: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))
    unidade_medida: Optional[str] = None
    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v
    @field_validator("quantidade_estoque")
    @classmethod
    def validar_quantidade(cls, v: Optional[Decimal]):
        if v is None:
            return v
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
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
    codigo: int
    nome: str
    quantidade_estoque: Decimal
    unidade_medida: str
    class Config:
        from_attributes = True

class AssociacaoCriar(BaseModel):
    materia_prima_id: int
    quantidade_necessaria: Decimal = Field(..., gt=Decimal("0.00"))
    unidade_medida: str
    @field_validator("quantidade_necessaria")
    @classmethod
    def validar_quantidade(cls, v):
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    @field_validator("unidade_medida")
    @classmethod
    def validar_unidade(cls, v: str):
        uv = v.lower()
        if uv not in ALLOWED_UNITS:
            raise ValueError("Unidade inválida")
        return uv

class AssociacaoEditar(BaseModel):
    quantidade_necessaria: Optional[Decimal] = Field(default=None, gt=Decimal("0.00"))
    unidade_medida: Optional[str] = None
    @field_validator("quantidade_necessaria")
    @classmethod
    def validar_quantidade(cls, v: Optional[Decimal]):
        if v is None:
            return v
        d = Decimal(str(v))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
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
    quantidade_necessaria: Decimal
    unidade_medida: str
    class Config:
        from_attributes = True

class ProducaoItem(BaseModel):
    produto_id: int
    codigo: int
    nome: str
    quantidade: int
    valor_unitario: Decimal
    valor_total_item: Decimal

class ProducaoResposta(BaseModel):
    itens: List[ProducaoItem]
    valor_total: Decimal
