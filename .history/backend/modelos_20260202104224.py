from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .banco import Base

class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    ingredientes: Mapped[list["ProdutoMateriaPrima"]] = relationship("ProdutoMateriaPrima", back_populates="produto", cascade="all, delete-orphan")

class MateriaPrima(Base):
    __tablename__ = "materias_primas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    quantidade_estoque: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    unidade_medida: Mapped[str] = mapped_column(String(10), nullable=False, default="un")
    usos: Mapped[list["ProdutoMateriaPrima"]] = relationship("ProdutoMateriaPrima", back_populates="materia_prima", cascade="all, delete-orphan")

class ProdutoMateriaPrima(Base):
    __tablename__ = "produtos_materias_primas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True)
    materia_prima_id: Mapped[int] = mapped_column(ForeignKey("materias_primas.id", ondelete="CASCADE"), nullable=False, index=True)
    quantidade_necessaria: Mapped[int] = mapped_column(Integer, nullable=False)
    produto: Mapped[Produto] = relationship("Produto", back_populates="ingredientes")
    materia_prima: Mapped[MateriaPrima] = relationship("MateriaPrima", back_populates="usos")
    __table_args__ = (UniqueConstraint("produto_id", "materia_prima_id", name="uq_produto_materia"),)
