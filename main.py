import time
import capsolver
from seleniumbase import Driver
from src.proxy import Proxy
import threading
import ngrok

# --- CHAVES DE API ---
# Passar para um arquivo .env posteriormente
CAPSOLVER_API_KEY = "CAP-D38F9278056E5453E567FB2115F9D2FF89C61B09C5F64FDBE74D1B76D2A81521"
NGROK_KEY = '33cXA5fJv78EF8LLikmVuezl0rE_7Zi16aFZhszhdxG4zwbx2'

# --- Configurações do scrapper
GGMAX_SITE_KEY = "0x4AAAAAAADnPIDROrmt1Wwj" 
PAGE_URL = "https://ggmax.com.br"

# --- Configurações do proxy
PROXY_USER = 'usuario'
PROXY_PASS = 'senha'
PROXY_IP = '127.0.0.1'
PROXY_PORT = 5001

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
    "websiteURL": "https://ggmax.com.br",
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