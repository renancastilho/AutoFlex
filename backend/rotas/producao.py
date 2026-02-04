from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..banco import SessaoLocal
from ..esquemas import ProducaoResposta
from ..services.producao import calcular_producao
from typing import Optional

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
def calcular_producao_sugerida(produto_id: Optional[int] = None, sessao: Session = Depends(obter_sessao)):
    return calcular_producao(sessao, produto_id)
