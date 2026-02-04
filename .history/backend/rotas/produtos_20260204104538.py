from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..modelos import Produto
from ..esquemas import ProdutoCriar, ProdutoEditar, ProdutoResposta
from typing import List

roteador = APIRouter(prefix="/produtos", tags=["produtos"])

def obter_sessao():
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()

@roteador.get("", response_model=List[ProdutoResposta])
def listar_produtos(sessao: Session = Depends(obter_sessao)):
    return sessao.query(Produto).order_by(Produto.nome).all()

@roteador.post("", response_model=ProdutoResposta, status_code=201)
def criar_produto(dados: ProdutoCriar, sessao: Session = Depends(obter_sessao)):
    existente = sessao.query(Produto).filter(Produto.codigo == dados.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Código já cadastrado")
    novo = Produto(codigo=dados.codigo, nome=dados.nome, valor=dados.valor)
    sessao.add(novo)
    sessao.commit()
    sessao.refresh(novo)
    return novo

@roteador.get("/{produto_id}", response_model=ProdutoResposta)
def obter_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@roteador.put("/{produto_id}", response_model=ProdutoResposta)
def editar_produto(produto_id: int, dados: ProdutoEditar, sessao: Session = Depends(obter_sessao)):
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if dados.nome is not None:
        produto.nome = dados.nome
    if dados.valor is not None:
        produto.valor = dados.valor
    sessao.commit()
    sessao.refresh(produto)
    return produto

@roteador.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    sessao.delete(produto)
    sessao.commit()
    return None
