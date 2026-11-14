from unittest.mock import patch, Mock
from email import message_from_string
from email.header import decode_header

from app.services.EmailService import enviar_email_aprovacao


def _orcamento(os_id=10, nome="José", email="jose@email.com", cpf="123"):
    return Mock(os_id=os_id, cliente_nome=nome, cliente_email=email, cliente_cpf=cpf, valor_total=211.8)


def _ler_email(mock_smtp):
    raw_message = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0][2]
    email_msg = message_from_string(raw_message)
    subject, encoding = decode_header(email_msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")
    return email_msg, subject


@patch("app.services.EmailService.smtplib.SMTP")
def test_enviar_email_aprovacao_sucesso(mock_smtp):
    enviar_email_aprovacao(_orcamento())

    email_msg, subject = _ler_email(mock_smtp)
    body = email_msg.get_payload(decode=True).decode()

    assert "OS #10" in subject
    assert email_msg["From"] == "oficina@zemechanics.com"
    assert email_msg["To"] == "jose@email.com"
    assert "José" in body
    assert "R$ 211.80" in body
    assert "http://localhost:8002/api/v1/orcamento/10/aprovar?cliente_cpf=123" in body


@patch.dict("os.environ", {"BILLING_PUBLIC_URL": "https://api.zemechanics.com/billing"})
@patch("app.services.EmailService.smtplib.SMTP")
def test_enviar_email_usa_url_publica_configurada(mock_smtp):
    enviar_email_aprovacao(_orcamento(os_id=5, nome="Ana", email="ana@email.com", cpf="999"))

    email_msg, subject = _ler_email(mock_smtp)
    body = email_msg.get_payload(decode=True).decode()

    assert "OS #5" in subject
    assert email_msg["To"] == "ana@email.com"
    assert "https://api.zemechanics.com/billing/api/v1/orcamento/5/aprovar?cliente_cpf=999" in body


@patch("app.services.EmailService.smtplib.SMTP")
def test_enviar_email_erro_smtp(mock_smtp):
    mock_smtp.side_effect = Exception("Erro SMTP")

    enviar_email_aprovacao(_orcamento(os_id=1))

    mock_smtp.assert_called_once()
