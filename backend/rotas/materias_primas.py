from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import MateriaPrima
from ..esquemas import MateriaPrimaCriar, MateriaPrimaEditar, MateriaPrimaResposta
from typing import List

roteador = APIRouter(prefix="/materias-primas", tags=["materias-primas"])

def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()

@roteador.get("", response_model=List[MateriaPrimaResposta])
def listar_materias(sessao: Session = Depends(obter_sessao)):
    return sessao.query(MateriaPrima).order_by(MateriaPrima.nome).all()

@roteador.post("", response_model=MateriaPrimaResposta, status_code=201)
def criar_materia(dados: MateriaPrimaCriar, sessao: Session = Depends(obter_sessao)):
    existente = sessao.query(MateriaPrima).filter(MateriaPrima.codigo == dados.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Código já cadastrado")
    nova = MateriaPrima(codigo=dados.codigo, nome=dados.nome, quantidade_estoque=dados.quantidade_estoque, unidade_medida=dados.unidade_medida)
    sessao.add(nova)
    sessao.commit()
    sessao.refresh(nova)
    return nova

@roteador.get("/{materia_id}", response_model=MateriaPrimaResposta)
def obter_materia(materia_id: int, sessao: Session = Depends(obter_sessao)):
    materia = sessao.query(MateriaPrima).get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
    return materia

@roteador.put("/{materia_id}", response_model=MateriaPrimaResposta)
def editar_materia(materia_id: int, dados: MateriaPrimaEditar, sessao: Session = Depends(obter_sessao)):
    materia = sessao.query(MateriaPrima).get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
    if dados.nome is not None:
        materia.nome = dados.nome
    if dados.quantidade_estoque is not None:
        materia.quantidade_estoque = dados.quantidade_estoque
    if dados.unidade_medida is not None:
        materia.unidade_medida = dados.unidade_medida
    sessao.commit()
    sessao.refresh(materia)
    return materia

@roteador.delete("/{materia_id}", status_code=204)
def excluir_materia(materia_id: int, sessao: Session = Depends(obter_sessao)):
    materia = sessao.query(MateriaPrima).get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
    sessao.delete(materia)
    sessao.commit()
    return None
