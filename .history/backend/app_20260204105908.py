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
        cols_assoc = con.exec_driver_sql("PRAGMA table_info('produtos_materias_primas')").fetchall()
        nomes_assoc = [r[1] for r in cols_assoc]
        tipos_assoc = {r[1]: r[2].upper() for r in cols_assoc}
        if "unidade_medida" not in nomes_assoc:
            con.exec_driver_sql("ALTER TABLE produtos_materias_primas ADD COLUMN unidade_medida VARCHAR(10) DEFAULT 'un'")
            con.commit()
        if tipos_assoc.get("quantidade_necessaria", "") == "INTEGER":
            con.exec_driver_sql("""
                CREATE TABLE IF NOT EXISTS _tmp_produtos_materias_primas (
                    id INTEGER PRIMARY KEY,
                    produto_id INTEGER NOT NULL,
                    materia_prima_id INTEGER NOT NULL,
                    quantidade_necessaria NUMERIC(14,2) NOT NULL,
                    unidade_medida VARCHAR(10) NOT NULL DEFAULT 'un'
                )
            """)
            con.exec_driver_sql("""
                INSERT INTO _tmp_produtos_materias_primas (id, produto_id, materia_prima_id, quantidade_necessaria, unidade_medida)
                SELECT id, produto_id, materia_prima_id, CAST(quantidade_necessaria AS REAL), COALESCE(unidade_medida, 'un')
                FROM produtos_materias_primas
            """)
            con.exec_driver_sql("DROP TABLE produtos_materias_primas")
            con.exec_driver_sql("ALTER TABLE _tmp_produtos_materias_primas RENAME TO produtos_materias_primas")
            con.commit()
except Exception:
    pass
