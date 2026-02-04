from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto, ProdutoMateriaPrima, MateriaPrima
from ..esquemas import ProducaoResposta, ProducaoItem

def converter_quantidade(valor: float, de: str, para: str) -> float:
    if de == para:
        return valor
    if de == "kg" and para == "g":
        return valor * 1000.0
    if de == "g" and para == "kg":
        return valor / 1000.0
    raise ValueError("Unidades incompatíveis")

roteador = APIRouter(prefix="/producao", tags=["producao"])

def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()

@roteador.get("/sugerida", response_model=ProducaoResposta)
def calcular_producao_sugerida(sessao: Session = Depends(obter_sessao)):
    materias = {m.id: m for m in sessao.query(MateriaPrima).all()}
    estoque = {m.id: float(m.quantidade_estoque) for m in materias.values()}
    produtos = sessao.query(Produto).all()
    produtos.sort(key=lambda p: p.valor, reverse=True)
    itens = []
    for p in produtos:
        ingredientes = sessao.query(ProdutoMateriaPrima).filter(ProdutoMateriaPrima.produto_id == p.id).all()
        if not ingredientes:
            continue
        maximo = None
        for ing in ingredientes:
            materia = materias[ing.materia_prima_id]
            try:
                disponivel_assoc = converter_quantidade(estoque.get(ing.materia_prima_id, 0.0), materia.unidade_medida, ing.unidade_medida)
            except Exception:
                disponivel_assoc = 0.0
            possivel = int(disponivel_assoc // float(ing.quantidade_necessaria))
            if maximo is None or possivel < maximo:
                maximo = possivel
        quantidade = maximo or 0
        if quantidade <= 0:
            continue
        for ing in ingredientes:
            materia = materias[ing.materia_prima_id]
            delta_assoc = quantidade * float(ing.quantidade_necessaria)
            try:
                delta_materia = converter_quantidade(delta_assoc, ing.unidade_medida, materia.unidade_medida)
            except Exception:
                delta_materia = 0.0
            estoque[ing.materia_prima_id] = estoque.get(ing.materia_prima_id, 0.0) - delta_materia
        itens.append(ProducaoItem(produto_id=p.id, codigo=p.codigo, nome=p.nome, quantidade=quantidade, valor_unitario=p.valor, valor_total_item=quantidade * p.valor))
    valor_total = sum(i.valor_total_item for i in itens)
    return ProducaoResposta(itens=itens, valor_total=valor_total)
