import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

def obter_url_banco():
    url = os.getenv("BANCO_URL")
    if url:
        return url
    return "sqlite:///c:/Users/Renan de Castilho/Desktop/AutoFlex/dados.db"

motor = create_engine(obter_url_banco(), echo=False, future=True)
SessaoLocal = sessionmaker(bind=motor, autoflush=False, autocommit=False, future=True)
