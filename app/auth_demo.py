"""
Versão demonstrativa do módulo principal da API do Ignis3D.
Responsável pela autenticação de usuários, cadastro, login social (Google/Facebook),
gerenciamento de sessões, validação de tokens e inicialização da aplicação.
Credenciais, regras internas e implementações proprietárias foram removidas.
"""

import uuid
import random
import string
import bcrypt
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import database, models, schemas, billing

router = APIRouter()
app = FastAPI(title="Ignis3D API")

pendentes = {}


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def gerar_token():
    return "".join(random.choices(string.digits, k=8))


@router.get("/auth/google/callback")
def google_callback(code: str, db: Session = Depends(database.get_db)):

    usuario = {
        "email": "usuario@email.com",
        "nickname": "Demo User"
    }

    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.email == usuario["email"]
    ).first()

    if not db_usuario:
        db_usuario = models.Usuario(
            nickname=usuario["nickname"],
            email=usuario["email"],
            tipo_conta="demo"
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)

    token = str(uuid.uuid4())

    return {
        "token": token,
        "usuario": db_usuario.nickname
    }


@router.get("/auth/facebook/callback")
def facebook_callback(code: str):

    return {
        "status": "success",
        "provider": "facebook"
    }


@app.post("/cadastrar")
def cadastrar(usuario: schemas.UsuarioCreate):

    token = gerar_token()

    pendentes[usuario.email] = {
        "nickname": usuario.nickname,
        "senha_hash": get_password_hash(usuario.senha),
        "token": token,
        "expira": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    return {
        "status": "pending",
        "message": "Cadastro iniciado."
    }


@app.post("/finalizar")
def finalizar(payload: schemas.UsuarioFinalizacao):

    dados = pendentes.get(payload.email)

    if not dados:
        raise HTTPException(400, "Cadastro inexistente.")

    if dados["token"] != payload.token:
        raise HTTPException(401, "Token inválido.")

    return {
        "status": "success"
    }


@app.post("/auth/login")
def login(usuario: schemas.UsuarioLogin,
          db: Session = Depends(database.get_db)):

    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email
    ).first()

    if not db_usuario:
        raise HTTPException(401, "Credenciais inválidas.")

    if not verify_password(usuario.senha, db_usuario.senha_hash):
        raise HTTPException(401, "Credenciais inválidas.")

    token = str(uuid.uuid4())

    return {
        "token": token,
        "usuario": db_usuario.nickname,
        "tipo_conta": db_usuario.tipo_conta
    }


@app.post("/auth/validar-token")
def validar_token():

    return {
        "status": "ok"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(billing.router)


@app.get("/")
def health_check():

    return {
        "status": "online"
    }
