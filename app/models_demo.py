"""
Este arquivo demonstra como estruturar modelos ORM usando SQLAlchemy em uma API FastAPI.
Os modelos representam tabelas de autenticação e controle de acesso:
- Usuários
- Tokens de sessão
- Licenças
- Logs de checkout

Mostra boas práticas de mapeamento relacional, uso de chaves estrangeiras e relacionamentos.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# -------------------
# Usuário
# -------------------
class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "autenticacao"}  
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    consentimento_dados = Column(Boolean, default=False)
    tipo_conta = Column(String(20), default="demo")
    hardware_id = Column(String(255), nullable=True)

    tokens = relationship("TokenSessao", back_populates="usuario")
    licencas = relationship("Licenca", back_populates="usuario")


# -------------------
# Token de Sessão
# -------------------
class TokenSessao(Base):
    __tablename__ = "tokens_sessao"
    __table_args__ = {"schema": "autenticacao"}

    id_token = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("autenticacao.usuarios.id_usuario"), nullable=False)
    token = Column(String(36), unique=True, index=True, nullable=False)
    expira_em = Column(TIMESTAMP(timezone=True), nullable=False)
    usado = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="tokens")


# -------------------
# Licença
# -------------------
class Licenca(Base):
    __tablename__ = "licencas"
    __table_args__ = {"schema": "autenticacao"}

    id_licenca = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("autenticacao.usuarios.id_usuario"), nullable=False)
    data_vencimento = Column(TIMESTAMP(timezone=True), nullable=True)  # Null = licença vitalícia
    ativa = Column(Boolean, default=True)
    tipo = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)

    usuario = relationship("Usuario", back_populates="licencas")


# -------------------
# Log de Checkout
# -------------------
class LogCheckout(Base):
    __tablename__ = "logs_checkout"
    __table_args__ = {"schema": "autenticacao"}

    id_log = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("autenticacao.usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    plano = Column(String(50), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", backref="logs_checkout")
