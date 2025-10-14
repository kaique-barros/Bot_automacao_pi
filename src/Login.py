import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

WAIT = 10

class Login_process:
    def __init__(self, usuario, senha):
        self.USUARIO = usuario
        self.SENHA = senha
    
    def login(self):
        """Acessa site GGmax já aberto no Chrome"""
        options = webdriver.ChromeOptions()
        options.debugger_address = "127.0.0.1:9222"  # porta padrao do --remote-debugging
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, WAIT)

        try:
            menu_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon-menu-03")))
            menu_icon.click()
            print("Menu aberto.")
        except Exception as e:
                print("Erro ao abrir menu:", e)
            
        try:
            entrar_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='account__popover']//a[contains(text(), 'Entrar')]")))
            entrar_link.click()
            print("Cliquei no botão 'Entrar'.")
        except Exception as e:
                print("Erro ao clicar no botão de entrar:", e)
            
        try:
            campo_email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Usuário ou e-mail']")))
            campo_email.send_keys(self.USUARIO)
            print("E-mail preenchido.")
            campo_senha = driver.find_element(By.CSS_SELECTOR, "[name='password']")
            campo_senha.send_keys(self.SENHA)
            print("Senha preenchida.")
        except Exception as e:
                print("Erro ao preencher dados do usuário:", e)
            
        try:
            botao_entrar_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//form[contains(@class, 'ggmax-login-form')]//button[contains(text(), 'Entrar')]")))
            botao_entrar_login.click()
            print("Cliquei no botão final de login.")
        except Exception as e:
                print("Erro ao clicar no botão de finalizar login:", e)

        try:
            print("Aguardando confirmação de e-mail...")
            wait_confirm = WebDriverWait(driver, 120)  # espera até 2 minutos enquanto confirma o e-mail
            wait_confirm.until(EC.presence_of_element_located((By.CSS, " "))) # ADICIONAR SELETOR AQUI!!!! EX.: ICONE DAS NOTIFICAÇÕES
            print("Login realizado com sucesso!")
        except TimeoutException:
            print("Tempo de espera pela confirmação do login esgotado.")
        except Exception as e:
            print(f"Ocorreu um erro durante o processo de login, Detalhes: {e}")

        finally:
            pass