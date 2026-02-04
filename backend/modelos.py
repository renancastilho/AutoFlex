from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .banco import Base
from decimal import Decimal

class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    ingredientes: Mapped[list["ProdutoMateriaPrima"]] = relationship("ProdutoMateriaPrima", back_populates="produto", cascade="all, delete-orphan")

class MateriaPrima(Base):
    __tablename__ = "materias_primas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    quantidade_estoque: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    unidade_medida: Mapped[str] = mapped_column(String(10), nullable=False, default="un")
    usos: Mapped[list["ProdutoMateriaPrima"]] = relationship("ProdutoMateriaPrima", back_populates="materia_prima", cascade="all, delete-orphan")

class ProdutoMateriaPrima(Base):
    __tablename__ = "produtos_materias_primas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True)
    materia_prima_id: Mapped[int] = mapped_column(ForeignKey("materias_primas.id", ondelete="CASCADE"), nullable=False, index=True)
    quantidade_necessaria: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unidade_medida: Mapped[str] = mapped_column(String(10), nullable=False, default="un")
    produto: Mapped[Produto] = relationship("Produto", back_populates="ingredientes")
    materia_prima: Mapped[MateriaPrima] = relationship("MateriaPrima", back_populates="usos")
    __table_args__ = (UniqueConstraint("produto_id", "materia_prima_id", name="uq_produto_materia"),)
