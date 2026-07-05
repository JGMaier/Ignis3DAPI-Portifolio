"""
Versão demonstrativa do módulo de faturamento do Ignis3D.
Responsável pelo fluxo de assinatura, integração com gateway de pagamentos,
processamento de webhooks, ativação de licenças e confirmação da compra.
Informações sensíveis e regras proprietárias foram removidas.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    usuario_id: int
    plano: str


PLANOS = {
    "mensal": "price_demo_monthly",
    "anual": "price_demo_yearly",
}


@router.post("/checkout/licenca")
def criar_checkout(req: CheckoutRequest):

    if req.plano not in PLANOS:
        raise HTTPException(status_code=400, detail="Plano inválido")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price": PLANOS[req.plano],
                "quantity": 1,
            }
        ],
        metadata={
            "usuario_id": str(req.usuario_id),
            "plano": req.plano,
        },
        success_url="https://example.com/checkout/success",
        cancel_url="https://example.com/checkout/cancel",
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook():

    evento = {
        "tipo": "checkout.session.completed",
        "usuario_id": 1,
        "plano": "mensal",
        "subscription_id": "sub_demo"
    }

    if evento["tipo"] != "checkout.session.completed":
        return {"status": "ignored"}

    licenca = {
        "usuario": evento["usuario_id"],
        "plano": evento["plano"],
        "status": "ativo",
        "subscription": evento["subscription_id"],
    }

    enviar_email_confirmacao(
        "usuario@email.com",
        licenca["plano"]
    )

    return {
        "status": "success",
        "licenca": licenca
    }


def enviar_email_confirmacao(email_destino, plano):

    assunto = "Compra confirmada"

    mensagem = f"""
    Sua assinatura foi ativada com sucesso.

    Plano:
    {plano.capitalize()}

    Obrigado por utilizar o Ignis3D.
    """

    print(f"Enviando e-mail para {email_destino}")
    print(assunto)
    print(mensagem)


@router.get("/checkout/success")
def checkout_success():

    return {
        "status": "success",
        "message": "Pagamento concluído com sucesso."
    }


@router.get("/checkout/cancel")
def checkout_cancel():

    return {
        "status": "cancelled",
        "message": "Pagamento cancelado."
    }
