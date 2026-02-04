from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..utils.texto import normalizar_nome
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
    try:
        nomes = [n for (n,) in sessao.query(MateriaPrima.nome).all()]
        if any(normalizar_nome(n) == normalizar_nome(dados.nome) for n in nomes):
            raise HTTPException(status_code=400, detail="Nome já cadastrado")
        proximo = (sessao.query(func.max(MateriaPrima.codigo)).scalar() or 0) + 1
        nova = MateriaPrima(codigo=proximo, nome=dados.nome, nome_normalizado=normalizar_nome(dados.nome), quantidade_estoque=dados.quantidade_estoque, unidade_medida=dados.unidade_medida)
        sessao.add(nova)
        sessao.commit()
        sessao.refresh(nova)
        return nova
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar matéria-prima")

@roteador.get("/{materia_id}", response_model=MateriaPrimaResposta)
def obter_materia(materia_id: int, sessao: Session = Depends(obter_sessao)):
    materia = sessao.get(MateriaPrima, materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
    return materia

@roteador.put("/{materia_id}", response_model=MateriaPrimaResposta)
def editar_materia(materia_id: int, dados: MateriaPrimaEditar, sessao: Session = Depends(obter_sessao)):
    try:
        materia = sessao.get(MateriaPrima, materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
        if dados.nome is not None:
            nomes = [n for (n,) in sessao.query(MateriaPrima.nome).all() if n != materia.nome]
            if any(normalizar_nome(n) == normalizar_nome(dados.nome) for n in nomes):
                raise HTTPException(status_code=400, detail="Nome já cadastrado")
            materia.nome = dados.nome
            materia.nome_normalizado = normalizar_nome(dados.nome)
        if dados.quantidade_estoque is not None:
            materia.quantidade_estoque = dados.quantidade_estoque
        if dados.unidade_medida is not None:
            materia.unidade_medida = dados.unidade_medida
        sessao.commit()
        sessao.refresh(materia)
        return materia
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar matéria-prima")

@roteador.delete("/{materia_id}", status_code=204)
def excluir_materia(materia_id: int, sessao: Session = Depends(obter_sessao)):
    try:
        materia = sessao.query(MateriaPrima).get(materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail="Matéria-prima não encontrada")
        sessao.delete(materia)
        sessao.commit()
        return None
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir matéria-prima")
