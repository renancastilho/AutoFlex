from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto, ProdutoMateriaPrima, MateriaPrima
from ..esquemas import ProducaoResposta, ProducaoItem

roteador = APIRouter(prefix="/producao", tags=["producao"])

def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()

@roteador.get("/sugerida", response_model=ProducaoResposta)
def calcular_producao_sugerida(sessao: Session = Depends(obter_sessao)):
    estoque = {m.id: m.quantidade_estoque for m in sessao.query(MateriaPrima).all()}
    produtos = sessao.query(Produto).all()
    produtos.sort(key=lambda p: p.valor, reverse=True)
    itens = []
    for p in produtos:
        ingredientes = sessao.query(ProdutoMateriaPrima).filter(ProdutoMateriaPrima.produto_id == p.id).all()
        if not ingredientes:
            continue
        maximo = None
        for ing in ingredientes:
            disponivel = estoque.get(ing.materia_prima_id, 0)
            possivel = disponivel // ing.quantidade_necessaria
            if maximo is None or possivel < maximo:
                maximo = possivel
        quantidade = maximo or 0
        if quantidade <= 0:
            continue
        for ing in ingredientes:
            estoque[ing.materia_prima_id] = estoque.get(ing.materia_prima_id, 0) - quantidade * ing.quantidade_necessaria
        itens.append(ProducaoItem(produto_id=p.id, codigo=p.codigo, nome=p.nome, quantidade=quantidade, valor_unitario=p.valor, valor_total_item=quantidade * p.valor))
    valor_total = sum(i.valor_total_item for i in itens)
    return ProducaoResposta(itens=itens, valor_total=valor_total)
