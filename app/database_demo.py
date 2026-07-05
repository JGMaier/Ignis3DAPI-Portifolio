"""
Este arquivo demonstra como configurar a conexão com banco de dados PostgreSQL usando SQLAlchemy.
Inclui:
- Engine com pool configurado
- Base declarativa para modelos ORM
- SessionLocal para gerenciar sessões
- Dependência get_db para uso nas rotas FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("A variável de ambiente DATABASE_URL não foi encontrada. O PostgreSQL é obrigatório para esta aplicação.")

# Configuração do engine com parâmetros de pool
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,   # tempo máximo de espera por conexão
    pool_recycle=1800  # recicla conexões a cada 30 min
)

# Cria sessão e base declarativa
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência para obter a sessão do banco nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
