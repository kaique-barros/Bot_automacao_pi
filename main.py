import ngrok
import threading
import capsolver
from src.proxy import Proxy
from src.buyProcess import BuyProccesss
from src.Login import Login_process
from seleniumbase import Driver
from src.efi_bank.pagamento import EfiPagamento

# -----------------------------------------------------------------------------------------------------
# ------------------- CONFIGURAÇÔES -------------------------------------------------------------------
# --- Chaves de API
CAPSOLVER_API_KEY = "CAP-C94A0A65FBA75A043865A88CCECBA228DC0C9E6A73EB20F0EB81A42D0627A95A"
NGROK_KEY =         '33yZX8AEwoIrDQToGVY7lO4YXlS_2L2Q7Q9oFBC91DDb5mAMb'

# --- Configurações do scrapper
GGMAX_SITE_KEY =    '0x4AAAAAAADnPIDROrmt1Wwj' # <- Mantenha esse valor 
PAGE_URL =          'https://ggmax.com.br/anuncio/pacotes-no-cod-warzone-e-bo6-entrega-automatica'

# --- Configurações do proxy
PROXY_USER =        '98d5e8f4b835e0968ce439df645264ba3dbea6d17f374a5afe83846be09fdb4c'
PROXY_PASS =        'b4604382119649c7f6fdb81bb4071204ccebded8a31cc0f555605d5ce14a8bed'
PROXY_IP =          '127.0.0.1'
PROXY_PORT =        5001

# --- Configurações do login
USUARIO =           "kaique.barros@pijunior.com.br"
SENHA =             "Abc12345!"

# --- Configurações do processo de compra
NOME =              "Felipe Neymar"
PRICE =             "2,00"
NUM_COMPRAS =       3
WAIT =              10

# --- Configurações do EfiBank 
CERTIFICADO =       'Caminho/para/seu/certificado.pem'
CLIENT_ID =         'Client_Id_de_Producao_COPIADO_DAQUI'
CLIENT_SECRET =     'Client_Secret_de_Producao_COPIADO_DAQUI'
CHAVE_PIX =         'a8c2d1e4-f3g6-4h7i-j8k9-l0m1n2o3p4q5' # Exemplo de chave aleatória

# ----------------------------------------------------------------------------------------------------



login_process = Login_process(USUARIO, SENHA)

PRICE = "R$ " + PRICE 
buy_process = BuyProccesss(NOME, WAIT, PRICE)
# Inicia o proxy
proxy = Proxy(PROXY_USER, PROXY_PASS, PROXY_IP, PROXY_PORT)
proxy_thread = threading.Thread(target=proxy.start_proxy, daemon=True)
proxy_thread.start()
print("[*] Proxy iniciado.")

try: 
  # Abre o tunel no ngrok
  ngrok.set_auth_token(NGROK_KEY)
  listener = ngrok.forward(PROXY_PORT, 'tcp')
  ngrok_port = listener.url().split(":")[2]
  print("[*] Tunel ngrok aberto.")

  PROXY_CONNECTION = f'socks5://{PROXY_USER}:{PROXY_PASS}@0.tcp.sa.ngrok.io:{ngrok_port}'

  # Solicita a resolução o captcha
  print("[*] Solicitando resolução do captcha.")
  capsolver.api_key = CAPSOLVER_API_KEY
  solution = capsolver.solve({
    "type": "AntiCloudflareTask",
    "websiteURL": PAGE_URL,
    "proxy": PROXY_CONNECTION,
    "timeout": 300
  })
  print(f'[*] Solução do captcha recebida: {solution['token'][:10]}')

  with Driver(browser='chrome', uc=True, agent=solution['userAgent'], headless=False, port=9222) as driver:
    driver.open(PAGE_URL)
    print("[*] Pagina aberta")
    
    print("[*] Setando os cookies")
    for cookie_name in solution['cookies']:
      cookie = {
        'name': cookie_name,
        'value': solution['cookies'][cookie_name],
        'domain': '.ggmax.com.br'
      }
      driver.add_cookie(cookie)
      print(f"[*] Cookie {cookie_name} adicionado.")

    print("[*] Recarregando a página.")
    driver.refresh()
    
    print("[*] Iniciando o processo de login.")
    login_process.login()
    
    print("[*] Iniciando o processo de compra.")
    for i in range(NUM_COMPRAS):
      print(f"[*] Iniciando a compra {i+1} de {NUM_COMPRAS}.")
      buy_process.buy()
      driver.open(PAGE_URL)
      
    # print("[*] Iniciando o pagamento via EfiBank.")
    # for pix in buy_process.pix_codes:
    #   print(f"[*] Código Pix da compra {buy_process.pix_codes.index(pix)+1}: {pix[:180]}...")
    #   efi_instance = EfiPagamento(CERTIFICADO, NGROK_KEY, CLIENT_ID, CLIENT_SECRET, CHAVE_PIX, PROXY_PORT)
    #   efi_instance.pagar_qrCode(pix)
    
except KeyboardInterrupt:
  print("Execução encerrada.")