import time
import ngrok
import requests
import threading
import capsolver
from src.proxy import Proxy
from src.buyProcess import BuyProccesss
from src.Login import Login_process
from seleniumbase import Driver

# -----------------------------------------------------------------------------------------------------
# ------------------- CONFIGURAÇÔES -------------------------------------------------------------------
# --- Chaves de API
CAPSOLVER_API_KEY = 'CAP-ED5DF302811B699CA76FC80712D56EF5044F6B693FFF7E5E53DCD377F7CF28B0'
NGROK_KEY =         '33yZX8AEwoIrDQToGVY7lO4YXlS_2L2Q7Q9oFBC91DDb5mAMb'

# --- Configurações do scrapper
GGMAX_SITE_KEY =    '0x4AAAAAAADnPIDROrmt1Wwj' 
PAGE_URL =          'https://ggmax.com.br/anuncio/venda-de-brinrots-raros-no-roblox-entrega-rapida-e-segura'

# --- Configurações do proxy
PROXY_USER =        '98d5e8f4b835e0968ce439df645264ba3dbea6d17f374a5afe83846be09fdb4c'
PROXY_PASS =        'b4604382119649c7f6fdb81bb4071204ccebded8a31cc0f555605d5ce14a8bed'
PROXY_IP =          '127.0.0.1'
PROXY_PORT =        5001

# --- Configurações do login
USUARIO = "kaique.barros@pijunior.com.br"
SENHA = "Abc12345!"
login_process = Login_process(USUARIO, SENHA)

# --- Configurações do processo de compra
NOME = "Marcos Camargo Oliveira Bakker da Silva"
WAIT = 10
PRICE = "R$ " + "2,00"
buy_process = BuyProccesss(NOME, WAIT, PRICE)
NUM_PURCHASES = 1

# --- Configurações do EfiBank 
PIX_KEY = ""
INFO = "Pagamento de QR Code via API Pix"
# -----------------------------------------------------------------------------------------------------

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
    "proxy": PROXY_CONNECTION
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
    
    time.sleep(30)
    
    # print("[*] Iniciando o processo de compra.")
    # for i in range(NUM_PURCHASES):
    #   print(f"[*] Iniciando a compra {i+1} de {NUM_PURCHASES}.")
    #   buy_process.buy()
    #   driver.open(PAGE_URL)
    
    
except KeyboardInterrupt:
  print("Execução encerrada.")