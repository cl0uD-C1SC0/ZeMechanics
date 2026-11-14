import smtplib
from email.mime.text import MIMEText
import os


def enviar_email_aprovacao(orcamento):

    SMTP_SERVER = str(os.getenv('MAIL_SERVER_ADDRESS'))
    BILLING_URL = os.getenv('BILLING_PUBLIC_URL', 'http://localhost:8002')

    msg = MIMEText(f"""
        Olá {orcamento.cliente_nome}!

        O orçamento da sua OS #{orcamento.os_id} está aguardando sua aprovação.
        Valor total: R$ {orcamento.valor_total:.2f}

        Acesse o link para aprovar:
        {BILLING_URL}/api/v1/orcamento/{orcamento.os_id}/aprovar?cliente_cpf={orcamento.cliente_cpf}

    """)

    msg["Subject"] = f"OS #{orcamento.os_id} — Aguardando sua aprovação"
    msg["From"] = "oficina@zemechanics.com"
    msg["To"] = f"{orcamento.cliente_email}"

    try:
        with smtplib.SMTP(SMTP_SERVER, 1025) as server:
            server.sendmail(msg["From"], msg["To"], msg.as_string())

    except Exception as e:
        print(f"Erro ao enviar email: {e}")
