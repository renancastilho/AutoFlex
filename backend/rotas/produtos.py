from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..utils.texto import normalizar_nome
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
    try:
        nomes = [n for (n,) in sessao.query(Produto.nome).all()]
        if any(normalizar_nome(n) == normalizar_nome(dados.nome) for n in nomes):
            raise HTTPException(status_code=400, detail="Nome já cadastrado")
        proximo = (sessao.query(func.max(Produto.codigo)).scalar() or 0) + 1
        novo = Produto(codigo=proximo, nome=dados.nome, nome_normalizado=normalizar_nome(dados.nome), valor=dados.valor)
        sessao.add(novo)
        sessao.commit()
        sessao.refresh(novo)
        return novo
    except HTTPException:
        raise
    except Exception as e:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar produto")

@roteador.get("/{produto_id}", response_model=ProdutoResposta)
def obter_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    produto = sessao.query(Produto).get(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@roteador.put("/{produto_id}", response_model=ProdutoResposta)
def editar_produto(produto_id: int, dados: ProdutoEditar, sessao: Session = Depends(obter_sessao)):
    try:
        produto = sessao.get(Produto, produto_id)
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        if dados.nome is not None:
            nomes = [n for (n,) in sessao.query(Produto.nome).all() if n != produto.nome]
            if any(normalizar_nome(n) == normalizar_nome(dados.nome) for n in nomes):
                raise HTTPException(status_code=400, detail="Nome já cadastrado")
            produto.nome = dados.nome
            produto.nome_normalizado = normalizar_nome(dados.nome)
        if dados.valor is not None:
            produto.valor = dados.valor
        sessao.commit()
        sessao.refresh(produto)
        return produto
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar produto")

@roteador.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, sessao: Session = Depends(obter_sessao)):
    try:
        produto = sessao.query(Produto).get(produto_id)
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        sessao.delete(produto)
        sessao.commit()
        return None
    except HTTPException:
        raise
    except Exception:
        sessao.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir produto")
