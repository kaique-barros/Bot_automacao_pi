import time
import capsolver
from seleniumbase import Driver
from src.proxy import start_proxy
import threading
import ngrok

# --- SUAS CONFIGURAÇÕES ---
CAPSOLVER_API_KEY = "CAP-D38F9278056E5453E567FB2115F9D2FF89C61B09C5F64FDBE74D1B76D2A81521"
GGMAX_SITE_KEY = "0x4AAAAAAADnPIDROrmt1Wwj" 
PAGE_URL = "https://ggmax.com.br"
MAX_TRIES = 5

proxy_thread = threading.Thread(target=start_proxy, daemon=True)
proxy_thread.start()
print("Proxy iniciado.")

ngrok.set_auth_token('33cXA5fJv78EF8LLikmVuezl0rE_7Zi16aFZhszhdxG4zwbx2')

listener = ngrok.forward(
                5001,
                'tcp'
            )

ngrok_port = listener.url().split(":")[2]

PROXY_CONNECTION = f'socks5://usuario:senha123@0.tcp.sa.ngrok.io:{ngrok_port}'

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