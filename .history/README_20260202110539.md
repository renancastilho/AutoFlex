# Controle de Produção (Web/API)

Aplicação web simples para controlar produtos, matérias-primas, associações e calcular produção sugerida priorizando maior valor.

## Tecnologias

- Back-end: FastAPI + SQLAlchemy
- Front-end: HTML/CSS/JS puro
- Banco: SQLite por padrão (configurável via BANCO_URL)

## Executar

1. `python -m pip install -r requirements.txt`
2. `python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000`
3. Abrir `http://127.0.0.1:8000/web/`

## Endpoints principais

- `/produtos` CRUD
- `/materias-primas` CRUD
- `/associacoes` CRUD
- `/producao/sugerida` cálculo da produção

## Configuração do Banco

Defina `BANCO_URL` para Postgres/MySQL/Oracle conforme necessidade.

## Observações

Nomes de pastas, métodos e variáveis em Português.
