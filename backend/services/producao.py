from sqlalchemy.orm import Session
from ..modelos import Produto, ProdutoMateriaPrima, MateriaPrima
from ..esquemas import ProducaoResposta, ProducaoItem
from decimal import Decimal

MASS = {"kg", "g", "mg"}
VOL = {"l", "ml"}

def converter_quantidade(valor: float, de: str, para: str) -> float:
    if de == para:
        return valor
    if (de in MASS and para in VOL) or (de in VOL and para in MASS):
        raise ValueError("Unidades incompatíveis")
    if de in MASS and para in MASS:
        fatores_g = {"kg": 1000.0, "g": 1.0, "mg": 0.001}
        em_g = valor * fatores_g[de]
        return em_g / fatores_g[para]
    if de in VOL and para in VOL:
        fatores_ml = {"l": 1000.0, "ml": 1.0}
        em_ml = valor * fatores_ml[de]
        return em_ml / fatores_ml[para]
    raise ValueError("Unidades incompatíveis")

def calcular_producao(sessao: Session, produto_id: int | None = None) -> ProducaoResposta:
    materias = {m.id: m for m in sessao.query(MateriaPrima).all()}
    estoque = {m.id: float(m.quantidade_estoque) for m in materias.values()}
    produtos = sessao.query(Produto).all() if produto_id is None else sessao.query(Produto).filter(Produto.id == produto_id).all()
    produtos.sort(key=lambda p: float(p.valor), reverse=True)
    itens: list[ProducaoItem] = []
    for p in produtos:
        ingredientes = sessao.query(ProdutoMateriaPrima).filter(ProdutoMateriaPrima.produto_id == p.id).all()
        if not ingredientes:
            continue
        maximo = None
        for ing in ingredientes:
            materia = materias.get(ing.materia_prima_id)
            if not materia:
                continue
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
            materia = materias.get(ing.materia_prima_id)
            if not materia:
                continue
            delta_assoc = quantidade * float(ing.quantidade_necessaria)
            try:
                delta_materia = converter_quantidade(delta_assoc, ing.unidade_medida, materia.unidade_medida)
            except Exception:
                delta_materia = 0.0
            estoque[ing.materia_prima_id] = estoque.get(ing.materia_prima_id, 0.0) - delta_materia
        itens.append(ProducaoItem(produto_id=p.id, codigo=p.codigo, nome=p.nome, quantidade=quantidade, valor_unitario=float(p.valor), valor_total_item=quantidade * float(p.valor)))
    valor_total = sum(Decimal(str(i.valor_total_item)) for i in itens)
    return ProducaoResposta(itens=itens, valor_total=valor_total)
