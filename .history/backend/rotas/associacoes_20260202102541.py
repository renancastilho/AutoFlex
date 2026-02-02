from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto, MateriaPrima, ProdutoMateriaPrima
from ..esquemas import AssociacaoCriar, AssociacaoResposta
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
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    materia = sessao.query(MateriaPrima).get(dados.materia_prima_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
    existente = sessao.query(ProdutoMateriaPrima).filter(
        ProdutoMateriaPrima.produto_id == produto_id,
        ProdutoMateriaPrima.materia_prima_id == dados.materia_prima_id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Associação já existe")
    nova = ProdutoMateriaPrima(produto_id=produto_id, materia_prima_id=dados.materia_prima_id, quantidade_necessaria=dados.quantidade_necessaria)
    sessao.add(nova)
    sessao.commit()
    sessao.refresh(nova)
    return nova

@roteador.put("/{associacao_id}", response_model=AssociacaoResposta)
def editar_associacao(associacao_id: int, dados: AssociacaoCriar, sessao: Session = Depends(obter_sessao)):
    assoc = sessao.query(ProdutoMateriaPrima).get(associacao_id)
    if not assoc:
        raise HTTPException(status_code=404, detail="Associação não encontrada")
    assoc.quantidade_necessaria = dados.quantidade_necessaria
    sessao.commit()
    sessao.refresh(assoc)
    return assoc

@roteador.delete("/{associacao_id}", status_code=204)
def excluir_associacao(associacao_id: int, sessao: Session = Depends(obter_sessao)):
    assoc = sessao.query(ProdutoMateriaPrima).get(associacao_id)
    if not assoc:
        raise HTTPException(status_code=404, detail="Associação não encontrada")
    sessao.delete(assoc)
    sessao.commit()
    return None
