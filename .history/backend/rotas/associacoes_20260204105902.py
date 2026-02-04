from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto, MateriaPrima, ProdutoMateriaPrima
from ..esquemas import AssociacaoCriar, AssociacaoEditar, AssociacaoResposta, ALLOWED_UNITS
from typing import List

roteador = APIRouter(prefix="/associacoes", tags=["associacoes"])

def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()

@roteador.get("/produto/{produto_id}", response_model=List[AssociacaoResposta])
def listar_associacoes(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return sessao.query(ProdutoMateriaPrima).filter(ProdutoMateriaPrima.produto_id == produto_id).all()

@roteador.post("/produto/{produto_id}", response_model=AssociacaoResposta, status_code=201)
def criar_associacao(produto_id: int, dados: AssociacaoCriar, sessao: Session = Depends(obter_sessao)):
    try:
        produto = sessao.query(Produto).get(produto_id)
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        materia = sessao.query(MateriaPrima).get(dados.materia_prima_id)
        if not materia:
            raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
        if materia.unidade_medida not in ALLOWED_UNITS:
            raise HTTPException(status_code=400, detail="Unidade da matéria-prima inválida")
        if dados.unidade_medida not in ALLOWED_UNITS:
            raise HTTPException(status_code=400, detail="Unidade inválida")
        mass = {"kg", "g", "mg"}
        vol = {"l", "ml"}
        if materia.unidade_medida == "un" and dados.unidade_medida != "un":
            raise HTTPException(status_code=400, detail="Unidade incompatível com a matéria-prima")
        if (materia.unidade_medida in mass and dados.unidade_medida in vol) or (materia.unidade_medida in vol and dados.unidade_medida in mass):
            raise HTTPException(status_code=400, detail="Unidades de massa e volume são incompatíveis")
        existente = sessao.query(ProdutoMateriaPrima).filter(
            ProdutoMateriaPrima.produto_id == produto_id,
            ProdutoMateriaPrima.materia_prima_id == dados.materia_prima_id
        ).first()
        if existente:
            raise HTTPException(status_code=400, detail="Associação já existe")
        nova = ProdutoMateriaPrima(
            produto_id=produto_id,
            materia_prima_id=dados.materia_prima_id,
            quantidade_necessaria=dados.quantidade_necessaria,
            unidade_medida=dados.unidade_medida
        )
        sessao.add(nova)
        sessao.commit()
        sessao.refresh(nova)
        return nova
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar associação")

@roteador.put("/{associacao_id}", response_model=AssociacaoResposta)
def editar_associacao(associacao_id: int, dados: AssociacaoEditar, sessao: Session = Depends(obter_sessao)):
    try:
        assoc = sessao.query(ProdutoMateriaPrima).get(associacao_id)
        if not assoc:
            raise HTTPException(status_code=404, detail="Associação não encontrada")
        if dados.quantidade_necessaria is not None:
            assoc.quantidade_necessaria = dados.quantidade_necessaria
        if dados.unidade_medida is not None:
            materia = sessao.query(MateriaPrima).get(assoc.materia_prima_id)
            mass = {"kg", "g", "mg"}
            vol = {"l", "ml"}
            if materia.unidade_medida == "un" and dados.unidade_medida != "un":
                raise HTTPException(status_code=400, detail="Unidade incompatível com a matéria-prima")
            if (materia.unidade_medida in mass and dados.unidade_medida in vol) or (materia.unidade_medida in vol and dados.unidade_medida in mass):
                raise HTTPException(status_code=400, detail="Unidades de massa e volume são incompatíveis")
            assoc.unidade_medida = dados.unidade_medida
        sessao.commit()
        sessao.refresh(assoc)
        return assoc
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar associação")

@roteador.delete("/{associacao_id}", status_code=204)
def excluir_associacao(associacao_id: int, sessao: Session = Depends(obter_sessao)):
    try:
        assoc = sessao.query(ProdutoMateriaPrima).get(associacao_id)
        if not assoc:
            raise HTTPException(status_code=404, detail="Associação não encontrada")
        sessao.delete(assoc)
        sessao.commit()
        return None
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir associação")
