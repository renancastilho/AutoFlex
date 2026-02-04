from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto, ProdutoMateriaPrima, MateriaPrima
from ..esquemas import ProducaoResposta, ProducaoItem

def converter_quantidade(valor: float, de: str, para: str) -> float:
    if de == para:
        return valor
    mass = {"kg", "g", "mg"}
    vol = {"l", "ml"}
    if (de in mass and para in vol) or (de in vol and para in mass):
        raise ValueError("Unidades incompatíveis")
    # massa: normalizar em gramas
    if de in mass and para in mass:
        fatores_g = {"kg": 1000.0, "g": 1.0, "mg": 0.001}
        em_g = valor * fatores_g[de]
        return em_g / fatores_g[para]
    # volume: normalizar em mililitros
    if de in vol and para in vol:
        fatores_ml = {"l": 1000.0, "ml": 1.0}
        em_ml = valor * fatores_ml[de]
        return em_ml / fatores_ml[para]
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
    try:
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
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao calcular produção sugerida")
