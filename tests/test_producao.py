import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.banco import Base
from backend.modelos import Produto, MateriaPrima, ProdutoMateriaPrima
from backend.services.producao import calcular_producao

def setup_db():
    os.environ["BANCO_URL"] = "sqlite:///:memory:"
    engine = create_engine(os.environ["BANCO_URL"])
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()

def seed_basico(sess):
    p = Produto(codigo=1, nome="Bolo Teste", valor=10.00)
    a = MateriaPrima(codigo=1, nome="Farinha", quantidade_estoque=1000.00, unidade_medida="g")
    b = MateriaPrima(codigo=2, nome="Ovos", quantidade_estoque=30.00, unidade_medida="un")
    sess.add_all([p, a, b])
    sess.commit()
    sess.refresh(p)
    sess.refresh(a)
    sess.refresh(b)
    ing1 = ProdutoMateriaPrima(produto_id=p.id, materia_prima_id=a.id, quantidade_necessaria=200.00, unidade_medida="g")
    ing2 = ProdutoMateriaPrima(produto_id=p.id, materia_prima_id=b.id, quantidade_necessaria=2.00, unidade_medida="un")
    sess.add_all([ing1, ing2])
    sess.commit()

def test_calculo_producao_por_produto():
    sess = setup_db()
    seed_basico(sess)
    resp = calcular_producao(sess, produto_id=1)
    assert resp.valor_total == 10.00 * 5
    assert resp.itens[0].quantidade == 5
    assert resp.itens[0].nome == "Bolo Teste"
