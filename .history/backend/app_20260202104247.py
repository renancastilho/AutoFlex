from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from .banco import Base, motor
from .rotas.produtos import roteador as produtos_roteador
from .rotas.materias_primas import roteador as materias_roteador
from .rotas.associacoes import roteador as associacoes_roteador
from .rotas.producao import roteador as producao_roteador
import os

app = FastAPI(title="Controle de Produção", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=motor)

app.include_router(produtos_roteador)
app.include_router(materias_roteador)
app.include_router(associacoes_roteador)
app.include_router(producao_roteador)

raiz = os.path.dirname(os.path.dirname(__file__))
static_dir = os.path.join(raiz, "frontend")
if os.path.isdir(static_dir):
    app.mount("/web", StaticFiles(directory=static_dir, html=True), name="frontend")

try:
    with motor.connect() as con:
        cols = [r[1] for r in con.exec_driver_sql("PRAGMA table_info('materias_primas')").fetchall()]
        if "unidade_medida" not in cols:
            con.exec_driver_sql("ALTER TABLE materias_primas ADD COLUMN unidade_medida VARCHAR(10)")
            con.commit()
except Exception:
    pass
