"""
Este arquivo demonstra como estruturar modelos de dados (schemas) usando Pydantic em uma API FastAPI.
Os schemas definem a forma e validação dos dados para operações de autenticação e gerenciamento de usuários:
- Registro de novos usuários
- Login com credenciais e hardware_id
- Finalização de cadastro com token
- Representação de tokens de sessão com expiração
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime

# -------------------
# Usuário
# -------------------
class UsuarioBase(BaseModel):
    nickname: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str
    confirmar_senha: str
    consentimento_dados: bool

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str
    hardware_id: str | None = None

class UsuarioFinalizacao(BaseModel):
    email: EmailStr
    token: str

class Usuario(UsuarioBase):
    id_usuario: int

    class Config:
        from_attributes = True


# -------------------
# Token de Sessão
# -------------------
class TokenSessaoBase(BaseModel):
    token: str
    expira_em: datetime

class TokenSessao(TokenSessaoBase):
    id_token: int
    id_usuario: int

    class Config:
        from_attributes = True
