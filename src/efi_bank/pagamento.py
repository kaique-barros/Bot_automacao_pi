from pprint import pprint
from efipay import EfiPay
import ngrok
import threading
from .webhook import iniciar_webhook

class EfiPagamento:
    def __init__(self, certificado, ngrok_key, client_id, client_secret, chave, webhook_port):
        ngrok.set_auth_token(ngrok_key)
        listener = ngrok.forward(webhook_port, 'http')
        threading.Thread(target=iniciar_webhook, daemon=True, args=[webhook_port]).start()
        
        self.webhook_url = listener.url()

        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            'sandbox': False,
            'certificate': certificado
        }

        self.efi = EfiPay(credentials)
        self.chave = chave
        self.configurar_webhook()

    def configurar_webhook(self):
        headers = {
            'x-skip-mtls-checking': 'true'
        }

        params = {
            'chave': self.chave
        }

        body = {
            'webhookUrl': self.webhook_url
        }

        response =  self.efi.pix_config_webhook(params=params, body=body, headers=headers)
        print(response)
        
    def pagar_qrCode(self, chave):
        params = {
            'idEnvio': 1
        }

        body = {
        "pagador": {
            "chave": self.chave,
            "infoPagador": "Pagamento de QR Code via API Pix"
        },
        "pixCopiaECola": chave
        }

        response =  self.efi.pix_qrcode_pay(params=params, body=body)
        if response['status'] == 'EM_PROCESSAMENTO':
            print(f"[*] Pagamento no valor de {response['valor']} realizado.")
                
                
efi_instance = EfiPagamento('', '', '', '', '', 5001)
efi_instance.pagar_qrCode("00020126330014br.gov.bcb.pix01114377307681952040000530398654040.015802BR5919Kaique Barros Silva6009Sao Paulo62290525REC68F265B8EF74466433135263049C38")