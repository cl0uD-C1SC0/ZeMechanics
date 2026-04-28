import smtplib
from email.mime.text import MIMEText

def enviar_email_aprovacao(os):
    msg = MIMEText(f"""
        Olá {os.cliente.nome}!
        
        Sua OS #{os.id} está aguardando sua aprovação.
        
        Acesse o link para aprovar:
        http://localhost:8000/api/v1/ordem_servico/aprovar/{os.id}?cliente_cpf={os.cliente.cpf}
        
    """)
    
    msg["Subject"] = f"OS #{os.id} — Aguardando sua aprovação"
    msg["From"]    = "oficina@zemechanics.com"
    msg["To"]      = "teste_cliente@mail.com"

    with smtplib.SMTP("localhost", 1025) as server: 
        server.sendmail(msg["From"], msg["To"], msg.as_string())