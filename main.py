import time
import capsolver
from seleniumbase import Driver
from src.proxy import Proxy
import threading
import ngrok
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# -----------------------------------------------------------------------------------------------------
# ------------------- CONFIGURAÇÔES -------------------------------------------------------------------
# --- Chaves de API
CAPSOLVER_API_KEY = 'CAP-ED5DF302811B699CA76FC80712D56EF5044F6B693FFF7E5E53DCD377F7CF28B0'
NGROK_KEY = '33nepndDespFrKvWB8LueTLZVbj_7pMXHYADta3Vy2Q5JHeTM'

# --- Configurações do scrapper
GGMAX_SITE_KEY = "0x4AAAAAAADnPIDROrmt1Wwj" 
PAGE_URL = "https://ggmax.com.br/anuncio/venda-de-brinrots-raros-no-roblox-entrega-rapida-e-segura"

# --- Configurações do proxy
PROXY_USER = '98d5e8f4b835e0968ce439df645264ba3dbea6d17f374a5afe83846be09fdb4c'
PROXY_PASS = 'b4604382119649c7f6fdb81bb4071204ccebded8a31cc0f555605d5ce14a8bed'
PROXY_IP = '127.0.0.1'
PROXY_PORT = 5001
# -----------------------------------------------------------------------------------------------------

# Inicia o proxy
proxy = Proxy(PROXY_USER, PROXY_PASS, PROXY_IP, PROXY_PORT)
proxy_thread = threading.Thread(target=proxy.start_proxy, daemon=True)
proxy_thread.start()
print("Proxy iniciado.")

try: 
  # Abre o tunel no ngrok
  ngrok.set_auth_token(NGROK_KEY)
  listener = ngrok.forward(PROXY_PORT, 'tcp')
  ngrok_port = listener.url().split(":")[2]

  PROXY_CONNECTION = f'socks5://{PROXY_USER}:{PROXY_PASS}@0.tcp.sa.ngrok.io:{ngrok_port}'

  # Solicita a resolução o captcha
  print("Solicitando resolução do captcha.")
  capsolver.api_key = CAPSOLVER_API_KEY
  solution = capsolver.solve({
    "type": "AntiCloudflareTask",
    "websiteURL": PAGE_URL,
    "proxy": PROXY_CONNECTION
  })
  print(f'Solução do captcha recebida: {solution['token'][:10]}')

  with Driver(browser='chrome', uc=True, agent=solution['userAgent'], headless=False) as driver:
    driver.open(PAGE_URL)
    print("Pagina aberta")
    
    print("Setando os cookies")
    for cookie_name in solution['cookies']:
      cookie = {
        'name': cookie_name,
        'value': solution['cookies'][cookie_name],
        'domain': '.ggmax.com.br'
      }
      driver.add_cookie(cookie)
      print(f"Cookie {cookie_name} adicionado.")

    driver.refresh()
    
    time.sleep(20)
except KeyboardInterrupt:
  print("Execução encerrada.")